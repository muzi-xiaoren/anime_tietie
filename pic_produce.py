import os
import math
from PIL import Image, ImageDraw, ImageFont

def get_user_input():
    user_input = input("是否需要添加名称,时间,以及整体的透明度(例如:1,1,0.8),回车默认为1,1,0.8:")
    if not user_input:
        user_input = "1,1,0.8"
    
    try:
        add_name, add_time, text_opacity = map(float, user_input.split(','))
    except ValueError:
        print("输入格式错误,使用默认设置1,1,0.8")
        add_name, add_time, text_opacity = 1, 1, 0.8
    
    return add_name, add_time, text_opacity

def load_images_from_directory(dir_name):
    images = []
    for filename in os.listdir(dir_name):
        if filename.endswith('.jpg'):
            img_path = os.path.join(dir_name, filename)
            images.append((filename, Image.open(img_path).convert("RGBA")))
    return images

def check_background_directory(background_dir):
    if os.path.exists(background_dir) and os.path.isdir(background_dir):
        background_files = [f for f in os.listdir(background_dir) if f.endswith(('.png'))]
        if not background_files:
            print("No images found in background folder. Exiting.")
            return None
    else:
        print("Background folder not found. Exiting.")
        return None
    return background_files

def create_produced_directory(produced_dir):
    if not os.path.exists(produced_dir):
        os.makedirs(produced_dir)

def calculate_best_grid_size(num_images, background_aspect_ratio):
    best_grid_size = None
    min_diff = float('inf')
    for grid_size in range(1, num_images + 1):
        grid_size_1 = math.ceil(num_images / grid_size)
        grid_aspect_ratio = grid_size / grid_size_1
        diff = abs(grid_aspect_ratio - background_aspect_ratio)
        if diff < min_diff:
            min_diff = diff
            best_grid_size = (grid_size, grid_size_1)
    return best_grid_size

def calculate_row_sizes(num_images, row_count):
    base_images_per_row = num_images // row_count
    remainder = num_images % row_count
    row_sizes = [base_images_per_row + 1 if i < remainder else base_images_per_row for i in range(row_count)]
    return row_sizes

def add_text_to_image(new_image, x, y, name, time, font, add_name, add_time, text_opacity, image_size, border_size):
    text_layer = Image.new('RGBA', new_image.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_color = (0, 0, 0, 255)
    
    if add_name:
        name_bbox = text_draw.textbbox((0, 0), name, font=font)
        name_width = name_bbox[2] - name_bbox[0]
        name_height = name_bbox[3] - name_bbox[1]
        name_x = x + (image_size[0] + 2 * border_size - name_width) // 2
        text_y = y + image_size[1] + 2 * border_size
        text_draw.text((name_x, text_y), name, fill=text_color, font=font)
    
    if add_time:
        time_bbox = text_draw.textbbox((0, 0), time, font=font)
        time_width = time_bbox[2] - time_bbox[0]
        time_x = x + (image_size[0] + 2 * border_size - time_width) // 2
        text_draw.text((time_x, text_y + name_height + 8), time, fill=text_color, font=font)
    
    text_layer_alpha = text_layer.split()[3].point(lambda p: p * text_opacity)
    text_layer.putalpha(text_layer_alpha)
    new_image = Image.alpha_composite(new_image, text_layer)
    return new_image

def save_new_image(new_image, produced_dir, background_file, first_name, score_dic):
    base_name = os.path.splitext(background_file)[0]
    suffix = "_after" if score_dic else "_before"
    new_file_path = os.path.join(produced_dir, f"{first_name[0:6]}_{base_name}{suffix}.png")
    if os.path.exists(new_file_path):
        print(f"文件已存在，跳过: {new_file_path}")
        return
    
    new_image = new_image.convert("RGB")
    new_image.save(new_file_path)
    print(f"新图像已保存: {new_file_path}")

def add_text_to_images(init_result, dir_name, weekdays, first_name, score_dic):
    add_name, add_time, text_opacity = get_user_input()
    images = load_images_from_directory(dir_name)
    background_dir = 'processed_background'
    background_files = check_background_directory(background_dir)
    if not background_files:
        return
    
    produced_dir = 'produced'
    create_produced_directory(produced_dir)
    
    for background_file in background_files:
        background_path = os.path.join(background_dir, background_file)
        background = Image.open(background_path).convert("RGBA")
        background_aspect_ratio = round(background.width / background.height, 2)
        
        print(f"Loading background image: {background_file}")
        print(f"Background aspect ratio: {background_aspect_ratio}:1")
        
        image_size = (600, 750)
        border_size = 15
        text_height = 80
        new_image_size = (image_size[0] + 2 * border_size, image_size[1] + 2 * border_size + text_height)
        
        num_images = len(images)
        best_grid_size = calculate_best_grid_size(num_images, background_aspect_ratio)
        grid_size, grid_size_1 = best_grid_size
        print("Best grid size:", best_grid_size)
        
        row_count = grid_size_1
        col_count = grid_size
        row_sizes = calculate_row_sizes(num_images, row_count)
        print("Row sizes:", row_sizes)
        
        scale_factor = max((col_count * new_image_size[0]) / background.width, (row_count * new_image_size[1]) / background.height)
        canvas_size = (int(background.width * scale_factor), int(background.height * scale_factor))
        background = background.resize(canvas_size, Image.LANCZOS)
        new_image = Image.new('RGBA', canvas_size)
        new_image.paste(background, (0, 0))
        
        total_width = new_image_size[0] * col_count
        total_height = new_image_size[1] * row_count
        
        if total_width > canvas_size[0] or total_height > canvas_size[1]:
            raise ValueError("Canvas size is too small to fit all images with the specified grid size.")
        
        horizontal_margin = (canvas_size[0] - total_width) // (col_count + 1)
        vertical_margin = (canvas_size[1] - total_height) // (row_count + 1)
        
        font_path_text = "C:/Windows/Fonts/msyhbd.ttc"
        font = ImageFont.truetype(font_path_text, 30)
        
        image_index = 0
        for row in range(row_count):
            images_in_row = row_sizes[row]
            row_total_width = images_in_row * new_image_size[0]
            horizontal_spacing = (canvas_size[0] - row_total_width) // (images_in_row + 1)
            
            for col in range(images_in_row):
                x = horizontal_spacing * (col + 1) + new_image_size[0] * col
                y = vertical_margin * (row + 1) + new_image_size[1] * row
                
                filename, img = images[image_index]
                image_name = os.path.splitext(filename)[0]
                first = int(image_name.split('.')[0])
                second = int(image_name.split('.')[1])
                name, time = init_result[first][second-1][0], weekdays[first] + ' ' + init_result[first][second-1][2]
                
                if score_dic:
                    score_key = f"{first}.{second}"
                    if score_key in score_dic:
                        score = score_dic[score_key]
                        name = f"{name} {score}/10"
                
                img = img.resize(image_size, Image.LANCZOS)
                img_with_border = Image.new('RGBA', (image_size[0] + 2 * border_size, image_size[1] + 2 * border_size), (255, 255, 255, 0))
                img_with_border.paste(img, (border_size, border_size))
                
                if add_name and add_time:
                    img_with_border = img_with_border.convert("RGBA")
                    img_with_border_alpha = img_with_border.split()[3].point(lambda p: p * text_opacity)
                    img_with_border.putalpha(img_with_border_alpha)
                    new_image.paste(img_with_border, (x, y), img_with_border)
                
                new_image = add_text_to_image(new_image, x, y, name, time, font, add_name, add_time, text_opacity, image_size, border_size)
                image_index += 1
        
        save_new_image(new_image, produced_dir, background_file, first_name, score_dic)