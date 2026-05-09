#!/usr/bin/env python3
"""一站式服务：浏览器打开 → 上传图片 → 自动生成 GIF"""

import os, sys, io, uuid, json, traceback
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw
from http.server import HTTPServer, BaseHTTPRequestHandler

PUBLIC = "/public/geo-mosaic"; os.makedirs(PUBLIC, exist_ok=True)

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

INDEX = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>几何拼装</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Noto+Sans+SC:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#06060e;--surf:rgba(16,16,30,.9);--border:rgba(255,255,255,.07);--grn:#4ade80;--blu:#60a5fa;--amb:#fbbf24;--txt:#e2e8f0;--dim:#64748b;--r:10px}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--txt);min-height:100vh;
background-image:radial-gradient(ellipse at 20% 20%,rgba(74,222,128,.04) 0%,transparent 50%),radial-gradient(ellipse at 80% 70%,rgba(96,165,250,.04) 0%,transparent 50%)}}
.app{{max-width:900px;margin:0 auto;padding:12px}}
h1{{font-family:Orbitron;font-size:clamp(1rem,3vw,1.3em);text-align:center;font-weight:800;
background:linear-gradient(135deg,var(--grn),var(--blu),var(--amb));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:8px 0 2px;letter-spacing:.04em}}
.sub{{text-align:center;color:var(--dim);font-size:.75em;margin-bottom:10px}}
.u{{display:block;border:2px dashed rgba(255,255,255,.1);border-radius:var(--r);padding:20px;text-align:center;cursor:pointer;background:var(--surf);backdrop-filter:blur(12px);margin-bottom:8px;transition:.25s}}
.u:hover{{border-color:var(--grn);background:rgba(74,222,128,.04)}}
.u .ico{{font-size:1.8em;display:block;margin-bottom:4px}}
input[type=file]{{display:none}}
.ctls{{background:var(--surf);border:1px solid var(--border);border-radius:var(--r);padding:10px;margin-bottom:6px;backdrop-filter:blur(12px);display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;align-items:end}}
.ctl{{display:flex;flex-direction:column;gap:2px}}
.ctl label{{font-size:.6em;text-transform:uppercase;letter-spacing:.1em;color:var(--dim)}}
.ctl .v{{font-size:.6em;color:var(--grn);font-family:Orbitron}}
input[type=range]{{-webkit-appearance:none;width:100%;height:3px;border-radius:2px;background:rgba(255,255,255,.08);cursor:pointer}}
input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:var(--grn);border:2px solid var(--bg)}}
.btn{{padding:7px 10px;border-radius:6px;border:none;font-family:Orbitron;font-size:.65em;font-weight:600;letter-spacing:.06em;cursor:pointer;text-transform:uppercase;width:100%}}
.btn-go{{background:linear-gradient(135deg,var(--grn),#22c55e);color:#052e16}}
.btn-go:hover:not(:disabled){{transform:translateY(-1px)}}
.btn-go:disabled{{opacity:.3;cursor:not-allowed}}
.st{{text-align:center;font-size:.65em;color:var(--dim);margin:6px 0;min-height:1em}}
.r{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:6px}}
.card{{background:var(--surf);border:1px solid var(--border);border-radius:var(--r);padding:6px;backdrop-filter:blur(12px);text-align:center}}
.card h3{{font-family:Orbitron;font-size:.6em;letter-spacing:.1em;color:var(--dim);margin-bottom:4px}}
canvas,img{{max-width:100%;max-height:45vh;border-radius:4px;display:block;margin:0 auto;background:#000}}
@media(max-width:600px){{.ctls{{grid-template-columns:repeat(2,1fr)}}.r{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="app">
<h1>◆ GEOMETRIC MOSAIC</h1>
<p class="sub">上传图片 → 自动生成碎片拼装 GIF</p>
<label for="fi" class="u" id="ua"><span class="ico">📷</span>点击上传图片 (JPG/PNG)</label>
<input type="file" id="fi" accept="image/*">
<div class="ctls">
<div class="ctl"><label>三角密度</label><input type="range" id="pts" min="200" max="3000" value="800"><span class="v" id="ptsV">800</span></div>
<div class="ctl"><label>额外形状</label><input type="range" id="ext" min="100" max="1000" value="400"><span class="v" id="extV">400</span></div>
<div class="ctl"><label>元素大小</label><input type="range" id="sz" min="50" max="200" value="100"><span class="v" id="szV">100%</span></div>
<div class="ctl"><label>飞行范围</label><input type="range" id="spr" min="50" max="150" value="120"><span class="v" id="sprV">120%</span></div>
<button class="btn btn-go" id="go" disabled>⚡ 生成 GIF</button>
</div>
<div class="st" id="st">等待上传…</div>
<div class="r">
<div class="card"><h3>原图</h3><canvas id="sC"></canvas></div>
<div class="card"><h3>拼装 GIF</h3><img id="rI" style="display:none" alt="loading..."><canvas id="rC"></canvas></div>
</div>
</div>
<script>
const sC=document.getElementById('sC'),rC=document.getElementById('rC'),rI=document.getElementById('rI');
const sX=sC.getContext('2d'),rX=rC.getContext('2d');
const st=document.getElementById('st'),go=document.getElementById('go');
let imgData=null;
['pts','sz','spr','ext'].forEach(id=>{document.getElementById(id).oninput=e=>document.getElementById(id+'V').textContent=e.target.value})
document.getElementById('fi').onchange=e=>{{const f=e.target.files[0];if(!f)return;const r=new FileReader();r.onload=ev=>{{const img=new Image();img.onload=()=>{{const M=400;let w=img.width,h=img.height;if(w>M||h>M){{const rt=M/Math.max(w,h);w=Math.round(w*rt);h=Math.round(h*rt)}}sC.width=w;sC.height=h;rC.width=w;rC.height=h;sX.drawImage(img,0,0,w,h);imgData=sX.getImageData(0,0,w,h);document.getElementById('ua').innerHTML='<span class=ico>✅</span>已加载';go.disabled=false;st.textContent='点击生成'}}}};img.src=ev.target.result}};r.readAsDataURL(f)}}
// 前端轻量动画预览
function preview(){{
  if(!imgData)return;
  const w=sC.width,h=sC.height,d=imgData.data;
  const g=Math.sqrt(w*h/(parseInt(document.getElementById('pts').value)*1.5));
  const cols=Math.ceil(w/g),rows=Math.ceil(h/g);
  const ps=[];
  for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){{
    for(let k=0;k<2;k++){{
      const cx=c*g+g*.5+(Math.random()-.5)*g*.6,cy=r*g+g*.5+(Math.random()-.5)*g*.6;
      if(cx<0||cx>=w||cy<0||cy>=h)continue;
      const sz=g*(.8+Math.random()*.6);
      const sx=Math.min(w-1,Math.max(0,Math.round(cx))),sy=Math.min(h-1,Math.max(0,Math.round(cy)));
      const pi=(sy*w+sx)*4;
      const col=`rgba(${{d[pi]}}, ${{d[pi+1]}}, ${{d[pi+2]}}, 0.4)`;
      const rot=(Math.random()-.5)*Math.PI;
      const pts=[];for(let v=0;v<3;v++){{const a=v*Math.PI*2/3+Math.random()*.5;pts.push({{x:cx+Math.cos(a)*sz,y:cy+Math.sin(a)*sz}})}};
      ps.push({{tx:cx,ty:cy,x:w*.5+(Math.random()-.5)*w*1.2,y:h*.5+(Math.random()-.5)*h*1.2,pts,color:col,rot,delay:Math.random()*600}});
    }}
  }}
  for(let i=ps.length-1;i>0;i--){{[ps[i],ps[i-1]]=[ps[i-1],ps[i]]}};
  rX.fillStyle='#06060e';rX.fillRect(0,0,w,h);
  let start=null,idx=0;const total=ps.length;
  function loop(ts){{
    if(!start)start=ts;const dur=3000;
    rX.clearRect(0,0,w,h);
    for(let i=0;i<Math.min(idx+20,total);i++){{
      let t=0;const elapsed=ts-start;
      if(elapsed>ps[i].delay){{const raw=Math.min(1,(elapsed-ps[i].delay)/(dur*.5));t=1-Math.pow(1-raw,3)}}
      rX.save();const cx=ps[i].tx+(ps[i].x-ps[i].tx)*(1-t),cy=ps[i].ty+(ps[i].y-ps[i].ty)*(1-t);
      rX.translate(cx,cy);rX.rotate(ps[i].rot*(1-t));rX.fillStyle=ps[i].color;rX.beginPath();
      rX.moveTo(ps[i].pts[0].x-ps[i].tx,ps[i].pts[0].y-ps[i].ty);rX.lineTo(ps[i].pts[1].x-ps[i].tx,ps[i].pts[1].y-ps[i].ty);rX.lineTo(ps[i].pts[2].x-ps[i].tx,ps[i].pts[2].y-ps[i].ty);rX.closePath();rX.fill();rX.restore();
    }}
    if(elapsed>ps[Math.min(idx,total-1)].delay)idx+=20;
    if(idx<total)requestAnimationFrame(loop);
    else{{rX.fillStyle='#06060e';rX.fillRect(0,0,w,h);for(const p of ps){{rX.save();rX.translate(p.tx,p.ty);rX.scale(1.02,1.02);rX.fillStyle=p.color;rX.beginPath();rX.moveTo(p.pts[0].x-p.tx,p.pts[0].y-p.ty);rX.lineTo(p.pts[1].x-p.tx,p.pts[1].y-p.ty);rX.lineTo(p.pts[2].x-p.tx,p.pts[2].y-p.ty);rX.closePath();rX.fill();rX.restore()}}}}}
  }}
  requestAnimationFrame(loop);
}}
go.onclick=()=>{{st.textContent='⏳ 生成中（约10秒）…';go.disabled=true;
const form=new FormData();form.append('image',sC.toDataURL('image/png'));
form.append('points',document.getElementById('pts').value);
form.append('extra',document.getElementById('ext').value);
form.append('spread',parseInt(document.getElementById('spr').value)/100);
form.append('size',parseInt(document.getElementById('sz').value)/100);
form.append('alpha',0.35);form.append('fps',12);form.append('duration',2.5);
fetch('/generate',{{method:'POST',body:form}}).then(r=>r.text()).then(html=>{{
  const m=html.match(/src="([^"]+)"/);
  if(m){{rI.src=m[1]+'?t='+Date.now();rI.style.display='';rC.style.display='none';st.textContent='✅ 完成！'}}
  else{{st.textContent='❌ 失败，请重试'}}
  go.disabled=false;
}}).catch(e=>{{st.textContent='❌ 服务未启动: python3 server.py';go.disabled=false}});
preview();
}};
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
            return
        html = INDEX
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        try:
            content_type = self.headers.get("Content-Type", "")
            from urllib.parse import parse_qs
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            boundary = content_type.split("boundary=")[1] if "boundary=" in content_type else ""
            # Parse multipart manually
            parts = body.split(("--" + boundary).encode())
            img_bytes = None; params = {}
            for part in parts:
                if b"Content-Disposition" not in part: continue
                hdr, _, data = part.partition(b"\r\n\r\n")
                data = data.rstrip(b"\r\n--")
                name = ""
                for line in hdr.decode(errors="ignore").split("\r\n"):
                    if "name=" in line:
                        name = line.split('name="')[1].split('"')[0]
                if name == "image" and data:
                    # Remove data URL prefix
                    if b"base64," in data:
                        img_bytes = base64.b64decode(data.split(b"base64,")[1])
                    else:
                        img_bytes = data
                elif name and data:
                    try: params[name] = float(data.decode()) if b'.' in data else int(data)
                    except: pass

            if not img_bytes:
                self.send_error(400, "No image"); return

            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
            M = 500
            if img.size[0] > M or img.size[1] > M:
                r = M / max(img.size)
                img = img.resize((int(img.size[0]*r), int(img.size[1]*r)), Image.LANCZOS)
            w, h = img.size

            pts = int(params.get('points', 800))
            ext = int(params.get('extra', 400))
            sprd = float(params.get('spread', 1.2))
            sm = float(params.get('size', 1.0))
            alpha = float(params.get('alpha', 0.35))
            fps = int(params.get('fps', 12))
            dur = float(params.get('duration', 2.5))

            pieces = make_pieces(img, pts, ext, sprd, sm, alpha)
            total_frames = int(dur * fps)
            frames = []
            for i in range(total_frames):
                elapsed = (i / total_frames) * dur * 1000
                frames.append(frame(pieces, w, h, elapsed, dur * 1000))

            gid = uuid.uuid4().hex[:8]
            out_path = os.path.join(PUBLIC, f"m_{gid}.gif")
            frames[0].save(out_path, save_all=True, append_images=frames[1:],
                           duration=int(1000/fps), loop=0, disposal=2, transparency=0, optimize=False)

            prefix = os.environ.get("PUBLIC_URL_PREFIX", "")
            url = f"{prefix}/geo-mosaic/m_{gid}.gif"
            html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>完成</title>
<style>body{{font-family:sans-serif;background:#06060e;color:#e2e8f0;text-align:center;padding:30px}}
img{{max-width:90vw;max-height:65vh;border-radius:10px;box-shadow:0 8px 40px rgba(0,0,0,.6)}}
.stats{{color:#64748b;margin:12px 0}}a{{display:inline-block;padding:10px 24px;background:#4ade80;color:#052e16;border-radius:6px;text-decoration:none;font-weight:bold;margin-top:10px}}
</style></head><body><h2>✅ 生成完成</h2><div class=stats>{len(pieces)} 碎片 · {total_frames} 帧</div>
<img src="{url}"><br><a href="{url}" download>⬇ 下载 GIF</a></body></html>"""

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

    def log_message(self, fmt, *args): pass

PORT = int(os.environ.get("PORT", 8765))
import base64
if __name__ == "__main__":
    print(f"🚀 打开浏览器访问: http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
