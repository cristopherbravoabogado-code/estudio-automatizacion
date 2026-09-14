#!/usr/bin/env python3
"""build_sv.py — supervideo: prep <A|B>  |  final <A|B> <upload_url>"""
import sys,os,json,subprocess,urllib.request,numpy as np,wave,data
SR=48000;FPS=30;XF=0.4;MAXGAP=0.42;LEAD=0.15;TAIL=0.30
def sh(c,t=900): r=subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t); return r
def dl(u,p):
    if not (os.path.exists(p) and os.path.getsize(p)>2000):
        rq=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}); open(p,"wb").write(urllib.request.urlopen(rq,timeout=120).read())
def dec(p):
    r=subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(r,dtype=np.float32).copy()
def prep(K):
    os.makedirs("vo",exist_ok=True);os.makedirs("f",exist_ok=True);os.makedirs("sh",exist_ok=True);os.makedirs("mus",exist_ok=True);os.makedirs("sfx",exist_ok=True)
    for i in range(1,8): dl(data.VOICE_BASE+data.VOICE_ID[f"{K}{i}"]+".wav",f"vo/{K}{i}.wav")
    dl(data.PRESS[K],f"press_{K}.jpg"); dl(data.MUS[K],f"mus/{K}.mp3")
    for n,u in data.SFX.items(): dl(u,f"sfx/{n}.mp3")
    for s in data.SHOTS[K]:
        for c in s[1:]:
            if s[0]!="img": dl(f"https://assets.mixkit.co/videos/{c}/{c}-720.mp4",f"f/{c}.mp4")
    # timeline
    T0=[];D=[];WS=[];segs=[];t=0.0
    for i in range(1,8):
        a=dec(f"vo/{K}{i}.wav");out=[];nw=[];ot=LEAD;pe=0.0
        out.append(np.zeros(int(LEAD*SR),dtype=np.float32))
        for tx,s,e in data.words(f"{K}{i}"):
            kg=max(0.0,min(s-pe,MAXGAP if pe>0 else 0.10)); f0=int((s-kg)*SR);f1=int(e*SR); out.append(a[f0:f1])
            nw.append((tx,ot+kg,ot+(f1-f0)/SR)); ot+=(f1-f0)/SR; pe=e
        out.append(np.zeros(int((TAIL+(1.3 if i==7 else 0))*SR),dtype=np.float32))
        seg=np.concatenate(out); segs.append(seg); T0.append(t); D.append(len(seg)/SR); WS.append(nw); t+=len(seg)/SR
    TOTAL=t; json.dump({"t0":T0,"D":D,"total":TOTAL,"words":WS},open(f"tl_{K}.json","w"))
    # shots
    for k,s in enumerate(data.SHOTS[K]):
        L=D[k]+(XF if k<6 else 0); out=f"sh/{K}{k}.mp4"
        if s[0]=="img":
            FR=int(round(L*FPS))
            vf=f"scale=1350:-2,crop=1350:2400,zoompan=z='1+0.22*on/{FR}':x='iw/2-(iw/zoom/2)+16*sin(on/2.9)':y='ih/2-(ih/zoom/2)+12*sin(on/2.2)':d={FR}:s=1080x1920:fps={FPS},format=yuv420p"
            sh(f'ffmpeg -y -v error -i press_{K}.jpg -vf "{vf}" -frames:v {FR} -r {FPS} -c:v libx264 -preset veryfast -crf 18 {out}')
        else:
            clips=s[1:]; parts=[]
            for j,c in enumerate(clips):
                Lj=L/len(clips); pj=f"sh/{K}{k}_{j}.mp4"
                sh(f'ffmpeg -y -v error -stream_loop -1 -i f/{c}.mp4 -t {Lj:.3f} -an -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},format=yuv420p" -c:v libx264 -preset veryfast -crf 18 {pj}'); parts.append(pj)
            if len(parts)==1: os.replace(parts[0],out)
            else:
                open("cc.txt","w").write("".join(f"file '{p}'\n" for p in parts)); sh(f"ffmpeg -y -v error -f concat -safe 0 -i cc.txt -c copy {out}")
    # xfade chain
    tr=["slideleft","wipeup","fade","slideright","wipedown","fade"]
    ins=" ".join(f"-i sh/{K}{k}.mp4" for k in range(7)); fc=""; prev="[0:v]"
    for k in range(1,7):
        o=f"[v{k}]"; fc+=f"{prev}[{k}:v]xfade=transition={tr[k-1]}:duration={XF}:offset={T0[k]:.3f}{o};"; prev=o
    sh(f'ffmpeg -y -v error {ins} -filter_complex "{fc[:-1]}" -map "{prev}" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -r {FPS} mute_{K}.mp4')
    # audio master
    M=np.zeros(int((TOTAL+1)*SR),dtype=np.float32); V=np.zeros_like(M)
    for k,seg in enumerate(segs):
        i=int(T0[k]*SR); V[i:i+len(seg)]+=seg
    M+=V*0.98
    env=np.abs(V); w=int(0.06*SR); env=np.convolve(env,np.ones(w)/w,"same"); gate=(env>0.012).astype(np.float32)
    w2=int(0.16*SR); gate=np.convolve(gate,np.ones(w2)/w2,"same"); gain=0.72-0.50*np.clip(gate,0,1)
    mus=dec(f"mus/{K}.mp3"); 
    if len(mus)<len(M): mus=np.tile(mus,int(len(M)/len(mus))+1)
    mus=mus[:len(M)]; mus=mus/(np.abs(mus).max()+1e-9); fi=int(1.0*SR); fo=int(2.5*SR)
    mus[:fi]*=np.linspace(0,1,fi); mus[-fo:]*=np.linspace(1,0,fo); M+=mus*gain*0.20
    wh=dec("sfx/whoosh.mp3"); bo=dec("sfx/boom.mp3"); ri=dec("sfx/riser.mp3")
    def put(x,t,g):
        i=max(0,int(t*SR)); n=min(len(x),len(M)-i); M[i:i+n]+=x[:n]*g
    put(bo,0.08,0.55)
    for k in range(1,7): put(wh,T0[k]-0.22,0.38)
    tl=json.load(open(f"tl_{K}.json")); W3=tl["words"][3]; W4=tl["words"][4]
    slam = T0[3]+[s for t,s,e in W3 if t.startswith("once")][0] if K=="A" else T0[4]+[s for t,s,e in W4 if t.startswith("demandar")][0]
    put(bo,slam-0.05,0.5); twist = T0[5] if K=="A" else T0[4]; put(ri,twist-2.4,0.42); put(bo,twist,0.45)
    m=float(np.abs(M).max()); M=(np.tanh(M/(m*0.88))*0.95).astype(np.float32)
    wv=wave.open(f"master_{K}.wav","wb");wv.setnchannels(1);wv.setsampwidth(2);wv.setframerate(SR);wv.writeframes((np.clip(M,-1,1)*32700).astype("<i2").tobytes());wv.close()
    # subs
    def ts(x): mm=int(x//60); return f"0:{mm:02d}:{x-mm*60:05.2f}"
    Y=[1230,1300,1180,1330,1210,1290,1160]
    L=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 2","ScaledBorderAndShadow: yes","","[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding","Style: K,Liberation Sans,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,1,5,4,5,60,60,60,1","","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for k in range(7):
        ws=WS[k]
        for i,(tx,a,b) in enumerate(ws):
            st=T0[k]+a; en=T0[k]+(ws[i+1][1] if i+1<len(ws) else b+0.22); en=min(en,st+1.0)
            L.append(f"Dialogue: 0,{ts(st)},{ts(en)},K,,0,0,0,,{{\\an5\\pos(540,{Y[k]})\\fad(30,30)}}"+tx.upper().strip(".,:;"))
    open(f"subs_{K}.ass","w",encoding="utf-8").write("\n".join(L)+"\n")
    print("PREP_OK",K,"total=%.2f"%TOTAL,"t0=",[round(x,2) for x in T0])
def final(K,url):
    r=sh(f'ffmpeg -y -v error -i mute_{K}.mp4 -c:v libvpx-vp9 -i ov_{K}.webm -i master_{K}.wav -filter_complex "[0:v][1:v]overlay=0:0:format=auto,ass=subs_{K}.ass[v]" -map "[v]" -map 2:a -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart -shortest final_{K}.mp4')
    if r.returncode: print("FFMPEG_ERR",r.stderr[-800:]); return
    p=sh(f"ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,width,height,sample_rate,channels -of csv=p=0 final_{K}.mp4").stdout.replace("\n"," ")
    raw=subprocess.run(["ffmpeg","-v","error","-i",f"final_{K}.mp4","-vf","fps=15,scale=96:-2,format=gray","-f","rawvideo","-"],capture_output=True).stdout
    H=170;fs=96*H;nf=len(raw)//fs;a=np.frombuffer(raw[:nf*fs],dtype=np.uint8).reshape(nf,H,96).astype(np.int16);d=np.abs(np.diff(a,axis=0)).mean(axis=(1,2))
    b=subprocess.run(["ffmpeg","-v","error","-i",f"final_{K}.mp4","-vf","fps=2,crop=1080:400:0:1080,format=gray","-f","rawvideo","-"],capture_output=True).stdout
    g=np.frombuffer(b,dtype=np.uint8).reshape(-1,400,1080);whs=(g>235).sum(axis=(1,2))
    print("VERIF",K,p,"| motion mean %.2f p10 %.2f"%(d.mean(),np.percentile(d,10)),"| subs %d/%d frames"%((whs>400).sum(),len(whs)))
    print(sh(f"curl -s -o /dev/null -w 'PUT %{{http_code}}' -X PUT -H 'Content-Type: video/mp4' --data-binary @final_{K}.mp4 '{url}'").stdout)
if __name__=="__main__":
    (prep if sys.argv[1]=="prep" else lambda K,u: final(K,u))(*sys.argv[2:])
