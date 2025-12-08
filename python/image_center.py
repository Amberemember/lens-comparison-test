# -*- coding: utf-8 -*-
# 将图片裁剪为 3x3 网格后，保存中心块为单独图片

import os
import sys
from PIL import Image

def save_center_tile(input_path, output_dir=None):
    # 打开图片
    img = Image.open(input_path)
    width, height = img.size

    # 确定每块的大小
    cols, rows = 3, 3

    # 先算每块的宽高（基于原图）
    tile_w = width // cols
    tile_h = height // rows

    # 从中间裁出一个可以被整除的区域，避免边缘多出来几像素
    crop_w = tile_w * cols
    crop_h = tile_h * rows

    offset_x = (width - crop_w) // 2
    offset_y = (height - crop_h) // 2

    # 得到规整后的画面
    img_cropped = img.crop((
        offset_x,
        offset_y,
        offset_x + crop_w,
        offset_y + crop_h
    ))

    # 更新为裁剪后尺寸
    width, height = img_cropped.size
    tile_w = width // cols
    tile_h = height // rows

    # 统一定义基本信息
    base_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # 输出目录
    if output_dir is None:
        output_dir = os.path.join(base_dir, f"{base_name}_center")
    os.makedirs(output_dir, exist_ok=True)

    # 只裁一块：位于画面最中心、大小为 tile_w * tile_h
    center_left = (width - tile_w) // 2
    center_upper = (height - tile_h) // 2
    center_right = center_left + tile_w
    center_lower = center_upper + tile_h

    center_tile = img_cropped.crop((center_left, center_upper,
                                    center_right, center_lower))

    center_name = f"{base_name}_center.png"
    center_path = os.path.join(output_dir, center_name)
    center_tile.save(center_path)

    print(f"已生成中心图片：{center_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python image_center.py 输入图片路径 [输出目录]")
        print("示例：python image_center.py input.jpg out_dir")
        sys.exit(1)

    input_img = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) >= 3 else None

    save_center_tile(input_img, out_dir)
