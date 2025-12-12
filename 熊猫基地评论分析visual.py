import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import seaborn as sns
import numpy as np
from textblob import TextBlob
import jieba
import jieba.analyse
from wordcloud import WordCloud
from collections import Counter
import re
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# ====== 1. 中文字体配置 ======
print("正在配置中文字体...")

font_paths = [
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simsun.ttc',
]

chosen_font = None
for font_path in font_paths:
    if os.path.exists(font_path):
        chosen_font = font_path
        print(f"找到字体: {font_path}")
        break

if chosen_font:
    font_prop = font_manager.FontProperties(fname=chosen_font)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['font.sans-serif'] = [font_prop.get_name(), 'SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    chinese_ok = True
    print("中文字体配置成功")
else:
    chinese_ok = False
    print("使用英文标签")

def get_label(chinese, english):
    return chinese if chinese_ok else english

# ====== 2. 数据读取和预处理 ======
try:
    file_path = 'C:/Users/lenovo/Desktop/携程评论-熊猫基地/全部评论清洗后.csv'
    df = pd.read_csv(file_path, encoding='utf-8')
    print(f"数据读取成功！形状：{df.shape}")
except Exception as e:
    print(f"文件读取失败：{e}")
    exit()

# ====== 3. 情感分析 ======
print("正在进行情感分析...")

def analyze_sentiment(text):
    if pd.isna(text):
        return 0
    try:
        analysis = TextBlob(str(text))
        return analysis.sentiment.polarity
    except:
        return 0

df['sentiment'] = df['评论内容'].apply(analyze_sentiment)

def sentiment_category(score):
    if score > 0.1:
        return get_label('正面', 'Positive')
    elif score < -0.1:
        return get_label('负面', 'Negative')
    else:
        return get_label('中性', 'Neutral')

df['sentiment_category'] = df['sentiment'].apply(sentiment_category)

# 情感强度
df['sentiment_strength'] = df['sentiment'].abs()

# ====== 4. 文本分析 ======
print("正在进行文本分析...")

def extract_chinese_keywords(text, topK=10):
    if pd.isna(text):
        return []
    try:
        text_clean = re.sub(r'[^\u4e00-\u9fa5]', ' ', str(text))
        keywords = jieba.analyse.extract_tags(text_clean, topK=topK)
        return keywords
    except:
        return []

# 评论长度分析
df['comment_length'] = df['评论内容'].str.len()
df['word_count'] = df['评论内容'].str.split().str.len()

# ====== 5. 时间分析 ======
print("正在进行时间分析...")

try:
    df['发布时间'] = pd.to_datetime(df['发布时间'])
    df['year'] = df['发布时间'].dt.year
    df['month'] = df['发布时间'].dt.month
    df['year_month'] = df['发布时间'].dt.to_period('M')
    df['hour'] = df['发布时间'].dt.hour
    df['day_of_week'] = df['发布时间'].dt.dayofweek
    time_analysis = True
except:
    time_analysis = False
    print("时间分析跳过")

# ====== 6. 开始生成图表 ======
print("开始生成可视化图表...")

# 图表1: 综合评分分布雷达图
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
categories = ['总评分', '景色评分', '趣味评分', '性价比评分']
values = df[categories].mean().values
values = np.append(values, values[0])

angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

ax.plot(angles, values, 'o-', linewidth=2, label=get_label('平均评分', 'Average Rating'))
ax.fill(angles, values, alpha=0.25)
ax.set_xticks(angles[:-1])
ax.set_xticklabels([get_label('总体', 'Overall'), get_label('景色', 'Scenery'), 
                   get_label('趣味', 'Fun'), get_label('性价比', 'Value')])
ax.set_ylim(0, 5)
ax.set_title(get_label('各维度评分雷达图', 'Rating Radar Chart'), size=14, pad=20)
plt.tight_layout()
plt.savefig('01_rating_radar.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表1: 评分雷达图 完成")

# 图表2: 情感分布三维分析
fig = plt.figure(figsize=(15, 5))

# 情感类别分布
plt.subplot(131)
sentiment_counts = df['sentiment_category'].value_counts()
colors = ['#4CAF50', '#FF9800', '#F44336']
plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', 
        colors=colors, startangle=90)
plt.title(get_label('情感类别分布', 'Sentiment Category Distribution'))

# 情感分数分布
plt.subplot(132)
plt.hist(df['sentiment'], bins=50, color='#2196F3', alpha=0.7, edgecolor='black')
plt.axvline(x=0, color='red', linestyle='--', alpha=0.7, label=get_label('中性分界线', 'Neutral Line'))
plt.xlabel(get_label('情感分数', 'Sentiment Score'))
plt.ylabel(get_label('频率', 'Frequency'))
plt.title(get_label('情感分数分布', 'Sentiment Score Distribution'))
plt.legend()

# 情感强度分布
plt.subplot(133)
plt.hist(df['sentiment_strength'], bins=30, color='#9C27B0', alpha=0.7, edgecolor='black')
plt.xlabel(get_label('情感强度', 'Sentiment Strength'))
plt.ylabel(get_label('频率', 'Frequency'))
plt.title(get_label('情感强度分布', 'Sentiment Strength Distribution'))

plt.tight_layout()
plt.savefig('02_sentiment_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表2: 情感分析 完成")

# 图表3: 用户等级与情感关系
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 用户等级分布
user_level_order = ['', '黄金贵宾', '铂金贵宾', '钻石贵宾', '黑钻贵宾']
user_level_counts = df['用户等级'].value_counts().reindex(user_level_order, fill_value=0)
ax1.bar(range(len(user_level_counts)), user_level_counts.values, color='teal', alpha=0.7)
ax1.set_xticks(range(len(user_level_counts)))
ax1.set_xticklabels(user_level_counts.index, rotation=45)
ax1.set_xlabel(get_label('用户等级', 'User Level'))
ax1.set_ylabel(get_label('评论数量', 'Comment Count'))
ax1.set_title(get_label('用户等级分布', 'User Level Distribution'))

# 用户等级与情感关系
sns.boxplot(data=df, x='用户等级', y='sentiment', order=user_level_order, ax=ax2, palette='Set2')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
ax2.set_xlabel(get_label('用户等级', 'User Level'))
ax2.set_ylabel(get_label('情感分数', 'Sentiment Score'))
ax2.set_title(get_label('各用户等级情感分布', 'Sentiment by User Level'))

plt.tight_layout()
plt.savefig('03_user_level_sentiment.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表3: 用户等级分析 完成")

# 图表4: 评论长度与情感关系
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 评论长度分布
ax1.hist(df['comment_length'], bins=50, color='orange', alpha=0.7, edgecolor='black')
ax1.set_xlabel(get_label('评论长度（字符数）', 'Comment Length (Characters)'))
ax1.set_ylabel(get_label('频率', 'Frequency'))
ax1.set_title(get_label('评论长度分布', 'Comment Length Distribution'))

# 评论长度与情感关系
ax2.scatter(df['comment_length'], df['sentiment'], alpha=0.5, color='purple', s=20)
ax2.set_xlabel(get_label('评论长度（字符数）', 'Comment Length (Characters)'))
ax2.set_ylabel(get_label('情感分数', 'Sentiment Score'))
ax2.set_title(get_label('评论长度与情感关系', 'Comment Length vs Sentiment'))
ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('04_comment_length_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表4: 评论长度分析 完成")

# 图表5: 图片数量分析
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 图片数量分布
image_counts = df['图片数量'].value_counts().sort_index()
ax1.bar(image_counts.index, image_counts.values, color='brown', alpha=0.7)
ax1.set_xlabel(get_label('图片数量', 'Number of Images'))
ax1.set_ylabel(get_label('评论数量', 'Comment Count'))
ax1.set_title(get_label('评论附带图片数量分布', 'Image Count Distribution'))

# 图片数量与评分关系
sns.boxplot(data=df[df['图片数量'] <= 10], x='图片数量', y='总评分', ax=ax2, palette='viridis')
ax2.set_xlabel(get_label('图片数量', 'Number of Images'))
ax2.set_ylabel(get_label('总评分', 'Overall Rating'))
ax2.set_title(get_label('图片数量与评分关系', 'Images vs Rating'))

plt.tight_layout()
plt.savefig('05_image_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表5: 图片分析 完成")

# 图表6: 时间趋势分析（如果时间数据可用）
if time_analysis:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 年度趋势
    yearly_stats = df.groupby('year').agg({
        '总评分': 'mean',
        'sentiment': 'mean',
        '评论内容': 'count'
    }).reset_index()
    
    ax1.plot(yearly_stats['year'], yearly_stats['总评分'], marker='o', linewidth=2, label=get_label('平均评分', 'Avg Rating'))
    ax1.set_xlabel(get_label('年份', 'Year'))
    ax1.set_ylabel(get_label('平均评分', 'Average Rating'))
    ax1.set_title(get_label('评分年度趋势', 'Rating Trend by Year'))
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 情感年度趋势
    ax2.plot(yearly_stats['year'], yearly_stats['sentiment'], marker='s', linewidth=2, color='red', label=get_label('平均情感', 'Avg Sentiment'))
    ax2.set_xlabel(get_label('年份', 'Year'))
    ax2.set_ylabel(get_label('平均情感分数', 'Average Sentiment Score'))
    ax2.set_title(get_label('情感年度趋势', 'Sentiment Trend by Year'))
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 评论数量月度分布
    monthly_counts = df.groupby('month').size()
    ax3.bar(monthly_counts.index, monthly_counts.values, color='green', alpha=0.7)
    ax3.set_xlabel(get_label('月份', 'Month'))
    ax3.set_ylabel(get_label('评论数量', 'Comment Count'))
    ax3.set_title(get_label('评论数量月度分布', 'Monthly Comment Distribution'))
    
    # 小时分布
    hourly_counts = df.groupby('hour').size()
    ax4.bar(hourly_counts.index, hourly_counts.values, color='purple', alpha=0.7)
    ax4.set_xlabel(get_label('小时', 'Hour'))
    ax4.set_ylabel(get_label('评论数量', 'Comment Count'))
    ax4.set_title(get_label('评论发布时间分布', 'Comment Time Distribution'))
    
    plt.tight_layout()
    plt.savefig('06_time_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("图表6: 时间分析 完成")

# 图表7: 发布地点分析
plt.figure(figsize=(12, 8))
location_counts = df['发布地点'].value_counts().head(15)
plt.barh(location_counts.index, location_counts.values, color='lightseagreen', alpha=0.7)
plt.xlabel(get_label('评论数量', 'Comment Count'))
plt.ylabel(get_label('发布地点', 'Location'))
plt.title(get_label('评论发布地点分布（前15）', 'Comment Location Distribution (Top 15)'))
plt.tight_layout()
plt.savefig('07_location_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表7: 地点分布 完成")

# 图表8: 情感与各维度评分关系
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes = axes.flatten()

rating_columns = ['总评分', '景色评分', '趣味评分', '性价比评分']
colors = ['blue', 'green', 'orange', 'red']

for i, col in enumerate(rating_columns):
    axes[i].scatter(df[col], df['sentiment'], alpha=0.5, color=colors[i], s=20)
    axes[i].set_xlabel(get_label(f'{col}分', f'{col} Rating'))
    axes[i].set_ylabel(get_label('情感分数', 'Sentiment Score'))
    axes[i].set_title(get_label(f'{col}与情感关系', f'{col} vs Sentiment'))
    axes[i].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('08_rating_sentiment_correlation.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表8: 评分情感关系 完成")

# 图表9: 情感强度分析
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 情感强度分布
sentiment_bins = pd.cut(df['sentiment_strength'], bins=[0, 0.1, 0.3, 0.5, 1.0], 
                       labels=[get_label('微弱', 'Weak'), get_label('中等', 'Medium'), 
                              get_label('强烈', 'Strong'), get_label('非常强烈', 'Very Strong')])
strength_counts = sentiment_bins.value_counts()

ax1.bar(strength_counts.index.astype(str), strength_counts.values, color=['#FFEB3B', '#FF9800', '#F44336', '#B71C1C'], alpha=0.7)
ax1.set_xlabel(get_label('情感强度等级', 'Sentiment Strength Level'))
ax1.set_ylabel(get_label('评论数量', 'Comment Count'))
ax1.set_title(get_label('情感强度分布', 'Sentiment Strength Distribution'))
ax1.tick_params(axis='x', rotation=45)

# 情感强度与评论长度关系
ax2.scatter(df['sentiment_strength'], df['comment_length'], alpha=0.5, color='teal', s=20)
ax2.set_xlabel(get_label('情感强度', 'Sentiment Strength'))
ax2.set_ylabel(get_label('评论长度', 'Comment Length'))
ax2.set_title(get_label('情感强度与评论长度关系', 'Sentiment Strength vs Comment Length'))

plt.tight_layout()
plt.savefig('09_sentiment_strength_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表9: 情感强度分析 完成")

# 图表10: 综合热力图
plt.figure(figsize=(12, 8))
correlation_data = df[['总评分', '景色评分', '趣味评分', '性价比评分', 'sentiment', 'sentiment_strength', 'comment_length', '图片数量']].corr()
sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, fmt='.2f', 
            square=True, cbar_kws={"shrink": .8})
plt.title(get_label('变量相关性热力图', 'Variable Correlation Heatmap'))
plt.tight_layout()
plt.savefig('10_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表10: 相关性热力图 完成")

# 图表11: 点赞数分析
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 点赞数分布（对数尺度）
ax1.hist(df['点赞数'] + 1, bins=50, color='gold', alpha=0.7, edgecolor='black', log=True)
ax1.set_xlabel(get_label('点赞数+1（对数尺度）', 'Likes + 1 (Log Scale)'))
ax1.set_ylabel(get_label('频率', 'Frequency'))
ax1.set_title(get_label('点赞数分布', 'Likes Distribution'))

# 高点赞评论情感分析
high_like_threshold = df['点赞数'].quantile(0.9)
high_like_comments = df[df['点赞数'] > high_like_threshold]

if len(high_like_comments) > 0:
    ax2.hist(high_like_comments['sentiment'], bins=20, color='red', alpha=0.7, edgecolor='black')
    ax2.set_xlabel(get_label('情感分数', 'Sentiment Score'))
    ax2.set_ylabel(get_label('频率', 'Frequency'))
    ax2.set_title(get_label('高点赞评论情感分布', 'High-Like Comments Sentiment'))
else:
    ax2.text(0.5, 0.5, get_label('高点赞评论数据不足', 'Insufficient high-like comments'), 
            ha='center', va='center', transform=ax2.transAxes)

plt.tight_layout()
plt.savefig('11_likes_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表11: 点赞分析 完成")

# 图表12: 情感类别详细分析
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 各情感类别的评分分布
for i, sentiment_type in enumerate(df['sentiment_category'].unique()):
    sentiment_data = df[df['sentiment_category'] == sentiment_type]
    axes[0, 0].hist(sentiment_data['总评分'], bins=10, alpha=0.6, 
                   label=get_label(sentiment_type, sentiment_type), density=True)
axes[0, 0].set_xlabel(get_label('总评分', 'Overall Rating'))
axes[0, 0].set_ylabel(get_label('密度', 'Density'))
axes[0, 0].set_title(get_label('各情感类别评分分布', 'Rating Distribution by Sentiment'))
axes[0, 0].legend()

# 各情感类别的评论长度
sns.boxplot(data=df, x='sentiment_category', y='comment_length', ax=axes[0, 1], palette='Set3')
axes[0, 1].set_xlabel(get_label('情感类别', 'Sentiment Category'))
axes[0, 1].set_ylabel(get_label('评论长度', 'Comment Length'))
axes[0, 1].set_title(get_label('各情感类别评论长度', 'Comment Length by Sentiment'))

# 各情感类别的用户等级分布
sentiment_user_counts = pd.crosstab(df['sentiment_category'], df['用户等级'], normalize='index')
sentiment_user_counts.plot(kind='bar', stacked=True, ax=axes[1, 0], colormap='viridis')
axes[1, 0].set_xlabel(get_label('情感类别', 'Sentiment Category'))
axes[1, 0].set_ylabel(get_label('比例', 'Proportion'))
axes[1, 0].set_title(get_label('各情感类别用户等级分布', 'User Level Distribution by Sentiment'))
axes[1, 0].legend(title=get_label('用户等级', 'User Level'))

# 各情感类别的图片数量
sns.boxplot(data=df[df['图片数量'] <= 10], x='sentiment_category', y='图片数量', ax=axes[1, 1], palette='Set2')
axes[1, 1].set_xlabel(get_label('情感类别', 'Sentiment Category'))
axes[1, 1].set_ylabel(get_label('图片数量', 'Number of Images'))
axes[1, 1].set_title(get_label('各情感类别图片数量', 'Image Count by Sentiment'))

plt.tight_layout()
plt.savefig('12_detailed_sentiment_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("图表12: 详细情感分析 完成")

# ====== 7. 生成分析报告 ======
print("\n" + "="*50)
print("可视化分析完成！")
print(f"共生成 {12 if time_analysis else 11} 个分析图表")
print("\n生成的图表文件：")
chart_files = [f for f in os.listdir('.') if f.endswith('.png') and f[:2].isdigit()]
for chart in sorted(chart_files):
    print(f"  - {chart}")

print(f"\n数据分析摘要：")
print(f"总评论数: {len(df)}")
print(f"平均评分: {df['总评分'].mean():.2f}")
print(f"平均情感分数: {df['sentiment'].mean():.3f}")
print(f"情感分布: {dict(df['sentiment_category'].value_counts())}")
print(f"正面评论比例: {(df['sentiment_category'] == get_label('正面', 'Positive')).mean()*100:.1f}%")