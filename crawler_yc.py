import os
from bs4 import BeautifulSoup
from pic_produce import *
from tsdm import *
from get_respose import *

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.file_path = url[17:23] + '.html'
        # 获取网页数据
        self.response = check_file(self.url, self.file_path)
        self.soup = BeautifulSoup(self.response, 'html.parser')
        # 初始化转换字典
        self.weekdays = ['未知', '周一 (月)', '周二 (火)', '周三 (水)', '周四 (木)', '周五 (金)', '周六 (土)', '周日 (日)']
        self.mapping_num = {'周一 (月)': 1, '周二 (火)': 2, '周三 (水)': 3, '周四 (木)': 4, '周五 (金)': 5, '周六 (土)': 6, '周日 (日)': 7}
        self.init_result = {}

    def parse_data(self):
        # 动态调整 weekday_elements 数量
        weekday_elements = self.soup.find_all(class_='date2')
        if len(weekday_elements) == 8:
            self.weekdays.append('网络放送 & 其他')
            self.mapping_num['网络放送 & 其他'] = 8
        elif len(weekday_elements) == 9:
            self.weekdays.append('泡面番')
            self.mapping_num['泡面番'] = 8
            self.weekdays.append('网络放送 & 其他')
            self.mapping_num['网络放送 & 其他'] = 9

        counts = {}
        for element in weekday_elements:
            weekday_text = element.get_text(strip=True)
            parent_div = element.find_parent('div')
            next_div = parent_div.find_next_sibling('div')
            if next_div:
                temp_date = next_div.find_all(class_=['date_title', 'date_title1', 'date_title2', 'date_title_', 'date_title__'])
                counts[weekday_text] = len(temp_date)

        date_titles = [title.get_text(strip=True) for title in self.soup.find_all(class_=['date_title', 'date_title1', 'date_title2', 'date_title_', 'date_title__'])]
        images_120px = [img['data-src'] for img in self.soup.find_all('img', width='120px')]
        time_new = [time.get_text(strip=True)[0:5] for time in self.soup.find_all(class_=['imgtext','imgtext3_','imgtext4'])]
        time_new.extend([''] * (len(date_titles) - len(time_new)))

        current_index = 0
        for key, count in counts.items():
            combined_array = []
            for _ in range(count):
                combined_array.append([date_titles[current_index], images_120px[current_index], time_new[current_index]])
                current_index += 1
            self.init_result[self.mapping_num[key]] = combined_array

    def sort_data(self):
        days = list(self.mapping_num.values())
        self.init_result = time_reload(days, self.init_result)
        for day in days:
            if day != '8':
                self.init_result[day].sort(key=sort_key)

    def print_result(self):
        for key, value in self.init_result.items():
            key_name = self.weekdays[key]
            if key_name not in ['泡面番', '网络放送 & 其他']:
                print(f"{key_name.split()[0]}:", end='')
            else:
                print(f"{' '.join(key_name.split()[0:2])}:", end='')
            titles = [f"{i+1}.{item[0]}" for i, item in enumerate(value)]
            print('   '.join(titles) + '。')

    def download_images(self):
        user_input = input("请输入要下载的内容编号(例如:1.1,2.1,3.1):")
        user_selections = user_input.split(',')
        dir_name = 'img_' + self.url[17:23]
        os.makedirs(dir_name, exist_ok=True)
        img_download(dir_name, user_selections, self.init_result)

        # 读取文件夹内的所有文件，并提取前缀名
        user_selections = [os.path.splitext(f)[0] for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))]
        return user_selections, dir_name

    def ask_for_scores(self, user_selections):
        score_input = input("是否进行打分？(1/0): ").strip().lower()    
        if score_input == '1':
            selected_titles = [self.init_result[int(day)][int(index)-1][0] for day, index in (sel.split('.') for sel in user_selections)]
            print("您选择的番剧名称如下:")
            for title in selected_titles:
                print(title)
            while True:
                scores = input("请输入每个番剧的分数(例如:7,8,9,9.5,10): ").split(',')
                if len(scores) != len(user_selections):
                    print(f"输入的分数数量({len(scores)})与选择的内容数量({len(user_selections)})不符，请重新输入。")
                else:
                    break
            score_dict = {sel: score for sel, score in zip(user_selections, scores)}
            # print(score_dict)
            return score_dict
        return None

    def run(self):
        # 生成数据
        self.parse_data()
        # 排序数据
        self.sort_data()
        # 打印结果
        self.print_result()
        # 下载图片和生成结果
        user_selections, dir_name = self.download_images()
        # 询问用户是否进行打分
        scores = self.ask_for_scores(user_selections)
        # 添加评分信息到图片
        add_text_to_images(self.init_result, dir_name, self.weekdays, self.file_path, scores)

if __name__ == "__main__":
    # 更换每期的url
    url = 'https://yuc.wiki/202501'
    scraper = WebScraper(url)
    scraper.run() 
