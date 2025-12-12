import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和图表参数
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.autolayout'] = True  # 自动调整布局

print("=== 开始生成完整版可视化图表 ===")

# 读取数据
df = pd.read_csv('携程景点数据.csv')
print(f"✅ 成功读取数据：{len(df)} 个景点")

def preprocess_data(df):
    df_clean = df.copy()
    df_clean['热度分'] = pd.to_numeric(df_clean['热度分'], errors='coerce')
    df_clean['评论数量'] = pd.to_numeric(df_clean['评论数量'], errors='coerce')
    df_clean['评分'] = pd.to_numeric(df_clean['评分'], errors='coerce')
    df_clean['门票价格_清洗'] = pd.to_numeric(df_clean['门票价格'], errors='coerce')
    df_clean['景区等级_清洗'] = df_clean['景区等级'].fillna('无等级')
    df_clean['标签列表'] = df_clean['标签'].str.split('、')
    df_clean['是否免费_bool'] = df_clean['是否免费'] == '是'
    
    # 处理距离
    def extract_distance(distance_str):
        if pd.isna(distance_str):
            return np.nan
        if 'km' in str(distance_str):
            try:
                return float(str(distance_str).replace('距市中心', '').replace('km', '').strip())
            except:
                return np.nan
        elif 'm' in str(distance_str):
            try:
                return float(str(distance_str).replace('距市中心', '').replace('m', '').strip()) / 1000
            except:
                return np.nan
        else:
            return np.nan
    
    df_clean['距离市中心_km'] = df_clean['距离市中心'].apply(extract_distance)
    return df_clean

df = preprocess_data(df)
print(f"数据预处理完成，共 {len(df)} 个景点")

# 1. 🎯 单独的热度TOP20图表
print("生成图表1: 热度TOP20...")
plt.figure(figsize=(14, 10))
top20 = df.nlargest(20, '热度分')
bars = plt.barh(range(len(top20)), top20['热度分'], color='skyblue', alpha=0.8)

# 优化Y轴标签
plt.yticks(range(len(top20)), top20['景点名称'], fontsize=9)
plt.xlabel('热度分', fontsize=12)
plt.title('成都热门景点TOP20', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()
plt.grid(axis='x', alpha=0.3)

# 在条形上添加数值
for i, (bar, value) in enumerate(zip(bars, top20['热度分'])):
    plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
             f'{value:.1f}', va='center', ha='left', fontsize=8)

plt.tight_layout()
plt.savefig('1_热度TOP20.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表1保存完成")

# 2. 📊 单独的等级分布图表
print("生成图表2: 等级分布...")
plt.figure(figsize=(12, 8))

# 子图1: 等级数量分布
plt.subplot(1, 2, 1)
grade_count = df['景区等级_清洗'].value_counts()
colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
plt.pie(grade_count.values, labels=grade_count.index, autopct='%1.1f%%', 
        startangle=90, colors=colors[:len(grade_count)], textprops={'fontsize': 10})
plt.title('景点等级分布', fontsize=12, fontweight='bold')

# 子图2: 各等级平均热度
plt.subplot(1, 2, 2)
grade_heat = df.groupby('景区等级_清洗')['热度分'].mean().sort_values(ascending=False)
bars = plt.bar(grade_heat.index, grade_heat.values, color=colors[:len(grade_heat)], alpha=0.8)
plt.title('各等级景点平均热度', fontsize=12, fontweight='bold')
plt.ylabel('平均热度分')
plt.xticks(rotation=45)

for bar, value in zip(bars, grade_heat.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
             f'{value:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('2_等级分布分析.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表2保存完成")

# 3. 💰 单独的价格分析图表
print("生成图表3: 价格分析...")
plt.figure(figsize=(15, 10))

# 子图1: 免费vs收费
plt.subplot(2, 2, 1)
free_count = df['是否免费'].value_counts()
plt.pie(free_count.values, labels=free_count.index, autopct='%1.1f%%', 
        colors=['lightgreen', 'lightcoral'], startangle=90, textprops={'fontsize': 10})
plt.title('免费vs收费景点分布', fontweight='bold')

# 子图2: 价格分布
plt.subplot(2, 2, 2)
paid_df = df[df['门票价格_清洗'] > 0]
plt.hist(paid_df['门票价格_清洗'], bins=20, edgecolor='black', alpha=0.7, color='lightblue')
plt.xlabel('门票价格(元)')
plt.ylabel('景点数量')
plt.title('收费景点价格分布', fontweight='bold')
plt.grid(alpha=0.3)

# 子图3: 价格与热度关系
plt.subplot(2, 2, 3)
scatter = plt.scatter(df['门票价格_清洗'], df['热度分'], alpha=0.6, 
                     c=df['评分'], cmap='viridis', s=50)
plt.colorbar(scatter, label='评分')
plt.xlabel('门票价格(元)')
plt.ylabel('热度分')
plt.title('门票价格 vs 热度分', fontweight='bold')
plt.grid(True, alpha=0.3)

# 子图4: 免费vs收费热度对比
plt.subplot(2, 2, 4)
free_heat = df[df['是否免费_bool']]['热度分'].mean()
paid_heat = df[~df['是否免费_bool']]['热度分'].mean()
bars = plt.bar(['免费景点', '收费景点'], [free_heat, paid_heat], 
               color=['lightgreen', 'lightcoral'], alpha=0.8)
plt.ylabel('平均热度分')
plt.title('免费vs收费景点平均热度', fontweight='bold')

for bar, value in zip(bars, [free_heat, paid_heat]):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
             f'{value:.1f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('3_价格分析.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表3保存完成")

# 4. 🏷️ 单独的标签分析图表
print("生成图表4: 标签分析...")

# 提取所有标签
all_tags = []
for tags in df['标签列表'].dropna():
    if isinstance(tags, list):
        all_tags.extend(tags)

tag_freq = Counter(all_tags)

plt.figure(figsize=(14, 10))

# 子图1: 热门标签
plt.subplot(2, 1, 1)
top_tags = pd.Series(tag_freq).nlargest(12)
bars = plt.barh(top_tags.index, top_tags.values, color='lightseagreen', alpha=0.8)
plt.xlabel('出现次数')
plt.title('TOP12热门标签', fontweight='bold')
plt.gca().invert_yaxis()

for bar, value in zip(bars, top_tags.values):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{value}', va='center', ha='left', fontsize=9)

# 子图2: 标签与热度关系
plt.subplot(2, 1, 2)
tag_heat_data = []
for tag in top_tags.index[:8]:
    mask = df['标签'].str.contains(tag, na=False)
    if mask.any():
        avg_heat = df[mask]['热度分'].mean()
        tag_heat_data.append((tag, avg_heat))

if tag_heat_data:
    tag_heat_data.sort(key=lambda x: x[1], reverse=True)
    tags, heats = zip(*tag_heat_data)
    bars = plt.bar(tags, heats, color='coral', alpha=0.8)
    plt.ylabel('平均热度分')
    plt.title('热门标签对应的平均热度', fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    for bar, value in zip(bars, heats):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                 f'{value:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('4_标签分析.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表4保存完成")

# 5. ⭐ 单独的评分分析图表
print("生成图表5: 评分分析...")
plt.figure(figsize=(15, 10))

# 子图1: 评分分布
plt.subplot(2, 2, 1)
valid_ratings = df['评分'].dropna()
plt.hist(valid_ratings, bins=15, edgecolor='black', alpha=0.7, color='gold')
plt.xlabel('评分')
plt.ylabel('景点数量')
plt.title('景点评分分布', fontweight='bold')
plt.grid(alpha=0.3)

# 子图2: 评分vs热度
plt.subplot(2, 2, 2)
valid_data = df[['评分', '热度分']].dropna()
if len(valid_data) > 0:
    plt.scatter(valid_data['评分'], valid_data['热度分'], alpha=0.6, color='purple', s=50)
    plt.xlabel('评分')
    plt.ylabel('热度分')
    plt.title('评分 vs 热度分', fontweight='bold')
    plt.grid(True, alpha=0.3)

# 子图3: 评论数量分析
plt.subplot(2, 2, 3)
valid_comments = df[['评论数量', '热度分', '评分']].dropna()
if len(valid_comments) > 0:
    scatter = plt.scatter(np.log1p(valid_comments['评论数量']), valid_comments['热度分'], 
                        alpha=0.6, c=valid_comments['评分'], cmap='coolwarm', s=50)
    plt.colorbar(label='评分')
    plt.xlabel('评论数量(对数尺度)')
    plt.ylabel('热度分')
    plt.title('评论数量 vs 热度分', fontweight='bold')
    plt.grid(True, alpha=0.3)

# 子图4: 高评分景点TOP8
plt.subplot(2, 2, 4)
top_rated = df.nlargest(8, '评分')
if len(top_rated) > 0:
    plt.barh(range(len(top_rated)), top_rated['评分'], color='lightgreen', alpha=0.8)
    plt.yticks(range(len(top_rated)), top_rated['景点名称'], fontsize=8)
    plt.xlabel('评分')
    plt.title('高评分景点TOP8', fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('5_评分分析.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表5保存完成")

# 6. 🗺️ 单独的地理分布分析图表
print("生成图表6: 地理分布分析...")
plt.figure(figsize=(15, 12))

# 子图1: 区域热度分析
plt.subplot(2, 2, 1)
region_heat = df.groupby('区域名称')['热度分'].mean().nlargest(15)
if len(region_heat) > 0:
    bars = plt.barh(region_heat.index, region_heat.values, color='orange', alpha=0.8)
    plt.xlabel('平均热度分')
    plt.title('各区域景点平均热度TOP15', fontweight='bold')
    plt.gca().invert_yaxis()
    
    for bar, value in zip(bars, region_heat.values):
        plt.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, 
                 f'{value:.1f}', va='center', ha='left', fontsize=9)

# 子图2: 距离市中心分析
plt.subplot(2, 2, 2)
valid_distances = df['距离市中心_km'].dropna()
if len(valid_distances) > 0:
    plt.hist(valid_distances, bins=20, edgecolor='black', alpha=0.7, color='lightblue')
    plt.xlabel('距离市中心(km)')
    plt.ylabel('景点数量')
    plt.title('景点距离市中心分布', fontweight='bold')
    plt.grid(alpha=0.3)

# 子图3: 距离vs热度
plt.subplot(2, 2, 3)
valid_dist_heat = df[['距离市中心_km', '热度分', '评分']].dropna()
if len(valid_dist_heat) > 0:
    scatter = plt.scatter(valid_dist_heat['距离市中心_km'], valid_dist_heat['热度分'], 
                        alpha=0.6, c=valid_dist_heat['评分'], cmap='plasma', s=50)
    plt.colorbar(scatter, label='评分')
    plt.xlabel('距离市中心(km)')
    plt.ylabel('热度分')
    plt.title('距离 vs 热度分', fontweight='bold')
    plt.grid(True, alpha=0.3)

# 子图4: 各城市景点分布
plt.subplot(2, 2, 4)
city_count = df['所在城市'].value_counts()
if len(city_count) > 0:
    plt.pie(city_count.values, labels=city_count.index, autopct='%1.1f%%', 
            startangle=90, colors=sns.color_palette('Set3'), textprops={'fontsize': 9})
    plt.title('各城市景点分布', fontweight='bold')

plt.tight_layout()
plt.savefig('6_地理分布分析.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表6保存完成")

# 7. 📈 单独的综合关联分析图表
print("生成图表7: 综合关联分析...")
plt.figure(figsize=(16, 12))

# 子图1: 多变量关联热力图
plt.subplot(2, 2, 1)
corr_columns = ['热度分', '评论数量', '评分', '门票价格_清洗', '距离市中心_km']
corr_data = df[corr_columns].dropna()
if len(corr_data) > 0:
    corr_matrix = corr_data.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True, 
                fmt='.2f', cbar_kws={'shrink': 0.8})
    plt.title('景点特征关联热力图', fontweight='bold')

# 子图2: 价格与热度关系（按等级分类）
plt.subplot(2, 2, 2)
valid_price_heat = df[['门票价格_清洗', '热度分', '景区等级_清洗']].dropna()
if len(valid_price_heat) > 0:
    for level in valid_price_heat['景区等级_清洗'].unique():
        level_data = valid_price_heat[valid_price_heat['景区等级_清洗'] == level]
        plt.scatter(level_data['门票价格_清洗'], level_data['热度分'], 
                   alpha=0.6, label=level, s=50)
    plt.xlabel('门票价格(元)')
    plt.ylabel('热度分')
    plt.title('价格vs热度（按等级分类）', fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)

# 子图3: 景点类型分析
plt.subplot(2, 2, 3)
def classify_attraction(tags):
    if not isinstance(tags, list):
        return '其他'
    tags_str = '、'.join(tags)
    if '博物馆' in tags_str or '展馆' in tags_str:
        return '博物馆展馆'
    elif '演出' in tags_str or '演唱会' in tags_str or '剧院' in tags_str:
        return '演出娱乐'
    elif '古镇' in tags_str or '历史建筑' in tags_str:
        return '古镇历史'
    elif '自然' in tags_str or '山水' in tags_str or '公园' in tags_str:
        return '自然风光'
    elif '动物园' in tags_str or '熊猫' in tags_str:
        return '动物相关'
    elif '乐园' in tags_str or '游乐场' in tags_str:
        return '主题乐园'
    else:
        return '其他'

df['景点类型'] = df['标签列表'].apply(classify_attraction)
type_analysis = df.groupby('景点类型').agg({
    '热度分': 'mean',
    '景点名称': 'count'
}).rename(columns={'景点名称': '数量'}).sort_values('热度分', ascending=False)

if len(type_analysis) > 0:
    x = range(len(type_analysis))
    width = 0.35
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    bars1 = ax1.bar(x, type_analysis['热度分'], width, alpha=0.7, 
                   color='lightgreen', label='平均热度')
    line2 = ax2.plot(x, type_analysis['数量'], 'o-', color='coral', 
                    linewidth=2, markersize=6, label='景点数量')
    
    ax1.set_xlabel('景点类型')
    ax1.set_ylabel('平均热度分')
    ax2.set_ylabel('景点数量')
    ax1.set_xticks(x)
    ax1.set_xticklabels(type_analysis.index, rotation=45, ha='right')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.title('各类型景点数量和热度分析', fontweight='bold')

# 子图4: 免费vs收费的多维度对比
plt.subplot(2, 2, 4)
comparison_data = df.groupby('是否免费_bool').agg({
    '热度分': 'mean',
    '评分': 'mean',
    '评论数量': 'mean'
}).reset_index()

if len(comparison_data) > 0:
    x = np.arange(len(comparison_data))
    width = 0.25
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    bars1 = ax1.bar(x - width, comparison_data['热度分'], width, 
                   label='平均热度', color='lightblue', alpha=0.8)
    bars2 = ax1.bar(x, comparison_data['评分'], width, 
                   label='平均评分', color='lightcoral', alpha=0.8)
    bars3 = ax2.bar(x + width, np.log1p(comparison_data['评论数量']), width, 
                   label='平均评论(对数)', color='lightgreen', alpha=0.8)
    
    ax1.set_xlabel('是否免费')
    ax1.set_ylabel('热度和评分')
    ax2.set_ylabel('评论数量(对数)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['收费', '免费'])
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.title('免费vs收费多维度对比', fontweight='bold')

plt.tight_layout()
plt.savefig('7_综合关联分析.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 图表7保存完成")

print("\n🎉 所有7个图表生成完成！")
print("生成的独立图表文件：")
print("1. 1_热度TOP20.png")
print("2. 2_等级分布分析.png") 
print("3. 3_价格分析.png")
print("4. 4_标签分析.png")
print("5. 5_评分分析.png")
print("6. 6_地理分布分析.png")
print("7. 7_综合关联分析.png")

# 生成数据摘要报告
print("\n" + "="*60)
print("成都景点数据综合分析报告")
print("="*60)
print(f"📊 总景点数: {len(df)}")
print(f"💰 免费景点: {df['是否免费_bool'].sum()}个 ({df['是否免费_bool'].mean()*100:.1f}%)")
print(f"🔥 平均热度: {df['热度分'].mean():.1f}")
print(f"⭐ 平均评分: {df['评分'].mean():.2f}")
print(f"💬 平均评论: {df['评论数量'].mean():.0f}条")

print(f"\n🏆 热门景点TOP3:")
for i, row in df.nlargest(3, '热度分').iterrows():
    print(f"  {i+1}. {row['景点名称']} - 热度: {row['热度分']:.1f}")

print(f"\n🏷️ 热门标签TOP3:")
for tag, count in pd.Series(tag_freq).nlargest(3).items():
    print(f"  {tag}: {count}次")