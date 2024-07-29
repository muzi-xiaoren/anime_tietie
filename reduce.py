import os
from PIL import Image

def remove_white_borders(image):
    # 将图像转换为RGBA模式
    image = image.convert("RGBA")
    # 获取图像数据
    data = image.getdata()

    # 找到非白色像素的边界
    left, top, right, bottom = image.width, image.height, 0, 0
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = data[y * image.width + x]
            if not (r > 240 and g > 240 and b > 240):
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)

    # 裁剪图像
    if left < right and top < bottom:
        image = image.crop((left, top, right + 1, bottom + 1))

    return image

def process_background_images():
    input_dir = 'background'
    output_dir = 'processed_background'

    # 创建输出文件夹
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # 检查输出文件是否已存在
        if os.path.exists(output_path):
            print(f"文件已存在，跳过: {output_path}")
            continue

        # 打开图像
        image = Image.open(input_path)
        # 去除白边
        processed_image = remove_white_borders(image)
        # 保存处理后的图像
        processed_image.save(output_path)
        print(f"Processed image saved to {output_path}")

process_background_images()
