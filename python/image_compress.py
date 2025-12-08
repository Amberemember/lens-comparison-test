# -*- coding: utf-8 -*-
# 批量压缩图片到指定最大宽度，并另存为 webp 格式

import os
import sys
from PIL import Image

# 支持的图片扩展名（可以根据需要增加）
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}

MAX_WIDTH = 1800  # 目标最大宽度


def is_image_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in IMAGE_EXTS


def compress_image_to_webp(input_path: str, max_width: int = MAX_WIDTH):
    """
    将单张图片压缩到指定最大宽度（如果需要），并另存为 webp：
    原文件: xxx.jpg -> xxx-compressed.webp
    """
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name_no_ext, _ = os.path.splitext(base_name)

    # 如果已经是 -compressed.webp，就跳过，防止重复处理
    if name_no_ext.endswith("-compressed"):
        print(f"[跳过] 已是压缩文件：{input_path}")
        return

    output_name = f"{name_no_ext}-compressed.webp"
    output_path = os.path.join(dir_name, output_name)

    # 如果目标文件已存在，可以选择跳过或覆盖，这里选择跳过
    if os.path.exists(output_path):
        print(f"[跳过] 目标文件已存在：{output_path}")
        return

    try:
        with Image.open(input_path) as img:
            orig_w, orig_h = img.size

            # 判断是否需要缩放
            if orig_w > max_width:
                # 计算新高度，保持宽高比
                new_w = max_width
                new_h = int(orig_h * (new_w / orig_w))
                img = img.resize((new_w, new_h), Image.LANCZOS)
                print(f"[缩放] {input_path} -> {new_w}x{new_h}")
            else:
                print(f"[不缩放] {input_path} 保持原尺寸 {orig_w}x{orig_h}")

            # 处理颜色模式，webp 支持透明通道，这里尽量保留
            if img.mode not in ("RGB", "RGBA"):
                # 如果原图有 alpha，尽量保持
                if "A" in img.getbands():
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")

            # 保存为 webp 格式，质量可以根据需要调整
            img.save(output_path, format="WEBP", quality=85, method=6)
            print(f"[保存] {output_path}")

    except Exception as e:
        print(f"[错误] 处理 {input_path} 时出错：{e}")


def walk_and_compress(root_dir: str, max_width: int = MAX_WIDTH):
    """
    递归遍历 root_dir 下的所有文件，压缩所有图片
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if not is_image_file(filename):
                continue

            full_path = os.path.join(dirpath, filename)
            compress_image_to_webp(full_path, max_width=max_width)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python compress_images.py <目录路径> [最大宽度]")
        print("示例：python compress_images.py ./images 1800")
        sys.exit(1)

    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"错误：{root} 不是一个有效的目录")
        sys.exit(1)

    if len(sys.argv) >= 3:
        try:
            max_w = int(sys.argv[2])
        except ValueError:
            print("最大宽度参数必须是整数，例如：1800")
            sys.exit(1)
    else:
        max_w = MAX_WIDTH

    print(f"开始处理目录：{root}，最大宽度：{max_w}")
    walk_and_compress(root, max_width=max_w)
    print("处理完成。")
