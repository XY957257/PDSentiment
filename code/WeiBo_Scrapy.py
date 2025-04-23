import requests
import csv
import random
import time

# 设置请求头，需要替换Cookie和Referer
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "Cookie": "SINAGLOBAL=2339119507760.923.1740890031835; ULV=1740890031889:1:1:1:2339119507760.923.1740890031835:; SCF=Ai_jzgIds4vbnew5oOPH38lN9DWhkcP83Z0C87NoZbUHSNh_yK7PLWzYOt0m_9FKvomn5JkFMhkJ2d3XKzez7ug.; SUB=_2A25FAyAWDeRhGeFJ7VYS9SrFzT6IHXVmYT3erDV8PUNbmtANLU7VkW9Nf0mmPouBdnJLyQpFCfuERclH8lNCGLO5; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh0PxAIqkQJT.5GaRrUr8Ds5JpX5KzhUgL.FoMNSoB0SKB4Soz2dJLoI0qLxK-LBo2L12zLxK.LBK2LBoqLxKML1-eL1-qLxKqLBK.L1K.LxK-LB-BL1K5LxK-L1K2LBoet; ALF=02_1747901766; WBPSESS=UbjZTYtDmeqw4nfrsyDQHb2HkatNf502urSKwGMWV8F4nxXgc0270tEKpHAjnoHhMoHwf9Cy-mnPlGGAeiusHx6XYcF6b93HphQE-9wuJiZCY5fwDWgDOVtVZMNxz1Kycz7Sz6wgEjRDIVFckBSvSA==",
    "Referer": "https://weibo.com/2656274875/Por8LsiIr"
}
url = "https://weibo.com/ajax/statuses/buildComments?"

# 打开文件
f = open("test2.csv","a",encoding="utf-8-sig",newline="")

# 写入表头，根据实际情况修改列名
writer = csv.writer(f)
writer.writerow(["comments","created_at","gender","location"])

# 定义爬取二级评论的第一页的函数的参数
def setFirstParams(id,max_id):
    # 需要替换uid
    """
    :param id: 一级评论的id
    :param max_id: 一级评论的max_id
    :return: 二级评论的参数
    """
    params = {
        "is_reload": "1",
        "id":id,
        "is_show_bulletin": "2",
        "is_mix": "1",
        "fetch_level": "1",
        "max_id": max_id,
        "count": "20",
        "uid": "2656274875",
        "locale": "zh-CN"
    }
    return params

# 定义爬取二级评论的第一页的函数
def crawl2(id, max_id):
    """
    :param id: 一级评论的id
    :param max_id: 一级评论的max_id
    :return: 一级评论的id和max_id
    """
    # 计数
    i = 1
    # 请求数据
    response = requests.get(url=url,params=setFirstParams(id=id,max_id=max_id), headers=headers).json()
    # 获取数据
    data_list = response["data"]
    for data in data_list:
        # 遍历data_list，获取每一条二级评论数据
        comments = data["text_raw"]
        created_at = data["created_at"]
        gender = data["user"]["gender"]
        location = data["user"]["location"] 
        # 写入文件
        writer.writerow([comments,created_at,gender,location])
        print(f"本页第{i}条评论已爬取")
        i += 1
        # 获取第一页二级评论的id和max_id
        id = str(data["id"])
        max_id = "max_id=" + str(response["max_id"])
    # 当存在下一页时，递归调用
    if response["max_id"] != 0:
        try:
            time.sleep(random.randint(1,3))
            # 使用crawl3函数爬取二级评论的下一页
            crawl3(id,max_id)
        except Exception as e:
            print(e)
    # 当不存在下一页时，返回第一页二级评论的id和max_id
    return id, max_id

# 定义爬取二级评论的下一页的函数的参数
def setSecondParams(id, max_id):
    """
    :param id: 二级评论的id
    :param max_id: 二级评论的max_id
    :return: 二级评论的参数
    """
    params = {
        "flow": "1",
        "is_reload": "1",
        "id": id,
        "is_show_bulletin": "2",
        "is_mix": "1",
        "fetch_level": "1",
        "max_id": max_id,
        "count": "20",
        "uid": "2656274875",
        "locale": "zh-CN",
    }
    return params

# 定义爬取二级评论的下一页的函数
def crawl3(id, max_id):
    """
    :param id: 二级评论的id
    :param max_id: 二级评论的max_id
    :return: 二级评论的id和max_id
    """
    print("开始爬取二级评论的下一页!")
    # 请求数据
    response = requests.get(url=url,params=setSecondParams(id=id,max_id=max_id), headers=headers).json()
    # 遍历data_list，获取每二级评论数据
    data_list = response["data"]
    for data in data_list:
        # 获取数据
        comments = data["text_raw"]
        created_at = data["created_at"]
        gender = data["user"]["gender"]
        location = data["user"]["location"] 
        # 写入文件
        writer.writerow([comments,created_at,gender,location])
        # 获取下一页二级评论的id和max_id
        id = str(data["id"])
        max_id = "max_id=" + str(response["max_id"])

    # 当存在下一页时，递归调用
    if response["max_id"] != 0:
        try:
            time.sleep(random.randint(1,3))
            crawl3(id,max_id)
        except Exception as e:
            print(e)
    return id, max_id

# 定义爬取一级评论的函数，需要替换url并且将链接中的"count=10"替换为"{next}"
def crawl(next = "count=10"):
    """
    :param next: 一级评论的翻页参数，默认为count=10，此后的参数为max_id
    :return: None
    """
    # 页数计数
    global page
    try:
        # 爬取一级评论
        url = f"https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=5158242036745131&is_show_bulletin=2&is_mix=0&{next}&uid=2656274875&fetch_level=0&locale=zh-CN"
        response = requests.get(url=url, headers=headers).json()
        # 遍历data_list，获取每一条一级评论数据
        data_list = response["data"]
        for data in data_list:
            # 获取数据
            comments = data["text_raw"]
            created_at = data["created_at"]
            gender = data["user"]["gender"]
            location = data["user"]["location"] 
            # 写入文件
            writer.writerow([comments,created_at,gender,location])
            # 获取下一页一级评论的id和max_id
            id = data["id"]
            max_id = "max_id=" + str(response["max_id"])

            # 如果data中的[total_number]不为0，表明存在二级评论，调用crawl2爬取第一页二级评论
            if data["total_number"] != 0:
            # if len(data["comments"]) != 0:
                try:
                    time.sleep(random.randint(1,3))
                    crawl2(id,max_id)
                except Exception as e:
                    print(e)

        print(f"------第{page}页已爬取！-------")
        page += 1

        # 当未爬取完所有评论时，递归调用
        if response["max_id"] != 0:
            try:
                time.sleep(random.randint(1,3))
                crawl(max_id)
            except Exception as e:
                print(e)
                f.close()
        print("----爬取结束！-----")
        f.close()
    except Exception as e:
        print(e)
        f.close()

if __name__ == '__main__':
    # 页数计数
    page = 1
    # 调用crawl函数
    crawl()