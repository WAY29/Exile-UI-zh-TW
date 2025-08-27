# 根据[leveltracker] areas 2.json 中的 id 和 name 对应关系，将 name 翻译成中文
# 将翻译后的结果保存到[leveltracker] areas 2 new.json 中
# 通过请求 https://poe2db.tw/tw/<area_name> 获取翻译后的结果
# 使用多线程进行翻译


import json
import requests
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, wait


def translate_area(i, j, area_name):
    url = f'https://poe2db.tw/tw/{area_name}'
    response: requests.Response = requests.get(
        url, proxies={"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}, timeout=10)
    # 解析 html
    # 获取翻译后的结果
    html = etree.HTML(response.text)
    if html is None:
        return area_name
    p = html.xpath('/html/body/div[3]/div/h4[1]/text()')
    if len(p) == 0:
        return area_name
    translation = p[0]
    data[i][j]['name'] = translation
    return translation


def capitalize_area_name(k, s):
    if s == "of" or s == "the" and k != 0:
        return s
    return s[0].upper() + s[1:]


with open('[leveltracker] areas 2.json', 'r', encoding='utf-8') as f, open('[leveltracker] areas 2 new.json', 'w', encoding='utf-8') as f2, ThreadPoolExecutor(max_workers=16) as pool:
    data = json.load(f)
    futures = []

    for i, item in enumerate(data):
        for j, area in enumerate(item):
            # 需要将 <area_name> 进行处理，空格替换为_, 每个单词首字母大写
            area_name: str = area['name']
            if " " in area_name:
                splited = area_name.split(" ")
                for k, s in enumerate(splited):
                    splited[k] = capitalize_area_name(k, s)
                area_name = "_".join(splited)
            else:
                area_name = capitalize_area_name(0, area_name)

            futures.append(pool.submit(translate_area, i, j, area_name))

    wait(futures)
    json.dump(data, f2, ensure_ascii=False, indent=4)
