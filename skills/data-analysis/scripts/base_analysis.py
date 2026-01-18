"""
基础数据分析脚本

参数：
    file: 输入的CSV文件路径
"""

import sys
import pandas as pd
import numpy as np

file = sys.argv[1]

# 加载数据 判断文件类型
if file.endswith('.csv'):
    df = pd.read_csv(file)
elif file.endswith('.xlsx'):
    df = pd.read_excel(file)
elif file.endswith('.json'):
    df = pd.read_json(file)
else:
    raise ValueError("不支持的文件类型。请提供CSV、Excel或JSON文件。")

# 数据概览
print("=== 数据概览 ===")
print(f"数据集形状: {df.shape}")
print(f"列数: {df.shape[1]}")
print(f"行数: {df.shape[0]}")

print("\n=== 列名 ===")
print(df.columns.tolist())

print("\n=== 数据类型 ===")
print(df.dtypes)

print("\n=== 前5行样本 ===")
print(df.head())

print("\n=== 数值列统计摘要 ===")
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    print(df[numeric_cols].describe())
else:
    print("无数值列")

print("\n=== 分类列统计摘要 ===")
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols[:5]:  # 限制前5个分类列
    print(f"\n{col} 唯一值计数:")
    print(df[col].value_counts().head(10))

print("\n=== 缺失值统计 ===")
missing = df.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0])
else:
    print("无缺失值")

print("\n=== 数据质量检查 ===")
# 检查重复行
duplicates = df.duplicated().sum()
print(f"重复行数: {duplicates}")

# 检查异常值（对于数值列）
for col in numeric_cols[:3]:  # 限制前3个数值列
    if df[col].dtype in ['int64', 'float64']:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()
        print(f"{col} 异常值数: {outliers}")
