# -*- coding: utf-8 -*-
# 将图片裁剪为 4x4 网格后，保存每块为单独图片

import os
import sys
from PIL import Image

def split_image_16(input_path, output_dir=None):
    # 打开图片
    img = Image.open(input_path)
    width, height = img.size

    # 4x4 网格
    cols, rows = 4, 4

    # 计算每块的宽高（先用整除得到每块的整数像素大小）
    tile_w = width // cols
    tile_h = height // rows

    # 为了保证每块大小完全一致，有可能会丢掉边缘少量像素：
    # 这里从中间截出一个可以被 4x4 整除的区域
    crop_w = tile_w * cols
    crop_h = tile_h * rows

    offset_x = (width - crop_w) // 2
    offset_y = (height - crop_h) // 2

    # 从中心裁剪出整齐区域
    img_cropped = img.crop((
        offset_x,
        offset_y,
        offset_x + crop_w,
        offset_y + crop_h
    ))

    # 更新宽高为裁剪后的
    width, height = img_cropped.size
    tile_w = width // cols
    tile_h = height // rows

    # 输出目录
    if output_dir is None:
        base_dir = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.join(base_dir, f"{base_name}_tiles")
    os.makedirs(output_dir, exist_ok=True)

    # 平分裁切
    index = 0
    for r in range(rows):
        for c in range(cols):
            left = c * tile_w
            upper = r * tile_h
            right = left + tile_w
            lower = upper + tile_h

            tile = img_cropped.crop((left, upper, right, lower))

            # 保存文件名：原名_row_col.png
            out_name = f"{base_name}_r{r}_c{c}.png"
            out_path = os.path.join(output_dir, out_name)
            tile.save(out_path)
            index += 1

    print(f"共生成 {index} 张图片，保存在：{output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python split_image_16.py 输入图片路径 [输出目录]")
        print("示例：python split_image_16.py input.jpg out_dir")
        sys.exit(1)

    input_img = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) >= 3 else None

    split_image_16(input_img, out_dir)
