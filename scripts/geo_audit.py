#!/usr/bin/env python3
"""合规类公众号文稿的 GEO 体检器。

和 content_audit.py 分工不同：那个管"这篇能不能发"（倒计时、文号、金额、AI 体、CTA），
这个管"发出去之后 AI 找不找得到"——有没有一句能被整句摘走的答案句、绑了哪条问句、
数据密度够不够、有没有外部权威引用、有没有 FAQ、多久没更新。

GEO 元数据一律走 HTML 注释，与 <!-- deadline:... --> 同一机制，不新增渲染组件：
    <!-- geo:answer 三个环节各 20%：装入、存续、终止清算 -->
    <!-- geo:prompts Q004,Q008 -->
    <!-- geo:updated 2026-09-22 -->

用法:
    geo_audit.py <file.md> [--prompts path/to/prompts.yaml] [--today YYYY-MM-DD]

退出码: 1 = 有 ERROR; 0 = 通过（可能有 WARNING）。
"""

import argparse
import datetime as dt
import pathlib
import re
import sys

# ── GEO 元数据 ──────────────────────────────────────────────
GEO_ANSWER = re.compile(r"<!--\s*geo:answer\s+(.+?)\s*-->", re.S)
GEO_PROMPTS = re.compile(r"<!--\s*geo:prompts\s+([^>]+?)\s*-->")
GEO_UPDATED = re.compile(r"<!--\s*geo:updated\s+(\d{4}-\d{2}-\d{2})\s*-->")
PROMPT_ID = re.compile(r"\bQ\d{2,4}\b")

# ── 阈值（与 config/geo.yaml 的 audit 段保持一致）──────────────
ANSWER_MAX_CHARS = 60
ANSWER_WITHIN_CHARS = 300
CLAIM_EVERY_WORDS = 150
MIN_CITATIONS = 3
MIN_FAQ_PAIRS = 2
REFRESH_DAYS = 90
PROMPTS_MIN, PROMPTS_MAX = 1, 3

# ── 可验证声明：数字、金额、日期、文号、百分比 ─────────────────
CLAIM = re.compile(
    r"[0-9]+(?:\.[0-9]+)?\s*(?:%|％|万元|亿元|万美元|亿美元|万港元|亿港元|万|亿|天|年|个月)|"
    r"\d{4}\s*年\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?|"
    r"[0-9]{1,3}\s*号(?:公告|文|令)"
)

# ── 外部权威引用 ──────────────────────────────────────────────
CITATION_HINT = re.compile(
    r"财政部|税务总局|国务院|发改委|商务部|外汇局|海关总署|证监会|"
    r"香港税务局|香港公司注册处|金管局|"
    r"答记者问|官方案例|处罚决定书|公告|通函|\[L[1-2]\]"
)

# ── FAQ ──────────────────────────────────────────────
FAQ_HEADING = re.compile(r"^#{2,4}\s*(常见问题|FAQ|问答)\s*$", re.M | re.I)

CODE_BLOCK = re.compile(r"```.*?```|`[^`]+`", re.S)
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


class Report:
    def __init__(self):
        self.errors = []
        self.warns = []

    def err(self, code, msg):
        self.errors.append((code, msg))

    def warn(self, code, msg):
        self.warns.append((code, msg))

    def dump(self):
        for c, m in self.errors:
            print(f"  ERROR  [{c}] {m}")
        for c, m in self.warns:
            print(f"  WARN   [{c}] {m}")
        print()
        print(f"  合计 {len(self.errors)} 个 ERROR，{len(self.warns)} 个 WARNING")
        return 1 if self.errors else 0


def strip_code(text):
    """去掉 frontmatter 与代码块——那里的数字不算可验证声明，注释也不是正文。"""
    text = FRONTMATTER.sub("", text)
    return CODE_BLOCK.sub(" ", text)


def body_after_meta(raw):
    """去掉 GEO 注释后的正文，用于计算答案句位置与字数。"""
    return re.sub(r"<!--.*?-->", "", raw, flags=re.S)


def check_answer(raw, r):
    m = GEO_ANSWER.search(raw)
    if not m:
        r.err("GA-01", "缺少答案句。补 <!-- geo:answer 一句 ≤60 字的判断 -->")
        return
    answer = re.sub(r"\s+", " ", m.group(1)).strip()
    if len(answer) > ANSWER_MAX_CHARS:
        r.err(
            "GA-02",
            f"答案句 {len(answer)} 字，超过 {ANSWER_MAX_CHARS} 字上限；拆成两句，一句一个判断",
        )
    pos = body_after_meta(raw).find(answer)
    if pos < 0:
        r.warn("GA-03", "答案句未出现在正文中，请把同一句判断写进正文首段")
    elif pos > ANSWER_WITHIN_CHARS:
        r.err(
            "GA-03",
            f"答案句出现在第 {pos} 字，应落在前 {ANSWER_WITHIN_CHARS} 字内",
        )


def check_prompts(raw, known_ids, r):
    m = GEO_PROMPTS.search(raw)
    if not m:
        r.err("GA-04", "未绑定目标问句。补 <!-- geo:prompts Q004,Q008 -->，每篇 1–3 条")
        return
    ids = PROMPT_ID.findall(m.group(1))
    if not ids:
        r.err("GA-04", "geo:prompts 注释里没有识别到 Q 开头的问句 ID")
        return
    if len(ids) > PROMPTS_MAX:
        r.err("GA-04", f"绑定了 {len(ids)} 条问句，超过上限 {PROMPTS_MAX} 条")
    if known_ids is not None:
        for i in ids:
            if i not in known_ids:
                r.err("GA-05", f"问句 {i} 不在 prompts.yaml 中，检查拼写或先入库")


def check_density(text, r):
    n = len([c for c in text if not c.isspace()])
    claims = len(CLAIM.findall(text))
    need = max(1, n // CLAIM_EVERY_WORDS)
    if claims < need:
        r.warn(
            "GD-01",
            f"可验证声明 {claims} 个，正文约 {n} 字，按每 {CLAIM_EVERY_WORDS} 字一个应有 {need} 个",
        )


def check_citations(text, r):
    found = {m.group(0) for m in CITATION_HINT.finditer(text)}
    if len(found) < MIN_CITATIONS:
        r.warn(
            "GR-01",
            f"外部权威引用 {len(found)} 处（{('、'.join(sorted(found)) or '无')}），建议不少于 {MIN_CITATIONS} 处",
        )


def check_faq(text, r):
    m = FAQ_HEADING.search(text)
    if not m:
        r.err("GF-01", "末尾没有「## 常见问题」章节；FAQ 是最容易被 AI 提取的形态")
        return
    tail = text[m.end():]
    pairs = len(re.findall(r"^\s*(?:\*\*)?问[：:]", tail, re.M))
    if pairs < MIN_FAQ_PAIRS:
        r.err("GF-01", f"FAQ 只有 {pairs} 组问答，至少 {MIN_FAQ_PAIRS} 组")


def check_updated(raw, today, r):
    m = GEO_UPDATED.search(raw)
    if not m:
        r.warn("GU-01", "缺少 <!-- geo:updated YYYY-MM-DD -->，季度更新时无法判断时效")
        return
    updated = dt.date.fromisoformat(m.group(1))
    days = (today - updated).days
    if days > REFRESH_DAYS:
        r.warn(
            "GU-01",
            f"上次更新距今 {days} 天，超过 {REFRESH_DAYS} 天；未更新的内容失去引用的速度是正常的 3 倍",
        )


def load_prompt_ids(path):
    if not path:
        return None
    p = pathlib.Path(path)
    if not p.exists():
        print(f"  提示：找不到问句库 {p}，跳过 GA-05 校验")
        return None
    return set(PROMPT_ID.findall(p.read_text(encoding="utf-8")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--prompts", help="私有仓库 geo/prompts.yaml 的路径")
    ap.add_argument("--today", help="体检日 YYYY-MM-DD，默认今天")
    a = ap.parse_args()

    raw = open(a.path, encoding="utf-8").read()
    text = strip_code(raw)
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    known = load_prompt_ids(a.prompts)

    r = Report()
    print(f"\nGEO 体检 {a.path}")
    print(f"体检日 {today.isoformat()} · 问句库 {a.prompts or '未提供'}\n")

    check_answer(raw, r)
    check_prompts(raw, known, r)
    check_density(text, r)
    check_citations(text, r)
    check_faq(text, r)
    check_updated(raw, today, r)

    sys.exit(r.dump())


if __name__ == "__main__":
    main()
