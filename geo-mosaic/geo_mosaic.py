#!/usr/bin/env python3
"""
几何拼装动画工具 - 后端版

将图片拆解为 Delaunay 三角 + 随机几何碎片，
生成碎片从散落飞回拼合的 GIF 动画。
"""

import argparse
import sys
import time
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw


def load_image(path, max_dim=500):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    if w > max_dim or h > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    return img


def generate_pieces(img, num_points, num_extra, spread, size_mul, alpha):
    """生成混合几何碎片：Delaunay 三角 + 随机菱形/圆形"""
    w, h = img.size
    pixels = np.array(img, dtype=np.float64)
    gray = np.mean(pixels[:, :, :3], axis=2)

    # 自适应采样点（细节密集处点多）
    grid = max(8, int(np.sqrt(w * h / num_points)))
    pts = []
    for y in range(0, h, grid):
        for x in range(0, w, grid):
            pts.append([x + (np.random.random() - 0.5) * grid * 0.6,
                        y + (np.random.random() - 0.5) * grid * 0.6])

    # 边缘增强采样
    if len(pts) < num_points:
        var = cv2_blur((gray - cv2_blur(gray, grid)) ** 2, grid)
        var_flat = var.flatten()
        var_flat /= var_flat.max() + 1e-8
        extra = num_points - len(pts)
        idx = np.random.choice(len(var_flat), size=min(extra * 2, len(var_flat)),
                               replace=False, p=var_flat / var_flat.sum())
        for i in idx:
            py, px = divmod(i, w)
            pts.append([px, py])

    pts = np.array(pts, dtype=np.float64)
    pts = np.clip(pts, 0, [w - 1, h - 1])
    # 四角
    corners = np.array([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]], dtype=np.float64)
    pts = np.vstack([pts, corners])
    pts = np.unique(pts, axis=0)

    # Delaunay 三角剖分
    if len(pts) >= 3:
        tri = Delaunay(pts)
        simplices = tri.simplices
    else:
        simplices = np.array([])

    pieces = []
    cell = max(w, h) / max(1, np.sqrt(len(pts)))

    # Delaunay 三角形
    for s in simplices:
        tri_pts = pts[s]
        cx, cy = tri_pts.mean(axis=0)
        sx, sy = int(np.clip(cx, 0, w - 1)), int(np.clip(cy, 0, h - 1))
        r, g, b, _ = pixels[sy, sx]
        color = (int(r), int(g), int(b), int(alpha * 255))
        # 散落起点
        sx0 = w * 0.5 + (np.random.random() - 0.5) * w * spread
        sy0 = h * 0.5 + (np.random.random() - 0.5) * h * spread
        rot = (np.random.random() - 0.5) * np.pi * 2
        delay = np.random.random() * 600
        pieces.append({
            'type': 'tri',
            'cx': cx, 'cy': cy,
            'sx': sx0, 'sy': sy0,
            'pts': tri_pts.tolist(),
            'color': color,
            'rot': rot,
            'delay': delay,
            'size_mul': size_mul * (0.8 + np.random.random() * 0.4)
        })

    # 额外随机形状（菱形 + 圆形）
    for _ in range(num_extra):
        cx = np.random.random() * w
        cy = np.random.random() * h
        sx, sy = int(np.clip(cx, 0, w - 1)), int(np.clip(cy, 0, h - 1))
        r, g, b, _ = pixels[sy, sx]
        color = (int(r), int(g), int(b), int(alpha * 255))
        sz = cell * size_mul * (0.6 + np.random.random() * 1.2)
        sx0 = w * 0.5 + (np.random.random() - 0.5) * w * spread
        sy0 = h * 0.5 + (np.random.random() - 0.5) * h * spread
        rot = (np.random.random() - 0.5) * np.pi * 2
        delay = np.random.random() * 600

        if np.random.random() < 0.5:
            # 菱形
            pts_l = [[cx, cy - sz], [cx + sz, cy], [cx, cy + sz], [cx - sz, cy]]
            pieces.append({
                'type': 'diamond', 'cx': cx, 'cy': cy,
                'sx': sx0, 'sy': sy0, 'pts': pts_l,
                'color': color, 'rot': rot, 'delay': delay,
                'size_mul': size_mul
            })
        else:
            pieces.append({
                'type': 'circle', 'cx': cx, 'cy': cy,
                'sx': sx0, 'sy': sy0, 'radius': sz,
                'color': color, 'rot': rot, 'delay': delay,
                'size_mul': size_mul
            })

    # 随机打乱
    np.random.shuffle(pieces)
    return pieces


def draw_piece(draw, p, progress, w, h):
    """progress: 0=散落, 1=到位"""
    t = progress
    cx = p['cx'] + (p['sx'] - p['cx']) * (1 - t)
    cy = p['cy'] + (p['sy'] - p['cy']) * (1 - t)
    rot = p['rot'] * (1 - t)

    # 简易仿射变换（旋转 + 平移）
    cos_r = np.cos(rot)
    sin_r = np.sin(rot)

    pts_transformed = []
    if p['type'] == 'circle':
        r = p['radius']
        # 圆形：画椭圆近似旋转
        pts_transformed = [(cx - r, cy - r, cx + r, cy + r)]
    else:
        for pt in p['pts']:
            px = pt[0] - p['cx']
            py = pt[1] - p['cy']
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            pts_transformed.append((cx + rx, cy + ry))

    try:
        if p['type'] == 'tri':
            draw.polygon(pts_transformed, fill=p['color'])
        elif p['type'] == 'diamond':
            draw.polygon(pts_transformed, fill=p['color'])
        elif p['type'] == 'circle':
            for (x0, y0, x1, y1) in pts_transformed:
                draw.ellipse([x0, y0, x1, y1], fill=p['color'])
    except Exception:
        pass


def render_frame(pieces, w, h, elapsed, duration):
    """渲染单帧：所有碎片从散落位飞到目标位"""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for p in pieces:
        t = 0
        if elapsed > p['delay']:
            raw = min(1.0, (elapsed - p['delay']) / (duration * 0.5))
            t = 1 - (1 - raw) ** 3  # easeOutCubic
        if t >= 0:
            draw_piece(draw, p, t, w, h)

    return img


def cv2_blur(arr, ksize):
    """简易 box blur，不依赖 cv2"""
    import scipy.ndimage as nd
    return nd.uniform_filter(arr, size=ksize)


def main():
    parser = argparse.ArgumentParser(description="几何拼装动画 - 输出 GIF")
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("-o", "--output", default="mosaic.gif", help="输出 GIF 路径")
    parser.add_argument("--points", type=int, default=800, help="Delaunay 采样点数")
    parser.add_argument("--extra", type=int, default=300, help="额外随机形状数")
    parser.add_argument("--spread", type=float, default=1.2, help="散落散布范围")
    parser.add_argument("--size", type=float, default=1.0, help="元素大小倍率")
    parser.add_argument("--alpha", type=float, default=0.35, help="碎片不透明度")
    parser.add_argument("--fps", type=int, default=15, help="GIF 帧率")
    parser.add_argument("--duration", type=float, default=2.5, help="动画时长(秒)")
    parser.add_argument("--max-dim", type=int, default=500, help="图片最大边长")
    args = parser.parse_args()

    print(f"📷 加载图片: {args.input}")
    img = load_image(args.input, args.max_dim)
    w, h = img.size
    print(f"   尺寸: {w}x{h}")

    print(f"🔍 生成碎片: {args.points} Delaunay + {args.extra} 随机…")
    pieces = generate_pieces(img, args.points, args.extra,
                             args.spread, args.size, args.alpha)
    print(f"   共 {len(pieces)} 个碎片")

    total_frames = int(args.duration * args.fps)
    duration_ms = args.duration * 1000

    print(f"🎨 渲染 {total_frames} 帧…")
    frames = []
    for i in range(total_frames):
        elapsed = (i / total_frames) * duration_ms
        frame = render_frame(pieces, w, h, elapsed, duration_ms)
        frames.append(frame)
        if (i + 1) % 10 == 0:
            print(f"   帧 {i + 1}/{total_frames}")

    print(f"💾 保存 GIF: {args.output}")
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / args.fps),
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False
    )
    print(f"✅ 完成 ({len(frames)} 帧, {args.fps}fps, {args.duration}s)")


if __name__ == "__main__":
    main()
