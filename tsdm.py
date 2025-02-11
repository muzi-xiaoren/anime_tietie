import re
import os
import requests

def time_reload(days, compare_result):
    # 处理时间大于24小时的情况
    for day in days:
        if day >= 8:
            continue
        next_day = day % 7 + 1
        
        new_entries = []
        for entry in compare_result[day]:
            time_str = entry[2]
            match = re.match(r'(\d+):(\d+)', time_str)
            if match:
                hour, minute = int(match.group(1)), match.group(2)
                if hour >= 24:
                    new_hour = hour - 24
                    new_time_str = f'{new_hour:02}:{minute}'
                    new_entry = [entry[0], entry[1], new_time_str]
                    compare_result[next_day].append(new_entry)
                else:
                    new_entries.append(entry)
            else:
                new_entries.append(entry)
        compare_result[day] = new_entries
    return compare_result


def sort_key(entry):
    time_str = entry[2]
    match = re.match(r'(\d+):(\d+)', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        return hour * 60 + minute
    return 0


def img_download(dir_name, user_selections, init_result):
# 下载图片
    if user_selections == ['']:
        return
    for selection in user_selections:
        first = int(selection.split('.')[0])
        second = int(selection.split('.')[1])
        url = init_result[first][second-1][1]
        print(init_result[first][second-1][0])

        response = requests.get(url)
        if response.status_code == 200:
            file_name = os.path.join(dir_name, f"{selection}.jpg")
            if os.path.exists(file_name):
                print(f"已存在，跳过：{file_name}")
                continue
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"已下载：{file_name}")
        else:
            print(f"无效：{selection}")
