import requests
import csv
import random
import time

# 设置请求头，需要替换Cookie和Referer
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
    "Cookie": "SINAGLOBAL=2339119507760.923.1740890031835; SCF=Ai_jzgIds4vbnew5oOPH38lN9DWhkcP83Z0C87NoZbUHSNh_yK7PLWzYOt0m_9FKvomn5JkFMhkJ2d3XKzez7ug.; XSRF-TOKEN=y4PavfqdrD82U072RgrZYvlB; ALF=1751449537; SUB=_2A25FOQKRDeRhGeFH71oX8S_NwzuIHXVmNxpZrDV8PUJbkNANLRfEkW1NewkZaSyRum1Xc9vsR9ZQW3dy7Kzdnp5D; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFi9L2clKBO0EQ.3ilLsjrd5JpX5KMhUgL.FoM4ShnceK2p1hM2dJLoI0YLxK-LB--L1h.LxK.L1-BL1K.LxKML12eLB-zLxK-L1KzLB-2LxK-LB-BLBKqLxKML1KBLB.zLxKML1KBLB.zt; _s_tentry=www.weibo.com; Apache=1262035601851.732.1748857606513; ULV=1748857606515:3:1:2:1262035601851.732.1748857606513:1748273358906; WBPSESS=NyAZoRytRkRkEvTdNBasMCiDbyxswZuqrp-1KA4OU-qBGyJofE5uHKDnvL8-lry_dpyFIOpYD8mhDIIeHEFO40aCjqoe3SqtLivynujV4uWlkkoFGM5Wk9EXrUtJveaQtFg88AiRgsRxI3C_b-ogcw==",
    "Referer": "https://www.weibo.com/5041432467/PrVW67Sek"
}
url = "https://weibo.com/ajax/statuses/buildComments?"

# 打开文件，使用spider.csv文件名适配数据处理函数
f = open("spider.csv", "a", encoding="utf-8-sig", newline="")

# 写入适配ana()函数的表头：内容,地区,日期,点赞
writer = csv.writer(f)
writer.writerow(["评论", "地区", "日期", "点赞"])


# 定义爬取二级评论的第一页的函数的参数
def setFirstParams(id, max_id):
    params = {
        "is_reload": "1",
        "id": id,
        "is_show_bulletin": "2",
        "is_mix": "1",
        "fetch_level": "1",
        "max_id": max_id,
        "count": "20",
        "uid": "5041432467",
        "locale": "zh-CN"
    }
    return params


# 定义爬取二级评论的第一页的函数
def crawl2(id, max_id):
    i = 1
    response = requests.get(url=url, params=setFirstParams(id=id, max_id=max_id), headers=headers).json()
    data_list = response["data"]

    for data in data_list:
        # 提取评论内容（注意：原代码中无点赞数，此处设为0或根据实际情况调整）
        content = data["text_raw"]
        # 地区信息可能需要从location或source字段提取，此处假设location是省份
        province = data["user"].get("location", "")
        date = data["created_at"]
        # 若无点赞数数据，默认设为0（ana函数要求必须有该字段）
        like_count = data.get("like_counts", data.get("like_count", 0))

        writer.writerow([content, province, date, like_count])
        print(f"本页第{i}条二级评论已爬取")
        i += 1

        id = str(data["id"])
        max_id = "max_id=" + str(response["max_id"])

    if response["max_id"] != 0:
        try:
            time.sleep(random.randint(1, 3))
            crawl3(id, max_id)
        except Exception as e:
            print(e)
    return id, max_id


# 定义爬取二级评论的下一页的函数的参数
def setSecondParams(id, max_id):
    params = {
        "flow": "1",
        "is_reload": "1",
        "id": id,
        "is_show_bulletin": "2",
        "is_mix": "1",
        "fetch_level": "1",
        "max_id": max_id,
        "count": "20",
        "uid": "5041432467",
        "locale": "zh-CN",
    }
    return params


# 定义爬取二级评论的下一页的函数
def crawl3(id, max_id):
    print("开始爬取二级评论的下一页!")
    response = requests.get(url=url, params=setSecondParams(id=id, max_id=max_id), headers=headers).json()
    data_list = response["data"]

    for data in data_list:
        content = data["text_raw"]
        province = data["user"].get("location", "")
        date = data["created_at"]
        like_count = data.get("like_counts", data.get("like_count", 0))

        writer.writerow([content, province, date, like_count])
        id = str(data["id"])
        max_id = "max_id=" + str(response["max_id"])

    if response["max_id"] != 0:
        try:
            time.sleep(random.randint(1, 3))
            crawl3(id, max_id)
        except Exception as e:
            print(e)
    return id, max_id


# 定义爬取一级评论的函数
def crawl(next="count=10"):
    global page
    try:
        # 调整URL结构以适配一级评论爬取
        url = f"https://www.weibo.com/ajax/statuses/buildComments?is_reload=1&id=5166575661876760&is_show_bulletin=2&is_mix=0&{next}&uid=5041432467&fetch_level=0&locale=zh-CN"
        response = requests.get(url=url, headers=headers).json()
        data_list = response["data"]

        for data in data_list:
            # 提取一级评论数据
            content = data["text_raw"]
            province = data["user"].get("location", "")
            date = data["created_at"]
            like_count = data.get("like_counts", data.get("like_count", 0))

            writer.writerow([content, province, date, like_count])

            # 处理二级评论（若有）
            if data.get("total_number", 0) != 0:
                try:
                    time.sleep(random.randint(1, 3))
                    comment_id = data["id"]
                    max_id = "max_id=" + str(response["max_id"])
                    crawl2(comment_id, max_id)
                except Exception as e:
                    print(f"二级评论爬取失败: {e}")

        print(f"------第{page}页一级评论已爬取！-------")
        page += 1

        if response["max_id"] != 0:
            try:
                time.sleep(random.randint(1, 3))
                crawl(f"max_id={response['max_id']}")
            except Exception as e:
                print(f"翻页失败: {e}")
                f.close()
        print("----爬取结束！-----")
        f.close()
    except Exception as e:
        print(f"爬取错误: {e}")
        f.close()


def main(weibo_url):
    """主函数，接受微博URL作为参数"""
    global page
    page = 1

    # 从URL中提取微博ID（根据实际URL格式调整）
    try:
        weibo_id = weibo_url.split('/')[-1]
        headers['Referer'] = weibo_url

        # 调用爬取函数
        crawl()
        return "数据收集成功!"
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        return f"执行过程中发生错误: {e}"

if __name__ == '__main__':
    page = 1
    crawl()