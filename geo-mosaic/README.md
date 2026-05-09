# 图片几何马赛克工具

将图片转换成用几何形状（三角形）一个个拼成的效果。

## 原理

1. **边缘检测** - 使用 Canny 算法检测图片边缘
2. **关键点采样** - 在边缘密集处采样更多点
3. **Delaunay 三角剖分** - 将点集分割成不重叠的三角形
4. **颜色填充** - 用每个三角形中心点的原始颜色填充

## 使用方法

```bash
# 安装依赖
pip install numpy opencv-python scipy Pillow

# 运行
python geo_mosaic.py input.jpg output.png --num-points 5000 --blur 5
```

## 参数说明

- `--num-points`: 采样点数量（越多越精细，默认 3000）
- `--blur`: 高斯模糊程度（减少噪点，默认 5）
