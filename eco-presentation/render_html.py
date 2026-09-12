# -*- coding: utf-8 -*-
"""Render the ECO deck to a single self-contained HTML file (arrow keys / click to navigate)."""
import html
import io
import os

from content import META, SLIDES

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ECO_Product_Presentation.html")

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
 --bg:#0b1220; --bg2:#0f1a2c; --card:#16233a; --line:#25344f;
 --tx:#e9eef7; --mut:#93a8c6; --acc:#4f8dff; --acc2:#22d3ee;
 --ok:#34d399; --warn:#fbbf24; --dan:#f87171;
}
html,body{height:100%}
body{background:#060a12;color:var(--tx);
 font-family:"Segoe UI",Inter,system-ui,-apple-system,Roboto,Arial,"Segoe UI Symbol","Apple Symbols","DejaVu Sans",sans-serif;
 display:flex;align-items:center;justify-content:center;overflow:hidden}
#stage{position:relative;width:min(100vw,calc(100vh*16/9));height:min(100vh,calc(100vw*9/16));}
.slide{position:absolute;inset:0;padding:5.2% 6%;background:
  radial-gradient(120% 90% at 100% 0%,#16243c 0%,rgba(11,18,32,0) 55%),
  linear-gradient(160deg,var(--bg) 0%,#0a1526 100%);
 display:none;flex-direction:column;container-type:size}
.slide.on{display:flex;animation:in .35s ease}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.kicker{font-size:2.1cqh;letter-spacing:.22em;text-transform:uppercase;color:var(--acc2);font-weight:700}
h1{font-size:11cqh;line-height:1.02;letter-spacing:-.02em;font-weight:800}
h2{font-size:6.6cqh;line-height:1.1;letter-spacing:-.015em;font-weight:750;margin:.8cqh 0 0}
h2::after{content:"";display:block;width:9cqh;height:.6cqh;border-radius:9px;margin-top:1.6cqh;
 background:linear-gradient(90deg,var(--acc),var(--acc2))}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;gap:2cqh;padding-top:1cqh}
ul{list-style:none;display:flex;flex-direction:column;gap:1.9cqh}
ul.two{display:block;column-count:2;column-gap:4cqh}
ul.two li{break-inside:avoid;margin-bottom:2cqh}
li{position:relative;padding-left:3.4cqh;font-size:3.15cqh;line-height:1.42;color:#dbe5f4}
ul.two li{font-size:2.75cqh}
li::before{content:"";position:absolute;left:0;top:.55em;width:1.25cqh;height:1.25cqh;border-radius:3px;
 background:linear-gradient(135deg,var(--acc),var(--acc2))}
li b{color:#fff;font-weight:700}
.note{font-size:2.5cqh;color:var(--mut);border-left:.45cqh solid var(--acc);padding-left:2cqh;font-style:italic}
.call{display:flex;gap:1.8cqh;align-items:flex-start;background:#132039;border:1px solid var(--line);
 border-left:.7cqh solid var(--acc);border-radius:10px;padding:2.2cqh 2.4cqh;font-size:2.7cqh;line-height:1.4}
.call.warn{border-left-color:var(--warn);background:#241d0f}
.call.danger{border-left-color:var(--dan);background:#2a1418}
.call.ok{border-left-color:var(--ok);background:#0f2418}
.call .ic{font-size:3.2cqh;line-height:1}
.chips{display:flex;align-items:center;gap:1.2cqh;flex-wrap:wrap}
.chip{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:1.5cqh 2.6cqh;
 font-size:2.6cqh;font-weight:650;white-space:nowrap}
.chip.acc{background:linear-gradient(135deg,#1b3a6b,#12293f);border-color:#2f5f9e;color:#fff}
.arrow{color:var(--acc2);font-size:3cqh;font-weight:800}
.rowlab{font-size:2.2cqh;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);margin-bottom:1.4cqh;font-weight:700}
.flowrow{margin-bottom:3cqh}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:2.4cqh;flex:1;align-content:center}
.card{background:var(--card);border:1px solid var(--line);border-top:.7cqh solid var(--acc);border-radius:14px;
 padding:2.8cqh 2.4cqh;display:flex;flex-direction:column;gap:1.4cqh}
.card.ok{border-top-color:var(--ok)} .card.warn{border-top-color:var(--warn)}
.card .tag{font-size:2.1cqh;letter-spacing:.16em;text-transform:uppercase;color:var(--acc2);font-weight:750}
.card h3{font-size:3.5cqh;line-height:1.15;font-weight:750}
.card p{font-size:2.5cqh;line-height:1.35;color:#cddbee;padding-left:2.6cqh;position:relative}
.card p::before{content:"";position:absolute;left:.4cqh;top:.6em;width:.9cqh;height:.9cqh;border-radius:50%;background:var(--acc2)}
ol{list-style:none;display:flex;flex-direction:column;gap:2.2cqh;counter-reset:s}
ol li{counter-increment:s;padding-left:6.5cqh;font-size:3.1cqh;line-height:1.4}
ol li::before{content:counter(s);left:0;top:0;width:4.6cqh;height:4.6cqh;border-radius:50%;
 background:linear-gradient(135deg,var(--acc),#2563eb);display:flex;align-items:center;justify-content:center;
 font-size:2.5cqh;font-weight:800;color:#fff}
table{width:100%;border-collapse:collapse;font-size:2.45cqh}
th{text-align:left;font-size:2.1cqh;letter-spacing:.16em;text-transform:uppercase;color:var(--acc2);
 padding:0 2cqh 1.4cqh;border-bottom:1px solid var(--line)}
td{padding:1.5cqh 2cqh;vertical-align:top;line-height:1.35;border-bottom:1px solid rgba(37,52,79,.6)}
tr td:first-child{font-weight:700;color:#fff;width:31%}
tbody tr:nth-child(even){background:rgba(22,35,58,.55)}
.gl{display:grid;grid-template-columns:1fr 1fr;gap:1.5cqh 3.4cqh;align-content:center;flex:1}
.gl div{display:flex;gap:1.4cqh;align-items:baseline;font-size:2.5cqh;border-bottom:1px solid rgba(37,52,79,.55);padding-bottom:1.2cqh}
.gl b{color:var(--acc2);font-weight:800;min-width:11cqh}
.gl span{color:#cddbee}
.title-slide{justify-content:center;gap:2.6cqh;background:
  radial-gradient(90% 120% at 85% 15%,#1d3a63 0%,rgba(11,18,32,0) 60%),linear-gradient(150deg,#0a1424,#0b1a30)}
.title-slide .bar{width:14cqh;height:.9cqh;border-radius:9px;background:linear-gradient(90deg,var(--acc),var(--acc2))}
.title-slide .sub{font-size:4.4cqh;color:#bcd0ec;font-weight:600}
.title-slide .tag{font-size:2.9cqh;color:var(--mut);max-width:70%}
.title-slide .meta{font-size:2.1cqh;color:#6f87a8;margin-top:3cqh}
.big{display:flex;flex-direction:column;gap:2.4cqh;justify-content:center;flex:1}
.big div{display:flex;gap:2.4cqh;align-items:center;font-size:3.5cqh;font-weight:650}
.big span.n{color:var(--acc2);font-weight:800;font-variant-numeric:tabular-nums;opacity:.85}
footer{display:flex;justify-content:space-between;align-items:center;font-size:1.95cqh;color:#65799a;
 border-top:1px solid rgba(37,52,79,.7);padding-top:1.6cqh;margin-top:1.6cqh}
#bar{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--acc),var(--acc2));z-index:9;transition:width .25s}
#hint{position:fixed;bottom:10px;right:14px;font-size:11px;color:#4a5a75;z-index:9}
@media print{
 @page{size:A4 landscape;margin:0}
 body{display:block;overflow:visible;background:#0b1220}
 #stage{width:100%;height:auto}
 .slide{display:flex!important;position:relative;inset:auto;width:100%;height:100vh;
  page-break-after:always;break-after:page;animation:none}
 #bar,#hint{display:none}
}
"""

JS = """
const s=[...document.querySelectorAll('.slide')];let i=0;
const bar=document.getElementById('bar');
function go(n){i=Math.max(0,Math.min(s.length-1,n));s.forEach((e,k)=>e.classList.toggle('on',k===i));
 bar.style.width=((i+1)/s.length*100)+'%';location.hash='#'+(i+1);}
document.addEventListener('keydown',e=>{
 if(['ArrowRight','PageDown',' ','Enter','n'].includes(e.key))go(i+1);
 if(['ArrowLeft','PageUp','p'].includes(e.key))go(i-1);
 if(e.key==='Home')go(0); if(e.key==='End')go(s.length-1);});
document.addEventListener('click',e=>go(i+(e.clientX<window.innerWidth*0.25?-1:1)));
go(parseInt((location.hash||'#1').slice(1))-1||0);
"""


def esc(t):
    return html.escape(t, quote=False)


def rich(segs):
    if isinstance(segs, str):
        return esc(segs)
    return "".join("<b>%s</b>" % esc(t) if b else esc(t) for t, b in segs)


def callout(c):
    ic = {"warn": "\u26a0", "danger": "\u26d4", "ok": "\u2713"}.get(c.get("tone", ""), "\u2139")
    return '<div class="call %s"><div class="ic">%s</div><div>%s</div></div>' % (
        c.get("tone", ""), ic, rich(c["text"]))


def head(s):
    o = ""
    if s.get("kicker"):
        o += '<div class="kicker">%s</div>' % esc(s["kicker"])
    o += "<h2>%s</h2>" % esc(s["title"])
    return o


def render():
    w = io.StringIO()
    w.write("<!doctype html><html lang=en><meta charset=utf-8>")
    w.write("<meta name=viewport content='width=device-width,initial-scale=1'>")
    w.write("<title>%s \u2014 %s</title>" % (esc(META["title"]), esc(META["subtitle"])))
    w.write("<style>%s</style><body><div id=bar></div><div id=stage>" % CSS)

    total = len(SLIDES)
    for n, s in enumerate(SLIDES, 1):
        k = s["kind"]
        w.write('<section class="slide%s">' % (" title-slide" if k == "title" else ""))

        if k == "title":
            w.write('<div class="bar"></div><h1>%s</h1><div class="sub">%s</div>'
                    '<div class="tag">%s</div><div class="meta">%s</div>'
                    % (esc(s["title"]), esc(s["subtitle"]), esc(s["tagline"]), esc(s["meta"])))
            w.write("</section>")
            continue

        if k == "close":
            w.write('<div class="kicker">Wrap-up</div><h2>%s</h2><div class="big">' % esc(s["title"]))
            for j, p in enumerate(s["points"], 1):
                w.write('<div><span class="n">%02d</span><span>%s</span></div>' % (j, esc(p)))
            w.write('</div><div class="meta" style="font-size:2.1cqh;color:#6f87a8">%s</div>' % esc(s["meta"]))
            w.write('<footer><span>%s</span><span>%d / %d</span></footer></section>' % (esc(META["footer"]), n, total))
            continue

        w.write(head(s))
        w.write('<div class="body">')

        if k == "bullets":
            cls = "two" if s.get("columns") == 2 else ""
            w.write('<ul class="%s">' % cls)
            for b in s["bullets"]:
                w.write("<li>%s</li>" % rich(b))
            w.write("</ul>")
            if s.get("note"):
                w.write('<div class="note">%s</div>' % esc(s["note"]))

        elif k == "steps":
            w.write("<ol>")
            for st in s["steps"]:
                w.write("<li>%s</li>" % rich(st))
            w.write("</ol>")

        elif k == "flow":
            for r in s["rows"]:
                w.write('<div class="flowrow"><div class="rowlab">%s</div><div class="chips">' % esc(r["label"]))
                for j, c in enumerate(r["chips"]):
                    if j:
                        w.write('<span class="arrow">\u203a</span>')
                    w.write('<span class="chip %s">%s</span>' % ("acc" if r["style"] == "accent" else "", esc(c)))
                w.write("</div></div>")
            if s.get("footnote"):
                w.write('<div class="note">%s</div>' % esc(s["footnote"]))

        elif k == "cards":
            w.write('<div class="cards">')
            for c in s["cards"]:
                w.write('<div class="card %s"><div class="tag">%s</div><h3>%s</h3>'
                        % (c.get("tone", ""), esc(c["tag"]), esc(c["title"])))
                for ln in c["lines"]:
                    w.write("<p>%s</p>" % esc(ln))
                w.write("</div>")
            w.write("</div>")
            if s.get("footnote"):
                w.write('<div class="note">%s</div>' % esc(s["footnote"]))

        elif k == "table":
            w.write("<table><thead><tr>%s</tr></thead><tbody>"
                    % "".join("<th>%s</th>" % esc(h) for h in s["head"]))
            for r in s["rows"]:
                w.write("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r))
            w.write("</tbody></table>")

        elif k == "glossary":
            w.write('<div class="gl">')
            for a, b in s["pairs"]:
                w.write("<div><b>%s</b><span>%s</span></div>" % (esc(a), esc(b)))
            w.write("</div>")

        if s.get("callout"):
            w.write(callout(s["callout"]))

        w.write("</div>")
        w.write('<footer><span>%s</span><span>%d / %d</span></footer></section>' % (esc(META["footer"]), n, total))

    w.write("</div><div id=hint>\u2190 \u2192 to navigate \u00b7 Ctrl/Cmd+P \u2192 Save as PDF</div>")
    w.write("<script>%s</script></body></html>" % JS)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(w.getvalue())
    return OUT, total


if __name__ == "__main__":
    p, t = render()
    print("HTML deck: %s (%d slides, %d KB)" % (p, t, os.path.getsize(p) // 1024))
