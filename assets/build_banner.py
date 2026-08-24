import re
from PIL import Image, ImageDraw, ImageFont

SS=4; FIG="/Users/harigovind/Desktop/Claude/results/figures"
GROUND_TOP=(17,26,23); GROUND_BOT=(10,16,14)
SAGE=(127,168,134); RULE=(52,74,60); BONE=(237,231,218); MUTED=(136,155,146)
FUTURA="/System/Library/Fonts/Supplemental/Futura.ttc"
AVENIR="/System/Library/Fonts/Avenir Next.ttc"
MENLO ="/System/Library/Fonts/Menlo.ttc"
SPECS=[("gyroid_p35","0.35"),("gyroid_p60","0.60"),("gyroid_p85","0.85")]

EYEBROW = "B.TECH · AI/ML"
NAME    = "HARIGOVIND R"
TAGLINE = "Physics-informed ML for bone tissue engineering"
EMAIL   = "hg155158@gmail.com"

def parse(fn):
    s=open(f"{FIG}/{fn}.svg").read(); out=[]
    for d in re.findall(r'<path d="([^"]+)"',s):
        p=[tuple(map(float,m)) for m in re.findall(r'([-\d.]+)\s+([-\d.]+)',d)]
        if len(p)>=3: out.append(p)
    return out
def mask(polys,size):
    m=Image.new("L",(size,size),0); d=ImageDraw.Draw(m); k=size/300.0
    for p in polys: d.polygon([(x*k,y*k) for x,y in p],fill=255)
    return m
def track(d,xy,t,f,fill,tr=0):
    x,y=xy
    for ch in t: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+tr
def twid(d,t,f,tr=0): return sum(d.textlength(c,font=f)+tr for c in t)-tr

def build(W,H,*,name_px,cell,gap,pad,x0,y_base,y_cell_top,eb_px,tag_px,lab_px,mail_px):
    sw,sh=W*SS,H*SS
    g=Image.new("RGB",(1,sh))
    for y in range(sh):
        t=y/sh; g.putpixel((0,y),tuple(round(a+(b-a)*t) for a,b in zip(GROUND_TOP,GROUND_BOT)))
    img=g.resize((sw,sh)); d=ImageDraw.Draw(img); S=lambda v:int(v*SS)
    hair=max(1,S(0.75))

    cs=S(cell); gp=S(gap); total=cs*3+gp*2
    xs=sw-S(pad)-total; ytop=S(y_cell_top); yb=S(y_base)

    d.line([(S(x0),yb),(sw-S(pad),yb)],fill=RULE,width=hair)
    for i,(fn,lab) in enumerate(SPECS):
        cx=xs+i*(cs+gp); m=mask(parse(fn),cs)
        img.paste(Image.new("RGB",(cs,cs),SAGE),(cx,ytop),m)
        d.rectangle([cx,ytop,cx+cs,ytop+cs],outline=RULE,width=hair)
        d.line([(cx+cs//2,yb),(cx+cs//2,yb+S(6))],fill=RULE,width=hair)

    small=ImageFont.truetype(MENLO,S(lab_px),index=0)
    for i,(fn,lab) in enumerate(SPECS):
        cx=xs+i*(cs+gp); txt=f"P {lab}"
        w=twid(d,txt,small,S(1.2)); track(d,(cx+cs//2-w/2,yb+S(14)),txt,small,SAGE,S(1.2))

    eb  =ImageFont.truetype(MENLO ,S(eb_px),  index=0)
    nm  =ImageFont.truetype(FUTURA,S(name_px),index=0)
    tg  =ImageFont.truetype(AVENIR,S(tag_px), index=7)
    mail=ImageFont.truetype(MENLO ,S(mail_px),index=0)

    # stack upward from the rule so nothing crosses y=290 (LinkedIn avatar zone)
    y_mail = y_base - mail_px - 21
    y_tag  = y_mail - tag_px  - 16
    y_nm   = y_tag  - name_px - 18
    y_eb   = y_nm   - eb_px   - 20
    track(d,(S(x0),S(y_eb)),EYEBROW,eb,SAGE,S(2.4))
    track(d,(S(x0),S(y_nm)),NAME,nm,BONE,S(4.2))
    d.text((S(x0),S(y_tag)),TAGLINE,font=tg,fill=MUTED)
    track(d,(S(x0),S(y_mail)),EMAIL,mail,SAGE,S(0.6))
    print(f"  type block y: eyebrow {y_eb} name {y_nm} tag {y_tag} mail {y_mail}-{y_mail+mail_px} | rule {y_base}")
    return img.resize((W,H),Image.LANCZOS)

build(1584,396,name_px=60,cell=196,gap=32,pad=88,x0=96,
      y_base=300,y_cell_top=72,eb_px=14,tag_px=21,lab_px=13,mail_px=15
     ).save("linkedin-cover.png")
print("ok")
