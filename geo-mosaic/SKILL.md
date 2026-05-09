---
name: geo-mosaic
description: 几何拼装工具 — 将图片拆解为三角形、菱形等几何碎片，碎片从画面外飞入拼合成原图，支持实时预览和 GIF 导出。适用于创意展示、Logo 动画、海报生成等场景。
---

# 几何拼装工具 (Geo Mosaic)

## 概述

将任意图片转换为几何碎片拼装动画。碎片从画面外飞入，经过旋转、缩放、位移，最终精确拼合成原图。

支持两种模式：
- **纯浏览器模式**：上传即用，gif.js 编码导出 GIF
- **Python 后端模式**：真正的 Delaunay 三角剖分，高质量渲染

## 核心文件

| 文件 | 说明 |
|------|------|
| `index.html` | 纯前端完整版，公网 CDN 可访问 |
| `server.py` | Python 前后端一体服务 (localhost:5173) |
| `geo_mosaic.py` | Python CLI 工具，直接生成 GIF |
| `watcher.py` | 文件监听模式，自动处理请求队列 |

## 技术要点

### 碎片生成算法

```javascript
// 核心思路：
// 1. 网格采样 → 每个格点取原图颜色
// 2. 每个格子生成多个碎片（三角+菱形混搭）
// 3. 碎片起点在画布外 5x 处
// 4. 每个碎片有随机延迟(300-1100ms) + 随机旋转
// 5. easeOutCubic 缓动飞入到位

function build(num, ov, spread) {
  const g = Math.min(w, h) / Math.ceil(Math.sqrt(num / 6));
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++)
      for (let k = 0; k < 6; k++) {
        // 三角形或菱形，随机形状
        // 颜色 = rgba(原图中心像素, alpha)
        // 起点 = 画布中心 ± 5x 画布宽度
        // delay = 300 + random*800 ms
      }
}
```

### 关键参数

- **碎片数**：500~80000，直接影响密度和性能
- **重叠度**：rgba alpha 值 (15%~55%)，控制碎片透明度
- **飞行范围**：控制碎片起点离画布中心的距离
- **GIF 尺寸/质量/帧率**：可调节导出质量和文件大小

### 避坑记录

1. **gif.js CORS 问题**：worker 脚本跨域被拦 → fetch worker 代码转 Blob URL
2. **copy:false 导致所有帧相同**：gif.js 延迟读取 canvas，需用 copy:true
3. **碎片延迟为 0 导致直接出现**：设最小延迟 300ms 确保飞入效果
4. **GIF 透明底不生效**：gif.js 对 alpha 支持有限，最终用黑底
5. **编码卡 94%**：workers:0 模式在部分版本有 bug，需内联 worker

### 性能建议

- 纯浏览器模式碎片建议 ≤ 8000
- 更高密度用 Python 后端（`server.py` on port 5173）
- GIF 导出建议 150-250px，8fps，质量 20
- 超高碎片数预览会比较卡，直接点下载 GIF 即可
