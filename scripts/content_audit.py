#!/usr/bin/env python3
"""跨境财税合规类公众号文稿内容审计器。

和平台 HTML 校验（validate_gzh_html.py）分工不同：那个管"能不能粘贴"，
这个管"能不能发"。合规类内容的返工点不在样式，在倒计时过期、文号缺失、
金额无出处、AI 体句式、CTA 重复这五类。

用法:
    content_audit.py <file.md|file.html> [--pubdate YYYY-MM-DD] [--layer 入口|转化|沉淀]

退出码: 1 = 有 ERROR; 0 = 通过（可能有 WARNING）。
"""

import argparse
import datetime as dt
import re
import sys

# ── 易错法规名称表 ──────────────────────────────────────────────
# key = 常见错误写法, value = 正确名称
REGULATION_NAMES = {
    "对外投资管理条例": "《国务院关于对外投资的规定》（国务院令第 837 号）",
    "境外投资管理条例": "《国务院关于对外投资的规定》（国务院令第 837 号）",
}

# 需要全称加文号的简称
NEEDS_FULL_CITE = [
    (re.compile(r"(?<![0-9])(\d{1,3})\s*号公告"), "号公告"),
    (re.compile(r"(?<![0-9])(\d{1,3})\s*号文"), "号文"),
    (re.compile(r"(?<![0-9])(\d{2,4})\s*号令"), "号令"),
]

# 判定"已给出全称"的特征：出现书名号且同段落内有编号，或出现"公告""通知""规定""条例""办法"等文种
FULL_CITE_HINT = re.compile(r"《[^》]{6,}》")

# ── AI 体禁用句式 ──────────────────────────────────────────────
AI_PATTERNS = [
    (re.compile(r"(变|动|卡|改)的是[^，。；]{0,12}[，。]"), "「X 的是……」归纳句式"),
    (re.compile(r"真正(要看|该看|重要)的是"), "「真正要看的是」归纳句式"),
    (re.compile(r"(这|那)(几|三|两|四)件事(都)?指向同一个方向"), "归拢式收尾"),
    (re.compile(r"说到底(就)?是一件事"), "归拢式收尾"),
    (re.compile(r"归根结底"), "归拢式收尾"),
    (re.compile(r"这里有个(关键点|容易搞混的地方)"), "空转过渡词"),
    (re.compile(r"值得注意的是"), "空转过渡词"),
    (re.compile(r"需要指出的是"), "空转过渡词"),
    (re.compile(r"但换个角度看"), "空转过渡词"),
    (re.compile(r"[0-9]{1,3}\s*号(文|令|公告)(自己|本身)?(写|定)的规矩"), "法规拟人化"),
    (re.compile(r"(这份|该)文件(想说的是|告诉你)"), "法规拟人化"),
    (re.compile(r"监管(在|正在)告诉(你|我们)"), "法规拟人化"),
    (re.compile(r"不是[^，。]{2,10}，不是[^，。]{2,10}，而是"), "连用排比三段论"),
]

# ── 金额与来源 ──────────────────────────────────────────────
AMOUNT = re.compile(r"[0-9]+(?:\.[0-9]+)?\s*(?:万元|亿元|万美元|亿美元|万港元|亿港元|万|亿)")
SOURCE_HINT = re.compile(
    r"外汇局|税务局|税务总局|财政部|发改委|商务部|海关|证监会|金管局|注册处|"
    r"新华社|财新|第一财经|中国税务报|人民日报|央视|21 ?世纪|证券时报|虎嗅|"
    r"律师事务所|律所|会计师事务所|公告|通函|决定书|答记者问|\[L[1-4]\]"
)

# ── 倒计时 ──────────────────────────────────────────────
DEADLINE_COMMENT = re.compile(r"<!--\s*deadline:(\d{4}-\d{2}-\d{2})\s*-->")
COUNTDOWN_TEXT = re.compile(r"还(?:剩|有)\s*(\d{1,4})\s*天")
DATE_IN_TEXT = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")

# ── CTA ──────────────────────────────────────────────
CTA = re.compile(r"欢迎加入星球聊一聊")

# ── 标点 ──────────────────────────────────────────────
HALF_PUNCT = re.compile(r"[\u4e00-\u9fff][,;!?]")
ASCII_QUOTE = re.compile(r'[\u4e00-\u9fff]["\']|["\'][\u4e00-\u9fff]')
CODE_BLOCK = re.compile(r"```.*?```|`[^`]+`", re.S)
MARKER_BANG = re.compile(r"!!")


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
    return CODE_BLOCK.sub(" ", text)


def check_countdown(text, pubdate, r):
    declared = DEADLINE_COMMENT.findall(text)
    stated = COUNTDOWN_TEXT.findall(text)

    if not stated:
        return

    if not pubdate:
        r.warn("CD-02", f"正文出现倒计时「还剩 {stated[0]} 天」，但未提供 --pubdate，无法核验")
        return

    # 优先用 deadline 注释；没有就从正文里找最近的一个日期
    target = None
    if declared:
        target = dt.date.fromisoformat(declared[0])
    else:
        m = DATE_IN_TEXT.search(text)
        if m:
            target = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            r.warn("CD-03", "倒计时组件缺少 <!-- deadline:YYYY-MM-DD --> 注释，已按正文首个日期推算")

    if not target:
        r.err("CD-04", "出现倒计时但找不到可比对的截止日")
        return

    real = (target - pubdate).days
    for bad in sorted({int(x) for x in stated if int(x) != real}):
        r.err(
            "CD-01",
            f"倒计时不一致：正文写「还剩 {bad} 天」，按发布日 {pubdate} 到 {target} 实际为 {real} 天",
        )


def check_citations(text, r):
    """逐个简称核查：该编号首次出现处的前后 120 字内要有《…》全称。"""
    seen = set()
    for pat, kind in NEEDS_FULL_CITE:
        for m in pat.finditer(text):
            key = (m.group(1), kind)
            if key in seen:
                continue
            seen.add(key)
            window = text[max(0, m.start() - 120): m.end() + 120]
            if not FULL_CITE_HINT.search(window):
                r.err(
                    "CT-01",
                    f"「{m.group(1)}{kind}」首次出现处附近无《…》全称，需写全称加文号",
                )


def check_regulation_names(text, r):
    for wrong, right in REGULATION_NAMES.items():
        if wrong in text:
            r.err("RG-01", f"法规名称有误：「{wrong}」应为 {right}")


def check_amounts(text, r):
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    for i, p in enumerate(paras):
        if not AMOUNT.search(p):
            continue
        window = " ".join(paras[max(0, i - 1): i + 2])
        if not SOURCE_HINT.search(window):
            sample = AMOUNT.search(p).group(0)
            r.warn("AM-01", f"金额「{sample}」所在段落前后未见来源标识，请确认出处")


def check_ai_style(text, r):
    for pat, label in AI_PATTERNS:
        m = pat.search(text)
        if m:
            r.err("AI-01", f"命中 AI 体：{label} —— 「{m.group(0)[:24]}」")


def check_cta(text, layer, r):
    n = len(CTA.findall(text))
    if n == 0 and layer in ("转化", "沉淀"):
        r.err("CTA-01", f"{layer}层文章缺少星球 CTA")
    elif n > 1:
        r.err("CTA-02", f"星球 CTA 出现 {n} 次，应有且仅有一次")
    elif n >= 1 and layer == "入口":
        r.warn("CTA-03", "入口层文章出现星球 CTA，建议改为指向次日文章")


def strip_markers(text):
    """去掉 !!...!! 标记的定界符本身。

    标记语法里的 !!对照!! / !!回指!! 会让「照!」「指!」被误判成中文后半角标点，
    这是检查器自己的产物，不是正文问题。只去掉定界符，标记内容照常参与其他检查。
    """
    return MARKER_BANG.sub("  ", text)


def check_punct(text, r):
    text = strip_markers(text)
    for m in HALF_PUNCT.finditer(text):
        r.warn("PU-01", f"中文后半角标点：「{m.group(0)}」")
        break
    for m in ASCII_QUOTE.finditer(text):
        r.warn("PU-02", f"中文语境出现直引号：「{m.group(0)}」")
        break


def check_backref(text, layer, r):
    if layer != "转化":
        return
    if not re.search(r"\d{1,2}\s*月\s*\d{1,2}\s*日那篇", text):
        r.warn("BR-01", "转化层文章未见回指历史文章，账号延续性靠这个撑")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--pubdate", help="发布日 YYYY-MM-DD")
    ap.add_argument("--layer", choices=["入口", "转化", "沉淀"], help="文章层级")
    a = ap.parse_args()

    raw = open(a.path, encoding="utf-8").read()
    text = strip_code(raw)
    pub = dt.date.fromisoformat(a.pubdate) if a.pubdate else None

    r = Report()
    print(f"\n审计 {a.path}")
    print(f"发布日 {a.pubdate or '未指定'} · 层级 {a.layer or '未指定'}\n")

    check_countdown(raw, pub, r)
    check_citations(text, r)
    check_regulation_names(text, r)
    check_amounts(text, r)
    check_ai_style(text, r)
    check_punct(text, r)
    if a.layer:
        check_cta(text, a.layer, r)
        check_backref(text, a.layer, r)
    else:
        r.warn("LY-01", "未指定 --layer，跳过 CTA 与回指检查")

    sys.exit(r.dump())


if __name__ == "__main__":
    main()
