import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import demo2 as dm2
import csv
import matplot as mt
import streamlit.components.v1 as components

# 设置页面配置
st.set_page_config(
    layout="wide",
    page_title="社交媒体情感分析平台",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主容器样式 */
    .main {
        background-color: #f8f9fa;
        font-family: 'Arial', sans-serif;
    }

    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #3a7bd5 0%, #00d2ff 100%);
        color: white;
        padding: 2rem 1rem;
    }

    .sidebar .stSelectbox, .sidebar .stRadio {
        color: white;
    }

    /* 标题样式 */
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3a7bd5;
        padding-bottom: 10px;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }

    h2, h3 {
        color: #2980b9;
        margin-top: 1.5rem;
        font-weight: 600;
    }

    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(90deg, #3a7bd5 0%, #00d2ff 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(90deg, #2c5cb5 0%, #00c2f0 100%);
    }

    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 12px;
        padding: 14px;
        border: 1px solid #dfe6e9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 单选按钮样式 */
    .stRadio>div {
        flex-direction: row;
        align-items: center;
        gap: 15px;
        margin: 15px 0;
    }

    .stRadio>div>label {
        margin-right: 0;
        padding: 10px 20px;
        border-radius: 25px;
        background-color: #f1f5f9;
        transition: all 0.3s;
        border: 1px solid #e2e8f0;
    }

    .stRadio>div>label:hover {
        background-color: #e2f1ff;
        transform: translateY(-2px);
    }

    /* 卡片效果 */
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
        margin-bottom: 25px;
        border: 1px solid #e2e8f0;
    }

    /* 结果展示样式 */
    .result-positive {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.3rem;
        padding: 8px 15px;
        background-color: #e8f5e9;
        border-radius: 20px;
        display: inline-block;
    }

    .result-negative {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.3rem;
        padding: 8px 15px;
        background-color: #ffebee;
        border-radius: 20px;
        display: inline-block;
    }

    .result-neutral {
        color: #3498db;
        font-weight: bold;
        font-size: 1.3rem;
        padding: 8px 15px;
        background-color: #e3f2fd;
        border-radius: 20px;
        display: inline-block;
    }

    /* 分隔线样式 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #3a7bd5, transparent);
        margin: 2.5rem 0;
        opacity: 0.3;
    }

    /* 图表容器 */
    .chart-container {
        border-radius: 12px;
        overflow: hidden;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* 响应式调整 */
    @media (max-width: 1200px) {
        .stRadio>div {
            flex-direction: column;
            align-items: flex-start;
        }
    }
</style>
""", unsafe_allow_html=True)

f11 = open("mid.txt", 'r', encoding="utf-8")
i = f11.readline()
print("主程序加载")


def main():
    # 原有模型初始化代码保持不变...
    a = 'mydata'
    b = '123'
    print("主函数开始")
    start_time = dm2.time.time()
    dm2.torch.manual_seed(1)
    dm2.torch.cuda.manual_seed_all(1)
    dm2.torch.backends.cudnn.deterministic = True
    config = dm2.Config(a, b)
    vocab_path = 'mydata/data/vocab3.pkl'
    vocab = dm2.pkl.load(open(vocab_path, 'rb'))
    time_dif = dm2.get_time_dif(start_time)
    print("Time usage:", time_dif)
    config.n_vocab = len(vocab)
    global cfggb
    cfggb = len(vocab)
    model = dm2.Model(config).to('cpu')
    model.load_state_dict(dm2.torch.load(config.save_path))

    # 侧边栏设计
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #3a7bd5; font-size: 1.8rem;">情感分析平台</h1>
            <p style="color: #3a7bd5; font-size: 1rem; opacity: 0.9;">社交媒体评论情感分析系统</p>
        </div>
        """, unsafe_allow_html=True)

        side = ["主界面", "数据分析结果"]
        la = st.selectbox("导航菜单", side, key="nav_select")

        st.markdown("---")
        st.markdown("""
        """, unsafe_allow_html=True)

    # 主界面内容
    if la == "主界面":
        # 单句分析部分
        st.markdown("""
        <div class="card">
            <h2 style="color: #3a7bd5;">🔍 单句情感分析</h2>
            <p style="color: #64748b;">输入文本内容，实时分析其情感倾向</p>
        </div>
        """, unsafe_allow_html=True)

        test = st.text_input("输入您想分析的文本:", key="single_text_input",
                             placeholder="例如：今天天气真好，心情愉快！")

        col1, col2 = st.columns([1, 5])
        with col1:
            x = st.button("开始分析", key="analyze_btn")

        if x and test:
            with st.spinner('分析中...'):
                res = dm2.predict(model, test, cfggb)
                # 根据结果选择不同的样式
                result_class = {
                    "积极": "result-positive",
                    "消极": "result-negative",
                    "中性": "result-neutral"
                }.get(res, "")

                st.markdown(f"""
                <div class="card">
                    <h3>分析结果</h3>
                    <p style="font-size: 1.1rem;"><strong>输入文本：</strong> {test}</p>
                    <p style="font-size: 1.1rem;"><strong>情感倾向：</strong> <span class="{result_class}">{res}</span></p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # 数据集分析部分
        st.markdown("""
        <div class="card">
            <h2 style="color: #3a7bd5;">📊 批量情感分析</h2>
            <p style="color: #64748b;">分析本地数据集或微博链接的评论情感</p>
        </div>
        """, unsafe_allow_html=True)

        text = st.text_input("输入微博链接或文件地址:",
                             key="dataset_input",
                             placeholder="例如: https://www.weibo.com/5041432467/PrVW67Sek#comment或 result2.csv")

        sel = ["请选择数据源", "已有数据集", "在线爬取数据集"]
        spy = st.radio("选择分析方式:", sel, horizontal=True)

        y = st.button("开始分析", key="dataset_analyze_btn")

        if y:
            if spy == "请选择数据源":
                st.warning("请先选择数据源类型")
            elif spy == "已有数据集":
                if not text:
                    st.error("请输入文件路径")
                else:
                    with st.spinner('正在分析数据集...'):
                        try:
                            text2 = dm2.reprocfun(text)
                            x = dm2.predict2(model, text2, cfggb)
                            cont, prov, date, like = dm2.da.ana()
                            emo = []
                            for i in cont:
                                x = dm2.predict2(model, i, cfggb)
                                emo.append(x)

                            if text == "":
                                text = "result2.csv"
                            mt.fun(text)

                            st.success("分析完成!请在导航菜单中选择数据分析结果查看可视化分析结果！")
                            with st.expander("📋 查看评论数据", expanded=True):
                                df1 = pd.read_csv(text)
                                st.dataframe(df1, width=1500)

                            f11 = open("mid.txt", 'w+', encoding="utf-8")
                            f11.write(text)
                            st.balloons()
                        except Exception as e:
                            st.error(f"分析出错: {str(e)}")
            else:
                if not text:
                    st.error("请输入微博链接")
                else:
                    with st.spinner('正在爬取和分析数据...'):
                        try:
                            f = open('result.csv', mode='w+', encoding='utf-8', newline='')
                            fieldnames = ['评论', '地区', '日期', '点赞', '情绪']
                            writer = csv.writer(f)
                            writer.writerow(fieldnames)

                            msg1 = dm2.sp.main(text)
                            cont, prov, date, like = dm2.da.ana()
                            emo = []
                            for i in cont:
                                x = dm2.predict2(model, i, cfggb)
                                emo.append(x)
                            for i in zip(cont, prov, date, like, emo):
                                writer.writerow([i[0], i[1], i[2], i[3], i[4]])
                            mt.fun()
                            cont = []
                            prov = []
                            date = []
                            like = []
                            emo = []

                            st.success("分析完成!请在导航菜单中选择数据分析结果查看可视化分析结果！")
                            with st.expander("📋 查看评论数据", expanded=True):
                                df1 = pd.read_csv("result.csv")
                                st.dataframe(df1, width=1500)

                            f22 = open("mid.txt", 'w+', encoding="utf-8")
                            f22.write("result.csv")
                            st.balloons()
                        except Exception as e:
                            st.error(f"分析出错: {str(e)}")

    elif la == "数据分析结果":
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50;">📈 数据分析结果</h1>
            <p style="color: #64748b;">可视化分析结果展示</p>
        </div>
        """, unsafe_allow_html=True)

        env = ["分析总览", "数据总览"]
        la2 = st.sidebar.selectbox("选择分析模块", env)

        if la2 == "分析总览":
            st.markdown("""
                    <div class="card">
                        <h3>📊 各省人数统计</h3>
                    </div>
                    """, unsafe_allow_html=True)
            with open("procnts.html") as fp2:
                text001 = fp2.read()
            components.html(text001, height=400, width=1200, scrolling=False)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # 情绪-点赞关系 - 单独一行
            st.markdown("""
                    <div class="card">
                        <h3>❤️ 情绪-点赞关系</h3>
                    </div>
                    """, unsafe_allow_html=True)
            with open("emolk.html") as fp1:
                text001 = fp1.read()
            components.html(text001, height=400, width=1200, scrolling=False)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # 情绪-地区折线图
            st.markdown("""
                    <div class="card">
                        <h3>🌍 情绪-地区分布</h3>
                    </div>
                    """, unsafe_allow_html=True)
            with open("nwpe.html") as fp3:
                text001 = fp3.read()
            components.html(text001, height=500, width=1200, scrolling=False)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # 情绪分布图表
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("""
                        <div class="card">
                            <h3>📡 情绪雷达图</h3>
                        </div>
                        """, unsafe_allow_html=True)
                with open("radar.html") as fp2:
                    text001 = fp2.read()
                components.html(text001, height=450, scrolling=False)

            with col4:
                st.markdown("""
                        <div class="card">
                            <h3>🍰 情绪饼图</h3>
                        </div>
                        """, unsafe_allow_html=True)
                with open("pie_rich_label.html") as fp2:
                    text001 = fp2.read()
                components.html(text001, height=450, scrolling=False)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # 地理分布与词云
            col5, col6 = st.columns(2)
            with col5:
                st.markdown("""
                        <div class="card">
                            <h3>🗺️ 评论地区热力图</h3>
                        </div>
                        """, unsafe_allow_html=True)
                with open("new_map.html") as fp2:
                    text001 = fp2.read()
                components.html(text001, height=600, scrolling=False)

            with col6:
                st.markdown("""
                        <div class="card">
                            <h3>☁️ 评论词云图</h3>
                        </div>
                        """, unsafe_allow_html=True)
                with open("wordcloud.html") as fp2:
                    text001 = fp2.read()
                components.html(text001, height=600, scrolling=False)

        elif la2 == "数据总览":
            st.markdown("""
            <div class="card">
                <h2>📋 原始数据</h2>
            </div>
            """, unsafe_allow_html=True)

            f11 = open("mid.txt", 'r', encoding="utf-8")
            flname = f11.readline()
            try:
                df1 = pd.read_csv(flname)
                st.dataframe(df1, width=1500, height=600)
            except Exception as e:
                st.error(f"加载数据出错: {str(e)}")
                st.info("请先在主界面完成数据分析")

            st.markdown("</div>", unsafe_allow_html=True)


main()