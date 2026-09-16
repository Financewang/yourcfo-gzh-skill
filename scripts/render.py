#!/usr/bin/env python3
"""Markdown → 公众号 HTML 渲染器。

按 references/ 里的主题与合规组件库装配，产出可直接粘贴的 <section> 片段。

用法:
    render.py <稿件.md> [--theme navy|amber] [--layer 入口|转化|沉淀] [--pubdate YYYY-MM-DD]

Markdown 扩展语法（本 skill 专用）:
    !!倒计时 2026-10-22!!        → C2 倒计时条
    !!法条 文号 | 原文!!          → C1 条文卡
    !!对号入座!! 之后的 1. 2. 3. → C3 对号入座块
    !!对照!! 情形 | 金额          → C4 金额对照表（连续多行）
    !!回指!! 文字                 → C6 回指卡
    !!更正!! 文字                 → C7 更正声明块
    ## 标题                       → 自动编号章节标题
    **加粗**                      → 主色加粗
    ==关键词==                    → 下划线标记
"""

import argparse
import datetime as dt
import html
import pathlib
import re
import sys

THEMES = {
    "navy": {
        "name": "政策深蓝",
        "PRIMARY": "#1E3A5F",
        "ACCENT": "#C8963E",
        "TINT": "#F4F7FB",
        "UL": "#C9D9EC",
        "GRAD": "#16283F",
    },
    "amber": {
        "name": "倒计时琥珀",
        "PRIMARY": "#B45309",
        "ACCENT": "#1E3A5F",
        "TINT": "#FDF8F0",
        "UL": "#F0D9B0",
        "GRAD": "#8A3F07",
    },
}

BODY = "#3A424E"
SUB = "#5A6472"
LINE = "#E3E8EF"


def esc(s):
    return html.escape(s, quote=False)


def leaf(s, style=""):
    st = f' style="{style}"' if style else ""
    return f'<span leaf=""{st}>{esc(s)}</span>'


def inline(text, T):
    """处理行内标记：**加粗** ==下划线=="""
    text = esc(text)
    text = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: f'</span><strong style="color:{T["ACCENT"]};font-weight:700;">'
                  f'<span leaf="">{m.group(1)}</span></strong><span leaf="">',
        text,
    )
    text = re.sub(
        r"==(.+?)==",
        lambda m: f'</span><span leaf="" style="border-bottom:2px solid {T["UL"]};'
                  f'font-weight:600;">{m.group(1)}</span><span leaf="">',
        text,
    )
    return f'<span leaf="">{text}</span>'


# ── 组件 ──────────────────────────────────────────────

def c_title(t, T):
    return (
        f'<section style="margin:0 0 8px 0;">'
        f'<p style="margin:0;font-size:22px;font-weight:700;line-height:1.5;'
        f'color:{T["PRIMARY"]};">{leaf(t)}</p></section>'
        f'<section style="margin:0 0 28px 0;height:3px;width:44px;'
        f'background:{T["ACCENT"]};border-radius:2px;"></section>'
    )


def c_h2(num, t, T):
    return (
        f'<section style="margin:34px 0 16px 0;">'
        f'<p style="margin:0;font-size:12px;letter-spacing:2px;color:#9AA7B8;'
        f'font-weight:600;">{leaf(num)}</p>'
        f'<p style="margin:4px 0 0 0;font-size:18px;font-weight:600;line-height:1.55;'
        f'color:{T["PRIMARY"]};">{leaf(t)}</p></section>'
    )


def c_p(t, T):
    return (
        f'<p style="margin:0 0 18px 0;font-size:16px;line-height:1.9;color:{BODY};'
        f'text-align:justify;">{inline(t, T)}</p>'
    )


def c_lead(t, T):
    return (
        f'<section style="margin:0 0 26px 0;padding:16px 18px;background:{T["TINT"]};'
        f'border-radius:6px;"><p style="margin:0;font-size:15px;line-height:1.85;'
        f'color:#4A5463;">{inline(t, T)}</p></section>'
    )


def c_quote(t, T):
    return (
        f'<section style="margin:20px 0;padding:0 0 0 14px;border-left:2px solid {T["UL"]};">'
        f'<p style="margin:0;font-size:15px;line-height:1.85;color:{SUB};">'
        f'{inline(t, T)}</p></section>'
    )


def c_law(cite, body, T):
    return (
        f'<section style="margin:24px 0;border-left:3px solid {T["PRIMARY"]};'
        f'background:{T["TINT"]};padding:16px 18px 16px 16px;border-radius:0 6px 6px 0;">'
        f'<p style="margin:0 0 10px 0;font-size:12px;letter-spacing:0.5px;'
        f'color:{T["PRIMARY"]};font-weight:600;">{leaf(cite)}</p>'
        f'<p style="margin:0;font-size:15px;line-height:1.85;color:#2C3542;">'
        f'{leaf(body)}</p></section>'
    )


def c_deadline(date_s, pub, T):
    d = dt.date.fromisoformat(date_s)
    days = (d - pub).days if pub else None
    num_color = "#E05A3C" if (days is not None and days <= 7) else T["ACCENT"]
    txt = f"{d.year} 年 {d.month} 月 {d.day} 日 · 从今天算还剩 "
    tail = " 天" if days is not None else ""
    numhtml = (
        f'<strong style="font-size:26px;color:{num_color};">{leaf(str(days))}</strong>'
        if days is not None else ""
    )
    return (
        f'<!-- deadline:{date_s} -->'
        f'<section style="margin:0 0 26px 0;background:linear-gradient(135deg,'
        f'{T["PRIMARY"]} 0%,{T["GRAD"]} 100%);border-radius:8px;padding:18px 20px;">'
        f'<p style="margin:0 0 6px 0;font-size:12px;letter-spacing:1px;'
        f'color:rgba(255,255,255,0.65);">{leaf("申报截止")}</p>'
        f'<p style="margin:0;font-size:15px;line-height:1.6;color:#FFFFFF;">'
        f'{leaf(txt)}{numhtml}{leaf(tail)}</p></section>'
    )


def c_cases(items, T):
    out = ['<section style="margin:22px 0;">']
    for i, (head, desc) in enumerate(items, 1):
        out.append(
            f'<section style="margin:0 0 16px 0;display:flex;align-items:flex-start;">'
            f'<section style="flex:0 0 26px;height:26px;border-radius:13px;'
            f'background:{T["PRIMARY"]};text-align:center;line-height:26px;'
            f'margin-right:12px;">{leaf(str(i), "font-size:13px;color:#FFFFFF;font-weight:600;")}'
            f'</section><section style="flex:1;">'
            f'<p style="margin:2px 0 6px 0;font-size:16px;font-weight:600;'
            f'color:{T["PRIMARY"]};line-height:1.5;">{leaf(head)}</p>'
            f'<p style="margin:0;font-size:15px;line-height:1.85;color:{BODY};">'
            f'{inline(desc, T)}</p></section></section>'
        )
    out.append("</section>")
    return "".join(out)


def c_table(rows, T):
    mx = max(range(len(rows)), key=lambda i: len(rows[i][1])) if rows else -1
    out = [
        f'<section style="margin:22px 0;border:1px solid {LINE};border-radius:8px;'
        f'overflow:hidden;">'
        f'<section style="display:flex;background:{T["TINT"]};padding:11px 14px;">'
        f'<section style="flex:2;">{leaf("情形", f"font-size:13px;font-weight:600;color:{T['PRIMARY']};")}</section>'
        f'<section style="flex:1;text-align:right;">{leaf("处罚", f"font-size:13px;font-weight:600;color:{T['PRIMARY']};")}</section>'
        f'</section>'
    ]
    for i, (a, b) in enumerate(rows):
        col = T["ACCENT"] if i == mx else BODY
        out.append(
            f'<section style="display:flex;padding:13px 14px;border-top:1px solid #EDF1F6;">'
            f'<section style="flex:2;">{leaf(a, f"font-size:14px;line-height:1.6;color:{BODY};")}</section>'
            f'<section style="flex:1;text-align:right;">'
            f'{leaf(b, f"font-size:15px;font-weight:600;color:{col};")}</section></section>'
        )
    out.append("</section>")
    return "".join(out)


def c_backref(t, T):
    return (
        f'<section style="margin:20px 0;padding:12px 16px;background:{T["TINT"]};'
        f'border-radius:6px;"><p style="margin:0;font-size:14px;line-height:1.8;'
        f'color:{SUB};">{leaf(t)}</p></section>'
    )


def c_fix(t, T):
    return (
        f'<section style="margin:22px 0;border:1px solid {T["ACCENT"]};border-radius:6px;'
        f'padding:14px 16px;background:#FFFDF8;">'
        f'<p style="margin:0 0 8px 0;font-size:12px;letter-spacing:0.5px;'
        f'font-weight:600;color:{T["ACCENT"]};">{leaf("更正")}</p>'
        f'<p style="margin:0;font-size:14px;line-height:1.85;color:{BODY};">'
        f'{leaf(t)}</p></section>'
    )


def c_cta(t, T):
    return (
        f'<section style="margin:30px 0 0 0;padding:18px 18px;border:1px solid {LINE};'
        f'border-radius:8px;"><p style="margin:0;font-size:14px;line-height:1.85;'
        f'color:{BODY};">{leaf(t)}</p></section>'
    )


def c_next(t, T):
    return (
        f'<section style="margin:28px 0 0 0;padding:14px 16px;background:{T["TINT"]};'
        f'border-radius:6px;"><p style="margin:0;font-size:14px;line-height:1.8;'
        f'color:{SUB};">{leaf(t)}</p></section>'
    )


# ── 解析 ──────────────────────────────────────────────

def render(md, T, layer, pub):
    out = []
    lines = md.split("\n")
    i = 0
    hn = 0
    lead_done = False
    first_para_done = False

    while i < len(lines):
        ln = lines[i].rstrip()

        if not ln.strip():
            i += 1
            continue

        if ln.startswith("# "):
            out.append(c_title(ln[2:].strip(), T))
            i += 1
            continue

        if ln.startswith("## "):
            hn += 1
            out.append(c_h2(f"{hn:02d}", ln[3:].strip(), T))
            i += 1
            first_para_done = True
            continue

        m = re.match(r"!!倒计时\s+(\d{4}-\d{2}-\d{2})!!", ln)
        if m:
            out.insert(0, c_deadline(m.group(1), pub, T))
            i += 1
            continue

        m = re.match(r"!!法条\s+(.+?)\s*\|\s*(.+?)!!", ln)
        if m:
            out.append(c_law(m.group(1).strip(), m.group(2).strip(), T))
            i += 1
            continue

        if ln.startswith("!!对号入座!!"):
            i += 1
            items = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    continue
                mm = re.match(r"^\d+\.\s*(.+?)\s*\|\s*(.+)$", s)
                if not mm:
                    break
                items.append((mm.group(1), mm.group(2)))
                i += 1
            if items:
                out.append(c_cases(items, T))
            continue

        if ln.startswith("!!对照!!"):
            i += 1
            rows = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    continue
                mm = re.match(r"^(.+?)\s*\|\s*(.+)$", s)
                if not mm or s.startswith("!!"):
                    break
                rows.append((mm.group(1), mm.group(2)))
                i += 1
            if rows:
                out.append(c_table(rows, T))
            continue

        m = re.match(r"!!回指!!\s*(.+)", ln)
        if m:
            out.append(c_backref(m.group(1).strip(), T))
            i += 1
            continue

        m = re.match(r"!!更正!!\s*(.+)", ln)
        if m:
            out.append(c_fix(m.group(1).strip(), T))
            i += 1
            continue

        m = re.match(r"!!预告!!\s*(.+)", ln)
        if m:
            out.append(c_next(m.group(1).strip(), T))
            i += 1
            continue

        if ln.startswith("> "):
            t = ln[2:].strip()
            if not lead_done and not first_para_done:
                out.append(c_lead(t, T))
                lead_done = True
            else:
                out.append(c_quote(t, T))
            i += 1
            continue

        if "欢迎加入星球聊一聊" in ln:
            out.append(c_cta(ln.strip(), T))
            i += 1
            continue

        out.append(c_p(ln.strip(), T))
        first_para_done = True
        i += 1

    return (
        f'<section style="font-family:-apple-system,BlinkMacSystemFont,'
        f'\'PingFang SC\',\'Hiragino Sans GB\',sans-serif;color:{BODY};'
        f'font-size:16px;letter-spacing:0.3px;">' + "".join(out) + "</section>"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--theme", choices=["navy", "amber"], default="navy")
    ap.add_argument("--layer", choices=["入口", "转化", "沉淀"])
    ap.add_argument("--pubdate")
    a = ap.parse_args()

    T = THEMES[a.theme]
    pub = dt.date.fromisoformat(a.pubdate) if a.pubdate else dt.date.today()
    src = pathlib.Path(a.path)
    md = src.read_text(encoding="utf-8")

    htm = render(md, T, a.layer, pub)
    out = src.with_name(f"{src.stem}_排版_{T['name']}.html")
    out.write_text(htm, encoding="utf-8")

    print(f"\n已排版 → {out}")
    print(f"主题 {T['name']} · 层级 {a.layer or '未指定'} · 发布日 {pub}")
    print(f"\n下一步：")
    print(f"  python scripts/validate_gzh_html.py \"{out}\"")
    print(f"  python scripts/wrap_preview.py \"{out}\"")


if __name__ == "__main__":
    main()
