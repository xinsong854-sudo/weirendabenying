#!/usr/bin/env python3
"""后台文件监听：发现新请求 → 生成 GIF → 存到 /public/"""

import os, sys, io, uuid, json, time, base64, traceback
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw

PUBLIC = "/public/geo-mosaic"; REQUEST_DIR = os.path.join(PUBLIC, "requests")
os.makedirs(REQUEST_DIR, exist_ok=True)

def make_pieces(img, n, extra, spread, sm, alpha):
    w, h = img.size; px = np.array(img, dtype=np.float64)
    gray = np.mean(px[:,:,:3], axis=2)
    g = max(6, int((w*h/n)**0.5))
    pts = []
    for y in range(0,h,g):
        for x in range(0,w,g):
            pts.append([x+(np.random.random()-.5)*g*.6, y+(np.random.random()-.5)*g*.6])
    import scipy.ndimage as nd
    b = nd.uniform_filter(gray,size=g)
    v = nd.uniform_filter((gray-b)**2,size=g)
    vf = v.flatten(); vf /= vf.max()+1e-8
    rm = max(0,n-len(pts))
    if rm>0:
        idx = np.random.choice(len(vf),size=min(rm*2,len(vf)),replace=False,p=vf/vf.sum())
        for i in idx: pts.append([i%w,i//w])
    pts = np.clip(np.array(pts,dtype=np.float64),0,[w-1,h-1])
    crn = np.array([[0,0],[w-1,0],[0,h-1],[w-1,h-1]],dtype=np.float64)
    pts = np.unique(np.vstack([pts,crn]),axis=0)
    tri = Delaunay(pts) if len(pts)>=3 else None
    ps = []; cell = max(w,h)/max(1,len(pts)**.5)
    if tri:
        for s in tri.simplices:
            tp = pts[s]; cx,cy = tp.mean(axis=0)
            sx,sy = int(np.clip(cx,0,w-1)),int(np.clip(cy,0,h-1))
            r,g,b,_ = px[sy,sx]; c=(int(r),int(g),int(b),int(alpha*255))
            ps.append({'t':'tri','cx':cx,'cy':cy,'sx':w*.5+(np.random.random()-.5)*w*spread,
                       'sy':h*.5+(np.random.random()-.5)*h*spread,
                       'pts':tp.tolist(),'c':c,'r':(np.random.random()-.5)*np.pi*2,
                       'd':np.random.random()*600})
    for _ in range(extra):
        cx=np.random.random()*w;cy=np.random.random()*h
        sx,sy=int(np.clip(cx,0,w-1)),int(np.clip(cy,0,h-1))
        r,g,b,_ = px[sy,sx]; c=(int(r),int(g),int(b),int(alpha*255))
        sz=cell*sm*(.5+np.random.random())
        sxo=w*.5+(np.random.random()-.5)*w*spread
        syo=h*.5+(np.random.random()-.5)*h*spread
        rot=(np.random.random()-.5)*np.pi*2; dly=np.random.random()*600
        if np.random.random()<.6:
            ps.append({'t':'diamond','cx':cx,'cy':cy,'sx':sxo,'sy':syo,
                       'pts':[[cx,cy-sz],[cx+sz,cy],[cx,cy+sz],[cx-sz,cy]],'c':c,'r':rot,'d':dly})
        else:
            ps.append({'t':'circle','cx':cx,'cy':cy,'sx':sxo,'sy':syo,'r':sz,'c':c,'rot':rot,'d':dly})
    np.random.shuffle(ps); return ps

def frame(pieces, w, h, elapsed, dur):
    img = Image.new("RGBA",(w,h),(0,0,0,0)); draw = ImageDraw.Draw(img)
    for p in pieces:
        t=0
        if elapsed>p['d']:
            raw=min(1.,(elapsed-p['d'])/(dur*.4)); t=1-(1-raw)**3
        if t<=0: continue
        cx=p['cx']+(p['sx']-p['cx'])*(1-t); cy=p['cy']+(p['sy']-p['cy'])*(1-t)
        rot=(p.get('r',0) if p['t']=='circle' else p['r'])*(1-t)
        cs,sn=np.cos(rot),np.sin(rot)
        try:
            if p['t']=='circle':
                r=p['r']; draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=p['c'])
            else:
                tf=[(cx+(pt[0]-p['cx'])*cs-(pt[1]-p['cy'])*sn,
                     cy+(pt[0]-p['cx'])*sn+(pt[1]-p['cy'])*cs) for pt in p['pts']]
                draw.polygon(tf,fill=p['c'])
        except: pass
    return img

def process_request(req_path):
    try:
        with open(req_path) as f: data = json.load(f)
        img_data = base64.b64decode(data['image'])
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        M = 500
        if img.size[0] > M or img.size[1] > M:
            r = M / max(img.size); img = img.resize((int(img.size[0]*r), int(img.size[1]*r)), Image.LANCZOS)
        w, h = img.size

        pieces = make_pieces(img, data.get('points',800), data.get('extra',400),
                            data.get('spread',1.2), data.get('size',1.0), data.get('alpha',0.35))
        fps = data.get('fps',12); dur = data.get('duration',2.5)
        total = int(dur * fps); dur_ms = dur * 1000
        frames = [frame(pieces, w, h, (i/total)*dur_ms, dur_ms) for i in range(total)]

        gid = uuid.uuid4().hex[:8]
        out = os.path.join(PUBLIC, f"m_{gid}.gif")
        frames[0].save(out, save_all=True, append_images=frames[1:],
                       duration=int(1000/fps), loop=0, disposal=2, transparency=0, optimize=False)

        # 写结果
        prefix = os.environ.get("PUBLIC_URL_PREFIX","")
        result = {"ok":True, "url":f"{prefix}/geo-mosaic/m_{gid}.gif",
                  "pieces":len(pieces), "frames":total}
        with open(req_path.replace(".json","_done.json"),"w") as f: json.dump(result,f)
        os.rename(req_path, req_path+".processed")
        print(f"✅ {len(pieces)} pieces → {out}")
    except Exception as e:
        traceback.print_exc()
        with open(req_path.replace(".json","_done.json"),"w") as f:
            json.dump({"ok":False,"error":str(e)},f)

if __name__ == "__main__":
    print("👀 监听请求目录:", REQUEST_DIR)
    while True:
        for fname in sorted(os.listdir(REQUEST_DIR)):
            if fname.endswith(".json") and not fname.endswith("_done.json") and ".processed" not in fname:
                process_request(os.path.join(REQUEST_DIR, fname))
        time.sleep(1)
