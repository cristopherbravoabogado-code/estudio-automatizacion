# Genera el index.html de HyperFrames (overlay transparente 1080x1920) para un supervideo.
import json
def wt(words, w):
    for t,s,e in words:
        if t.strip(".,:¿?").lower()==w.lower(): return s
    raise KeyError(w)
def html(key, T0, TOTAL, WORDS, HEAD):
    h1,h2,titular = HEAD
    A = key=="A"
    tP = T0[1]+0.4
    if A:
        tS1 = T0[2]+wt(WORDS[2],"treinta"); tS2 = T0[3]+wt(WORDS[3],"trescientos"); tS3 = T0[3]+wt(WORDS[3],"once"); tSout = T0[4]+0.3
        tR = [T0[5]+wt(WORDS[5],"treinta"), T0[5]+wt(WORDS[5],"cincuenta"), T0[5]+wt(WORDS[5],"ochenta")]; tRout = max(T0[6]+0.2, tR[-1]+1.3)
    else:
        tS1 = T0[2]+wt(WORDS[2],"dueño"); tS2 = T0[4]+wt(WORDS[4],"dueño"); tS3 = T0[4]+wt(WORDS[4],"demandar"); tSout = T0[5]+0.3
        tR = [T0[5]+wt(WORDS[5],"prohíbe")]; tRout = max(T0[6]+0.2, tR[-1]+1.3)
    tC = TOTAL-6.5
    stat_html = ('<div id="stat" class="grp" style="top:420px"><div class="big"><span id="num">0</span><span class="unit"> DÍAS</span></div>'
                 '<div class="lab" id="lab1">DE SUELDO POR CADA AÑO</div><div class="slam" id="slam">= 11 SUELDOS</div></div>') if A else \
                ('<div id="stat" class="grp" style="top:420px"><div class="tag2">ART. 2326 · CÓDIGO CIVIL</div><div class="mid" id="mid"><span id="strk">EL DUEÑO RESPONDE</span><div class="line" id="line"></div></div>'
                 '<div class="slam" id="slam">NADIE PAGA</div></div>')
    rec_html = ('<div id="rec" class="grp" style="top:520px"><div class="tag2">RECARGO SI EL DESPIDO ERA INJUSTIFICADO</div>'
                '<div class="bar" id="b0">+30%<span> necesidades de la empresa</span></div><div class="bar" id="b1">+50%<span> causal inventada</span></div><div class="bar" id="b2">+80%<span> falsa acusación</span></div></div>') if A else \
               ('<div id="rec" class="grp" style="top:520px"><div class="tag2">LEY DE CAZA · ART. 3</div><div class="bar" id="b0">PROHIBIDO<span> cazar fauna silvestre protegida</span></div></div>')
    js_stat = (f'tl.set("#stat",{{opacity:1}},{tS1:.3f});tl.fromTo("#stat .big",{{scale:1.6,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{tS1:.3f});'
               f'tl.to(N,{{v:30,duration:.9,ease:"power2.out",onUpdate:()=>{{document.getElementById("num").textContent=Math.round(N.v)}}}},{tS1:.3f});'
               f'tl.fromTo("#lab1",{{x:-60,opacity:0}},{{x:0,opacity:1,duration:.35}},{tS1+.25:.3f});'
               f'tl.to(N,{{v:330,duration:1.0,ease:"power3.out",onUpdate:()=>{{document.getElementById("num").textContent=Math.round(N.v)}}}},{tS2:.3f});'
               f'tl.to("#lab1",{{textContent:"TOPE MÁXIMO",duration:0}},{tS2:.3f});tl.fromTo("#lab1",{{x:-60,opacity:0}},{{x:0,opacity:1,duration:.35}},{tS2:.3f});'
               f'tl.fromTo("#slam",{{scale:2,opacity:0,rotation:-4}},{{scale:1,opacity:1,rotation:-2,duration:.28,ease:"back.out(3)"}},{tS3:.3f});'
               f'tl.to("#stat",{{opacity:0,y:-40,duration:.25}},{tSout:.3f});') if A else \
              (f'tl.set("#stat",{{opacity:1}},{tS1:.3f});tl.fromTo("#stat .tag2",{{x:-60,opacity:0}},{{x:0,opacity:1,duration:.3}},{tS1:.3f});'
               f'tl.fromTo("#mid",{{scale:1.5,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{tS1+.15:.3f});'
               f'tl.fromTo("#line",{{scaleX:0}},{{scaleX:1,duration:.35,ease:"power3.inOut"}},{tS2:.3f});tl.to("#strk",{{opacity:.45,duration:.3}},{tS2:.3f});'
               f'tl.fromTo("#slam",{{scale:2,opacity:0,rotation:-4}},{{scale:1,opacity:1,rotation:-2,duration:.28,ease:"back.out(3)"}},{tS3:.3f});'
               f'tl.to("#stat",{{opacity:0,y:-40,duration:.25}},{tSout:.3f});')
    js_rec = f'tl.set("#rec",{{opacity:1}},{tR[0]-.2:.3f});tl.fromTo("#rec .tag2",{{opacity:0}},{{opacity:1,duration:.2}},{tR[0]-.2:.3f});'
    for i,t in enumerate(tR):
        js_rec += f'tl.fromTo("#b{i}",{{x:-900,opacity:0}},{{x:0,opacity:1,duration:.32,ease:"expo.out"}},{t:.3f});'
    js_rec += f'tl.to("#rec",{{opacity:0,duration:.25}},{tRout:.3f});'
    return f'''<!doctype html><html lang="es"><head><meta charset="UTF-8"><title>{key}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
html,body{{margin:0;padding:0;width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:"Liberation Sans",Arial,Helvetica,sans-serif;font-weight:700}}
#master-root{{width:1080px;height:1920px;position:relative;background:transparent}}
.grp{{position:absolute;left:140px;width:800px;opacity:0}}
.box{{display:inline-block;background:rgba(0,0,0,.78);color:#fff;font-size:96px;line-height:1.02;padding:14px 26px;margin-bottom:18px;letter-spacing:-.02em;text-transform:uppercase;opacity:0;box-shadow:0 12px 40px rgba(0,0,0,.45)}}
.box.red{{background:#E5261F}}
.ul{{height:14px;width:800px;background:#E5261F;transform-origin:left;transform:scaleX(0)}}
.tag{{margin-top:22px;font-size:30px;color:#fff;background:rgba(0,0,0,.6);display:inline-block;padding:8px 16px;letter-spacing:.18em;opacity:0}}
.lbl{{display:inline-block;background:#E5261F;color:#fff;font-size:34px;letter-spacing:.14em;padding:10px 20px}}
.head{{background:rgba(255,255,255,.96);color:#111;font-size:44px;line-height:1.15;padding:22px 26px;border-left:16px solid #E5261F;box-shadow:0 14px 40px rgba(0,0,0,.5)}}
.big{{color:#fff;font-size:210px;line-height:.95;text-shadow:0 8px 30px rgba(0,0,0,.7);opacity:0}}
.big .unit{{font-size:78px}}
.lab{{color:#fff;font-size:48px;background:rgba(0,0,0,.7);display:inline-block;padding:10px 20px;margin-top:10px;opacity:0}}
.slam{{display:inline-block;margin-top:26px;background:#E5261F;color:#fff;font-size:92px;padding:12px 28px;opacity:0;transform:rotate(-2deg);box-shadow:0 14px 40px rgba(0,0,0,.5)}}
.tag2{{color:#fff;font-size:30px;letter-spacing:.16em;background:rgba(0,0,0,.6);display:inline-block;padding:8px 16px;margin-bottom:16px;opacity:0}}
.mid{{position:relative;display:inline-block;color:#fff;font-size:84px;line-height:1.05;background:rgba(0,0,0,.72);padding:12px 24px;opacity:0}}
.line{{position:absolute;left:0;top:50%;height:12px;width:100%;background:#E5261F;transform-origin:left;transform:scaleX(0)}}
.bar{{color:#fff;font-size:88px;background:rgba(0,0,0,.78);padding:8px 24px;margin-bottom:14px;opacity:0;border-left:18px solid #E5261F;line-height:1.05}}
.bar span{{font-size:38px;font-weight:400;display:block;letter-spacing:.02em}}
#cta{{position:absolute;left:140px;top:1400px;width:800px;opacity:0}}
.card{{background:rgba(255,255,255,.97);color:#111;padding:22px 30px;border-left:18px solid #E5261F;box-shadow:0 16px 50px rgba(0,0,0,.55);transform:translateX(-1000px)}}
.card .n{{font-size:32px;letter-spacing:.12em;color:#333}}
.card .p{{font-size:64px;line-height:1.05;margin-top:6px;color:#E5261F}}
</style></head><body>
<div id="master-root" data-composition-id="master" data-width="1080" data-height="1920" data-start="0" data-duration="{TOTAL:.3f}">
 <div id="hook" class="grp" style="top:330px"><div class="box" id="l1">{h1}</div><br><div class="box red" id="l2">{h2}</div><div class="ul" id="ul"></div><div class="tag" id="tg">NOTICIA REAL · BIOBIOCHILE · 13 SEP</div></div>
 <div id="press" class="grp" style="top:1000px"><div class="lbl">NOTICIA · 13 DE SEPTIEMBRE</div><div class="head">{titular}</div></div>
 {stat_html}
 {rec_html}
 <div id="cta"><div class="card"><div class="n">ESTUDIO JURÍDICO SAN BERNARDO</div><div class="p">+56 9 9690 5994</div></div></div>
<script>
window.__timelines=window.__timelines||{{}};
const tl=gsap.timeline({{paused:true}}); const N={{v:0}};
tl.set("#hook",{{opacity:1}},0);
tl.fromTo("#l1",{{scale:1.8,opacity:0,y:40}},{{scale:1,opacity:1,y:0,duration:.3,ease:"back.out(2.2)"}},0.12);
tl.fromTo("#l2",{{scale:1.8,opacity:0,y:40}},{{scale:1,opacity:1,y:0,duration:.3,ease:"back.out(2.2)"}},0.62);
tl.to("#ul",{{scaleX:1,duration:.4,ease:"power3.out"}},1.0);
tl.fromTo("#tg",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.3}},1.3);
tl.to("#hook",{{scale:1.12,opacity:0,duration:.25,ease:"power2.in"}},3.3);
tl.set("#press",{{opacity:1}},{tP:.3f});
tl.fromTo("#press",{{x:-1000}},{{x:0,duration:.45,ease:"expo.out"}},{tP:.3f});
tl.to("#press",{{x:1100,duration:.35,ease:"power3.in"}},{tP+4.3:.3f});
{js_stat}
{js_rec}
tl.set("#cta",{{opacity:1}},{tC:.3f});
tl.to("#cta .card",{{x:0,duration:.5,ease:"expo.out"}},{tC:.3f});
tl.to("#cta .card",{{scale:1.03,duration:.5,yoyo:true,repeat:8,ease:"sine.inOut"}},{tC+.6:.3f});
window.__timelines["master"]=tl;
</script></div></body></html>'''
if __name__=="__main__":
    import sys,data
    key=sys.argv[1]; tl=json.load(open(f"tl_{key}.json"))
    WORDS=[[tuple(w) for w in ws] for ws in tl["words"]]  # tiempos COMPRIMIDOS (los mismos del audio), no los crudos de HeyGen
    open(f"hf_{key}/index.html","w",encoding="utf-8").write(html(key,tl["t0"],tl["total"],WORDS,data.HEAD[key]))
    print("overlay html ok",key,round(tl["total"],2))
