from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, split, col
from pyspark.sql.types import StringType, IntegerType, ArrayType, DoubleType
import jieba
import re

# 初始化SparkSession
spark = SparkSession.builder \
    .appName("SocialMediaProcessing") \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.cores", "4") \
    .config("spark.executor.heartbeatInterval", "30s") \
    .getOrCreate()

# 设置日志级别（可选）
spark.sparkContext.setLogLevel("ERROR")

# 1. 数据加载
df = spark.read.csv(
    "hdfs:///social_data/test2.csv",
    header=True,
    inferSchema=True,
    multiLine=True,
    encoding="utf-8"
)

# 确保数据加载成功
print(f"Number of rows in input data: {df.count()}")
df.show(5)


# 2. 文本清洗函数
def clean_text(text):
    if not text:
        return ""
    # 去除URL
    text = re.sub(r'http\S+', '', text)
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去除表情符号（如[嘻嘻]）
    text = re.sub(r'$.*?$', '', text)
    # 去除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return text.strip()


clean_udf = udf(clean_text, StringType())


# 3. 中文分词函数（使用jieba）
def chinese_segment(text):
    return " ".join(jieba.cut(text)) if text else ""


segment_udf = udf(chinese_segment, StringType())

# 4. 停用词过滤
stopwords_rdd = spark.sparkContext.textFile("hdfs:///social_data/stopwords.txt")
stopwords = set(stopwords_rdd.collect())


def remove_stopwords(text):
    return " ".join([word for word in text.split() if word not in stopwords])


stopwords_udf = udf(remove_stopwords, StringType())


# 5. 情感倾向标注（示例：简单规则匹配）
def sentiment_label(text):
    positive_words = ['好', '棒', '支持', '加油']
    negative_words = ['垃圾', '恶心', '没必要']
    if any(word in text for word in positive_words):
        return 1
    elif any(word in text for word in negative_words):
        return -1
    return 0


sentiment_udf = udf(sentiment_label, IntegerType())

# 执行处理流程
processed_df = df.withColumn("cleaned_text", clean_udf(col("comments"))) \
    .withColumn("segmented_text", segment_udf(col("cleaned_text"))) \
    .withColumn("filtered_text", stopwords_udf(col("segmented_text"))) \
    .withColumn("sentiment", sentiment_udf(col("cleaned_text")))

# 将filtered_text列从字符串类型转换为数组类型
processed_df = processed_df.withColumn("filtered_text_array", split(processed_df["filtered_text"], " "))

# 6. 特征向量化（TF-IDF示例）
from pyspark.ml.feature import HashingTF, IDF

hashingTF = HashingTF(inputCol="filtered_text_array", outputCol="raw_features", numFeatures=1000)
idf = IDF(inputCol="raw_features", outputCol="features")

tf_df = hashingTF.transform(processed_df)
tfidf_df = idf.fit(tf_df).transform(tf_df)

# 选择需要保存的列
result_df = tfidf_df.select(
    col("comments"),
    col("cleaned_text"),
    col("filtered_text"),
    col("sentiment"),
    col("features")
)

# 将features列转换为字符串表示
@udf(StringType())
def vector_to_string(vector):
    if vector and hasattr(vector, "indices") and hasattr(vector, "values"):
        indices = vector.indices
        values = vector.values
        return ",".join([f"{i}:{v}" for i, v in zip(indices, values)])
    return ""


final_df = result_df.withColumn("features_str", vector_to_string(col("features"))).drop("features")

# 确保输出内容没有乱码
print(f"Number of rows in final_df: {final_df.count()}")
final_df.show(truncate=False)

# 7. 保存为CSV文件
final_df.write.csv(
    "hdfs:///social_data/processed_data.csv",
    header=True,
    sep=",",
    encoding="utf-8",
    mode="overwrite"
)

# 关闭Spark
spark.stop()