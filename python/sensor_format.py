# -*- coding: utf-8 -*-
# 假定当前图片为全幅拍摄，在图片中画出apsc和m43传感器的尺寸矩形框

import os
import sys
from PIL import Image, ImageDraw

width=10  # 矩形边框线宽（像素）

apsc_rect_scale=2/3
apsc_color=(255, 0, 0)
m43_color=(0, 0, 255)

def draw_center_rect(input_path, output_path=None):
    """
    在图片中心画一个矩形：
    - 矩形宽度 = 原图宽度 * rect_scale
    - 矩形高度 = 原图高度 * rect_scale
    - 默认 rect_scale = 2/3
    - color 为矩形边框颜色，(R, G, B)
    - width 为矩形边框线宽（像素）
    """
    # 打开图片
    img = Image.open(input_path).convert("RGB")
    w, h = img.size

    # apsc

    # 计算矩形尺寸（原图的 2/3）
    rect_w = int(w * apsc_rect_scale)
    rect_h = int(h * apsc_rect_scale)

    # 计算矩形左上和右下坐标，保证在画面中心
    left   = (w - rect_w) // 2
    top    = (h - rect_h) // 2
    right  = left + rect_w
    bottom = top + rect_h

    # 在图像上画矩形（只画边框，不填充）
    draw = ImageDraw.Draw(img)
    draw.rectangle([left, top, right, bottom], outline=apsc_color, width=width)

    # m43

    # 计算矩形尺寸
    rect_w = int(w * 17.3 / 36)
    rect_h = int(h * 13 / 24)

    # 计算矩形左上和右下坐标，保证在画面中心
    left   = (w - rect_w) // 2
    top    = (h - rect_h) // 2
    right  = left + rect_w
    bottom = top + rect_h

    # 在图像上画矩形（只画边框，不填充）
    draw = ImageDraw.Draw(img)
    draw.rectangle([left, top, right, bottom], outline=m43_color, width=width)

    # 输出路径
    if output_path is None:
        base_dir = os.path.dirname(input_path)
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(base_dir, f"{base_name}_rect{ext}")

    img.save(output_path)
    print(f"已生成带中心矩形的图片：{output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python sensor_format.py 输入图片路径 [输出图片路径]")
        print("示例：python sensor_format.py input.jpg output.jpg")
        sys.exit(1)

    input_img = sys.argv[1]
    out_img = sys.argv[2] if len(sys.argv) >= 3 else None

    draw_center_rect(input_img, out_img)
