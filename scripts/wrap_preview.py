#!/usr/bin/env python3
"""把干净正文片段包成带复制按钮的预览页。

用法: wrap_preview.py <正文.html>
产出: {同名}_预览.html
"""
import pathlib
import sys

TPL = """<!DOCTYPE html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>预览 · __NAME__</title>
<style>
body{margin:0;background:#EEF1F5;font-family:-apple-system,"PingFang SC",sans-serif}
#bar{position:sticky;top:0;background:#1E3A5F;padding:12px 16px;display:flex;
justify-content:space-between;align-items:center;z-index:9;
box-shadow:0 2px 8px rgba(0,0,0,.15)}
#bar span{color:#fff;font-size:13px;overflow:hidden;text-overflow:ellipsis;
white-space:nowrap;margin-right:12px}
#btn{background:#C8963E;color:#fff;border:0;border-radius:5px;padding:9px 20px;
font-size:14px;cursor:pointer;flex:0 0 auto;font-weight:600}
#btn:active{opacity:.8}
#tip{max-width:677px;margin:14px auto 0;padding:0 20px;font-size:12px;color:#7A8698}
#wrap{max-width:677px;margin:10px auto 40px;background:#fff;padding:26px 20px}
</style>
<div id="bar"><span>__NAME__</span><button id="btn">复制到公众号</button></div>
<div id="tip">点上方按钮复制，到公众号编辑器 Ctrl+V 粘贴。按钮无效时可在下方正文区手动全选复制。</div>
<div id="wrap">__BODY__</div>
<script>
document.getElementById('btn').onclick=async function(){
  var b=this, el=document.getElementById('wrap');
  var done=function(t){b.textContent=t;setTimeout(function(){
    b.textContent='复制到公众号';},1800);};
  try{
    if(navigator.clipboard&&window.ClipboardItem){
      var html=el.innerHTML;
      await navigator.clipboard.write([new ClipboardItem({
        'text/html':new Blob([html],{type:'text/html'}),
        'text/plain':new Blob([el.innerText],{type:'text/plain'})
      })]);
      return done('已复制');
    }
  }catch(e){}
  try{
    var r=document.createRange();r.selectNode(el);
    var s=getSelection();s.removeAllRanges();s.addRange(r);
    var ok=document.execCommand('copy');s.removeAllRanges();
    return done(ok?'已复制':'请手动全选复制');
  }catch(e){ return done('请手动全选复制'); }
};
</script>
"""

if len(sys.argv) < 2:
    print("用法: wrap_preview.py <正文.html>")
    sys.exit(2)

src = pathlib.Path(sys.argv[1])
if not src.exists():
    print(f"找不到文件：{src}")
    sys.exit(1)

out = src.with_name(src.stem + "_预览.html")
page = TPL.replace("__NAME__", src.stem).replace("__BODY__", src.read_text(encoding="utf-8"))
out.write_text(page, encoding="utf-8")

print(f"\n预览页已生成 → {out.resolve()}")
print("双击打开 → 点右上角「复制到公众号」→ 公众号编辑器 Ctrl+V")
