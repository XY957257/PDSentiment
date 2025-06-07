def ana():
    contents = []
    provinces = []
    dates = []
    like_counts = []

    try:
        with open("spider.csv", 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            headers = ["评论", "地区", "日期", "点赞"]
            header_line_found = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 自动跳过所有标题行（即使文件中有多个）
                if any(line.startswith(header) for header in headers):
                    continue

                parts = line.split(',')

                # 检查是否至少有4列（评论, 地区, 日期, 点赞）
                if len(parts) < 4:
                    print(f"⚠️ 跳过格式不完整的行: {line}")
                    continue

                content = parts[0].strip()
                province = parts[1].strip()
                date = parts[2].strip()

                # 处理点赞数
                like_str = parts[3].strip()
                if like_str.isdigit():  # 只接受纯数字
                    like_count = int(like_str)
                else:
                    print(f"⚠️ 点赞数无效，设为0: {like_str}")
                    like_count = 0

                contents.append(content)
                provinces.append(province)
                dates.append(date)
                like_counts.append(like_count)

    except FileNotFoundError:
        print("❌ 文件 'spider.csv' 不存在")
        return [], [], [], []
    except Exception as e:
        print(f"❌ 读取文件时发生错误: {e}")
        return [], [], [], []

    return contents, provinces, dates, like_counts