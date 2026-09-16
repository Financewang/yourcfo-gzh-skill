#!/usr/bin/env python3
"""微信公众号 HTML 平台合规校验。

只管"能不能粘贴"：禁用标签属性、<span leaf> 包裹。
内容结构问题归 content_audit.py 管，两者分工不重叠。

用法: validate_gzh_html.py <file.html>
退出码: 1 = 有 ERROR。
"""
import re
import sys
from html.parser import HTMLParser

FORBIDDEN = [
    (r"<style[\s>]", "<style> 会被过滤，样式必须内联"),
    (r"<script[\s>]", "<script> 会被过滤"),
    (r"</?div[\s>]", "<div> 会被改写，请用 <section>"),
    (r"<link[\s>]", "外部 <link> 会被过滤"),
    (r"\sclass\s*=", "class 属性会被剥离"),
    (r"\sid\s*=", "id 属性会被剥离"),
    (r"position\s*:\s*(fixed|absolute|sticky)", "position fixed/absolute/sticky 不支持"),
    (r"float\s*:", "float 不支持"),
    (r"@media", "@media 不支持"),
    (r"@keyframes", "@keyframes 不支持"),
    (r"@import", "@import 不支持"),
    (r"display\s*:\s*grid", "display:grid 不支持，请用 flex"),
    (r"var\s*\(\s*--", "CSS 变量不支持，请写死值"),
    (r"<!DOCTYPE", "产物应为纯 section 片段，不要文档外壳"),
    (r"</?html[\s>]", "产物应为纯 section 片段"),
    (r"</?body[\s>]", "产物应为纯 section 片段"),
    (r"\{PRIMARY\}|\{ACCENT\}|\{TINT\}", "组件色值占位符未替换"),
    (r"width\s*:\s*100%[^;]*;[^\"']*\"[^>]*<img|<img[^>]*width\s*:\s*100%", "img 用 max-width:100% 而非 width:100%"),
]

CJK = re.compile(r"[\u4e00-\u9fff]")


class LeafCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.leaf = 0
        self.count = 0
        self.bad = []

    def handle_starttag(self, tag, attrs):
        if tag == "span" and any(k == "leaf" for k, _ in attrs):
            self.leaf += 1
            self.count += 1

    def handle_endtag(self, tag):
        if tag == "span" and self.leaf:
            self.leaf -= 1

    def handle_data(self, data):
        if data.strip() and CJK.search(data) and not self.leaf:
            self.bad.append(data.strip()[:30])


def main():
    if len(sys.argv) < 2:
        print("用法: validate_gzh_html.py <file.html>")
        sys.exit(2)

    html = open(sys.argv[1], encoding="utf-8").read()
    errs = []

    for pat, msg in FORBIDDEN:
        m = re.search(pat, html, re.I)
        if m:
            errs.append(f"{msg} —— 「{m.group(0)[:40]}」")

    lc = LeafCheck()
    lc.feed(html)
    for t in lc.bad[:5]:
        errs.append(f"中文文本未被 <span leaf=\"\"> 包裹 —— 「{t}」")
    if len(lc.bad) > 5:
        errs.append(f"另有 {len(lc.bad) - 5} 处未包裹文本")

    print(f"\n校验 {sys.argv[1]}")
    print(f"span leaf 共 {lc.count} 处\n")
    for e in errs:
        print(f"  ERROR  {e}")
    print(f"\n  合计 {len(errs)} 个 ERROR")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
