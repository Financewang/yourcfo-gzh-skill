#!/usr/bin/env python3
"""把干净正文片段包成带复制按钮的预览页。

用法: wrap_preview.py <正文.html>
产出: {同名}_预览.html
"""
import pathlib
import sys

TPL = """<!DOCTYPE html>
<meta charset="utf-8">
<title>预览 · {name}</title>
<style>
body{{margin:0;background:#EEF1F5;font-family:-apple-system,"PingFang SC",sans-serif}}
#bar{{position:sticky;top:0;background:#1E3A5F;padding:12px 16px;display:flex;
justify-content:space-between;align-items:center;z-index:9}}
#bar span{{color:#fff;font-size:13px}}
#btn{{background:#C8963E;color:#fff;border:0;border-radius:5px;padding:8px 18px;
font-size:14px;cursor:pointer}}
#wrap{{max-width:677px;margin:18px auto;background:#fff;padding:26px 20px}}
</style>
<div id="bar"><span>{name}</span><button id="btn">复制到公众号</button></div>
<div id="wrap">{body}</div>
<script>
document.getElementById('btn').onclick=async()=>{{
  const r=document.createRange();r.selectNode(document.getElementById('wrap'));
  const s=getSelection();s.removeAllRanges();s.addRange(r);
  document.execCommand('copy');s.removeAllRanges();
  const b=document.getElementById('btn');b.textContent='已复制';
  setTimeout(()=>b.textContent='复制到公众号',1600);
}};
</script>
"""

src = pathlib.Path(sys.argv[1])
out = src.with_name(src.stem + "_预览.html")
out.write_text(TPL.format(name=src.stem, body=src.read_text(encoding="utf-8")), encoding="utf-8")
print(f"预览页 → {out}")
print("浏览器打开 → 点右上角复制 → 公众号编辑器粘贴")
