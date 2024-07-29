import os
import math
from PIL import Image, ImageDraw, ImageFont

def add_text_to_images(init_result, dir_name, weekdays, first_name, score_dic):
    # 获取用户输入
    user_input = input("是否需要添加名称,时间,以及整体的透明度(例如:1,1,0.8),回车默认为1,1,0.8:")
    if not user_input:
        user_input = "1,1,0.8"
    
    try:
        add_name, add_time, text_opacity = map(float, user_input.split(','))
    except ValueError:
        print("输入格式错误,使用默认设置1,1,0.8")
        add_name, add_time, text_opacity = 1, 1, 0.8

    images = []
    for filename in os.listdir(dir_name):
        if filename.endswith('.jpg'):
            img_path = os.path.join(dir_name, filename)
            images.append((filename, Image.open(img_path).convert("RGBA")))
    
    # 检查是否存在背景图片文件夹
    background_dir = 'processed_background'
    if os.path.exists(background_dir) and os.path.isdir(background_dir):
        # 获取文件夹中的所有图片
        background_files = [f for f in os.listdir(background_dir) if f.endswith(('.png'))]
        if not background_files:
            print("No images found in background folder. Exiting.")
            return
    else:
        print("Background folder not found. Exiting.")
        return

    # 创建produced文件夹
    produced_dir = 'produced'
    if not os.path.exists(produced_dir):
        os.makedirs(produced_dir)

    for background_file in background_files:
        background_path = os.path.join(background_dir, background_file)
        # 加载背景图片并获取其长宽比
        background = Image.open(background_path).convert("RGBA")
        background_aspect_ratio = round(background.width / background.height, 2)
        
        print(f"Loading background image: {background_file}")
        print(f"Background aspect ratio: {background_aspect_ratio}:1")

        # 创建新的图像
        image_size = (600, 750)
        border_size = 20  # 透明边框的大小
        text_height = 80  # 文本区域的高度
        new_image_size = (image_size[0] + 2 * border_size, image_size[1] + 2 * border_size + text_height)
        # print(new_image_size)

        # 确定排列方式
        num_images = len(images)
        best_grid_size = None
        min_diff = float('inf')
        for grid_size in range(1, num_images + 1):
            grid_size_1 = math.ceil(num_images / grid_size)
            grid_aspect_ratio = grid_size / grid_size_1
            diff = abs(grid_aspect_ratio - background_aspect_ratio)
            if diff < min_diff:
                min_diff = diff
                best_grid_size = (grid_size, grid_size_1)

        grid_size, grid_size_1 = best_grid_size
        print("Best grid size:", best_grid_size)

        # 放大背景图片
        scale_factor = max((grid_size * new_image_size[0]) / background.width, (grid_size_1 * new_image_size[1]) / background.height)
        canvas_size = (int(background.width * scale_factor), int(background.height * scale_factor))

        # 调整背景图片大小以适应画布
        background = background.resize(canvas_size, Image.LANCZOS)
        new_image = Image.new('RGBA', canvas_size)
        new_image.paste(background, (0, 0))

        # 计算间隔和边距
        total_width = new_image_size[0] * grid_size
        total_height = new_image_size[1] * grid_size_1

        if total_width > canvas_size[0] or total_height > canvas_size[1]:
            raise ValueError("Canvas size is too small to fit all images with the specified grid size.")

        horizontal_margin = (canvas_size[0] - total_width) // (grid_size + 1)
        vertical_margin = (canvas_size[1] - total_height) // (grid_size_1 + 1)

        # 设置字体
        font_path_text = "C:/Windows/Fonts/msyhbd.ttc"
        try:
            font = ImageFont.truetype(font_path_text, 30)
        except IOError:
            font = ImageFont.load_default()

        # 将图片排列到新图像上
        for index, (filename, img) in enumerate(images):
            image_name = os.path.splitext(filename)[0]
            # 从字典中获取相应的名称和时间
            first = int(image_name.split('.')[0])
            second = int(image_name.split('.')[1])
            name, time = init_result[first][second-1][0], weekdays[first]+' '+init_result[first][second-1][2]

            # 如果 score_dic 不为空，则将分数添加到 name 后面
            if score_dic:
                score_key = f"{first}.{second}"
                if score_key in score_dic:
                    score = score_dic[score_key]
                    name = f"{name} {score}/10"

            row = index // grid_size
            col = index % grid_size

            x = horizontal_margin * (col + 1) + new_image_size[0] * col
            y = vertical_margin * (row + 1) + new_image_size[1] * row

            # 调整图片大小
            img = img.resize(image_size, Image.LANCZOS)

            # 添加透明边框
            img_with_border = Image.new('RGBA', (image_size[0] + 2 * border_size, image_size[1] + 2 * border_size), (255, 255, 255, 0))
            img_with_border.paste(img, (border_size, border_size))

            # 将图片粘贴到新图像上，并调整透明度
            if add_name and add_time:
                img_with_border = img_with_border.convert("RGBA")
                img_with_border_alpha = img_with_border.split()[3].point(lambda p: p * text_opacity)
                img_with_border.putalpha(img_with_border_alpha)
                new_image.paste(img_with_border, (x, y), img_with_border)

            # 计算文本宽度以进行居中对齐
            if add_name:
                name_bbox = ImageDraw.Draw(new_image).textbbox((0, 0), name, font=font)
                name_width = name_bbox[2] - name_bbox[0]
                name_height = name_bbox[3] - name_bbox[1]
                name_x = x + (new_image_size[0] - name_width) // 2
                text_y = y + image_size[1] + 2 * border_size

            if add_time:
                time_bbox = ImageDraw.Draw(new_image).textbbox((0, 0), time, font=font)
                time_width = time_bbox[2] - time_bbox[0]
                time_x = x + (new_image_size[0] - time_width) // 2

            # 创建文本图层
            text_layer = Image.new('RGBA', new_image.size, (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_layer)
            text_color = (0, 0, 0, 255)  # 先绘制不透明的文本
            if add_name:
                text_draw.text((name_x, text_y), name, fill=text_color, font=font)
            if add_time:
                text_draw.text((time_x, text_y + name_height), time, fill=text_color, font=font)

            # 调整文本图层的透明度
            text_layer_alpha = text_layer.split()[3].point(lambda p: p * text_opacity)
            text_layer.putalpha(text_layer_alpha)

            # 将文本图层粘贴到新图像上
            new_image = Image.alpha_composite(new_image, text_layer)

        # 生成唯一文件名，根据 score_dic 是否为空调整后缀
        base_name = os.path.splitext(background_file)[0]
        suffix = "_after" if score_dic else "_before"
        new_file_path = os.path.join(produced_dir, f"{first_name[0:6]}_{base_name}{suffix}.png")
        if os.path.exists(new_file_path):
            print(f"文件已存在，跳过: {new_file_path}")
            continue

        new_image = new_image.convert("RGB")  # 转换为RGB模式以保存为PNG
        new_image.save(new_file_path)
        print(f"新图像已保存: {new_file_path}")
