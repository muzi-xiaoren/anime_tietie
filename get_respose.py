import os
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36 Edg/84.0.522.63',
}


def save_response_content(url, headers, file_path):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"内容已保存到 {file_path}")
    else:
        print(f"请求失败，状态码：{response.status_code}")


def load_response_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def check_file(url, file_path):
# 检查文件是否存在,如果存在就不反复爬取,减小服务器压力。
    if os.path.exists(file_path):
        print(f"{file_path} 文件已存在，读取内容...")
        content = load_response_content(file_path)
    else:
        print(f"{file_path} 文件不存在，访问页面并保存内容...")
        save_response_content(url, headers, file_path)
        content = load_response_content(file_path)

    return content
