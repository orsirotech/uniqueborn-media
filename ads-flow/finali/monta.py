import subprocess, os
B="/home/user/uniqueborn-media/ads-flow"; S="/tmp/claude-0/-home-user/f40f84a0-4dc5-5154-98c9-20a39ddc6568/scratchpad"
FONTS=S+"/v2/fonts"; W=S+"/montaggio"
ADS={
 "morag":(["morag-1-q","morag-2","morag-3-q","morag-4"],"Quando in Scozia trovi traffico.",[
  (0,0.0,3.8,"Signora mucca, per cortesia...\\Nci lascia passare?"),
  (1,0.0,3.6,"Non si sposta finché non ha\\Nla sua mela, amico!"),
  (1,4.3,5.2,"...Eh?"),
  (2,0.0,2.5,"Dice che si sposta solo per una mela!"),
  (2,2.6,4.8,"Ce l'ho io!"),
  (3,2.2,6.6,"A quanto pare Morag viene con noi.")]),
 "cartolina":(["cartolina-1-q","cartolina-2","cartolina-3","cartolina-4"],"Lo aveva promesso nel 1987.",[
  (0,0.0,1.8,"Me l'aveva promesso."),
  (1,0.0,2.3,"Senza tuo papà non ci vado."),
  (1,2.4,5.0,"Viene anche lui, mamma. È qui."),
  (2,0.0,3.2,"Gino... siamo tornati."),
  (3,0.0,1.6,"Piangi?"),
  (3,1.8,5.5,"No, no. È il vento.")]),
 "posto23":(["posto23-1","posto23-2-q","posto23-3","posto23-4"],"Su questo pullman manca una persona.",[
  (0,0.0,3.0,"Ma quel posto vuoto, di chi è?"),
  (1,0.0,5.4,"Quel posto?\\NÈ per te che stai guardando."),
  (2,0.0,1.4,"Dai, siediti qui!"),
  (2,4.5,5.4,"Biscotto?"),
  (3,0.0,3.4,"Prossima fermata: Isola di Skye!")]),
}
def t(x):
  h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h}:{m:02d}:{s:05.2f}"
for ad,(clips,hook,subs) in ADS.items():
  durs=[float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{B}/clip/{c}.mp4"]).strip()) for c in clips]
  off=[sum(durs[:i]) for i in range(4)]
  ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Outfit SemiBold,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,3,18,0,2,90,90,430,1
Style: Hook,Outfit SemiBold,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB0000000,0,0,0,0,100,100,0,0,3,24,0,8,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{t(0.15)},{t(2.9)},Hook,,0,0,0,,{{\\fad(150,250)}}{hook}
"""
  for ci,a,b,txt in subs:
    ass+=f"Dialogue: 0,{t(off[ci]+a)},{t(min(off[ci]+b,off[ci]+durs[ci]-0.05))},Sub,,0,0,0,,{{\\fad(80,80)}}{txt}\n"
  open(f"{W}/{ad}.ass","w").write(ass)
  inp=[]; fc=""
  for i,c in enumerate(clips):
    inp+=["-i",f"{B}/clip/{c}.mp4"]
    fc+=f"[{i}:v]scale=1080:1920:flags=lanczos,fps=25,setsar=1,format=yuv420p[v{i}];[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];"
  inp+=["-loop","1","-t","3","-framerate","25","-i",f"{B}/endcard/endcard-{ad}.png","-f","lavfi","-t","3","-i","anullsrc=r=48000:cl=stereo"]
  fc+="[4:v]scale=1080:1920,setsar=1,format=yuv420p,fade=t=in:st=0:d=0.3[v4];"
  fc+="".join(f"[v{i}][a{i}]" for i in range(4))+"[v4][5:a]concat=n=5:v=1:a=1[cv][ca];"
  fc+=f"[cv]ass={W}/{ad}.ass:fontsdir={FONTS}[ov];[ca]loudnorm=I=-14:TP=-1.5:LRA=11[oa]"
  out=f"{B}/finali/uniqueborn-ad-{ad}.mp4"
  subprocess.run(["ffmpeg","-y","-v","error",*inp,"-filter_complex",fc,"-map","[ov]","-map","[oa]","-c:v","libx264","-preset","slow","-crf","19","-profile:v","high","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",out],check=True)
  print(ad, subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size","-of","csv=p=0",out]).decode().strip())
