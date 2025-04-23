import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import accuracy_score, recall_score, f1_score
from pyspark.sql import SparkSession
from pyspark.sql.functions import split, col

# 屏蔽 TensorFlow 的 CUDA 警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 初始化 SparkSession，并指定 master 参数
spark = SparkSession.builder \
    .appName("SocialMediaSentimentAnalysis_GRU") \
    .getOrCreate()

# 读取数据，替换为完整的HDFS URI
data = spark.read.csv("hdfs://192.168.43.152:9000/social_data/processe_data.csv", header=True, inferSchema=True)

# 划分数据集
train_data, validation_data, test_data = data.randomSplit([0.7, 0.15, 0.15], seed=42)


def parse_features(features_str):
    """
    将 features_str 列中的数据解析为数值特征向量
    """
    pairs = features_str.split(',')
    feature_dict = {int(pair.split(':')[0]): float(pair.split(':')[1]) for pair in pairs if pair}
    return feature_dict


def convert_to_numpy(data, num_features):
    """
    将 PySpark DataFrame 转换为适合 TensorFlow 训练的 numpy 数组
    """
    features = data.select("features_str").rdd.map(lambda x: parse_features(x[0])).collect()
    labels = data.select("sentiment").rdd.map(lambda x: x[0]).collect()

    x = np.zeros((len(features), num_features))
    for i, feature in enumerate(features):
        for key, value in feature.items():
            x[i, key] = value
    y = np.array(labels)
    return x, y


# 计算整个数据集的特征数量
all_features = data.select("features_str").rdd.map(lambda x: parse_features(x[0])).collect()
max_feature_index = max(max(feature.keys()) for feature in all_features if feature)
num_features = max_feature_index + 1

# 转换数据
train_x, train_y = convert_to_numpy(train_data, num_features)
validation_x, validation_y = convert_to_numpy(validation_data, num_features)
test_x, test_y = convert_to_numpy(test_data, num_features)

# 调整输入形状以适应 GRU 模型
train_x = train_x.reshape(-1, num_features, 1)
validation_x = validation_x.reshape(-1, num_features, 1)
test_x = test_x.reshape(-1, num_features, 1)

# 构建改进后的模型
model = Sequential()
model.add(Bidirectional(GRU(64, return_sequences=True), input_shape=(num_features, 1)))
model.add(Dropout(0.2))
model.add(GRU(32, return_sequences=True))
model.add(Dropout(0.2))
model.add(GRU(16))
model.add(Dropout(0.2))
model.add(Dense(16, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))

# 编译模型，使用学习率调度器
optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

# 早停机制和学习率调度器
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=0.00001)

# 训练模型，调整批量大小
num_epochs = 50
batch_size = 32
history = model.fit(train_x, train_y, epochs=num_epochs, batch_size=batch_size,
                    validation_data=(validation_x, validation_y), callbacks=[early_stopping, reduce_lr])

# 评估模型，根据实际情况选择合适的average参数，这里假设是多分类问题选择'micro'
predictions = model.predict(test_x).round()
accuracy = accuracy_score(test_y, predictions)
recall = recall_score(test_y, predictions, average='micro')
f1 = f1_score(test_y, predictions, average='micro')

print(f"准确率: {accuracy}")
print(f"召回率: {recall}")
print(f"F1值: {f1}")

# 关闭 SparkSession
try:
    spark.stop()
except Exception as e:
    print(f"关闭 SparkSession 时出现错误: {e}")
