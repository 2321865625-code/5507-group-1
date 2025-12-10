import pandas as pd

# 修正路径中的斜杠（用正斜杠/）
file_path = "C:/Users/23218/Desktop/携程/全部评论(1).csv"
comment_column = "评论内容"
save_path = "C:/Users/23218/Desktop/携程/全部评论清洗后.csv"

# 注意：你的文件是.csv格式，需要用read_csv读取（之前写成了read_excel，这里一并修正）
df = pd.read_csv(file_path)

# 按评论列去重
df_cleaned = df.drop_duplicates(subset=[comment_column], keep="first")

# 保存为csv格式（用to_csv，之前写成了to_excel，一并修正）
df_cleaned.to_csv(save_path, index=False, encoding="utf-8-sig")  # 加encoding避免中文乱码

print(f"去重完成！原数据共{len(df)}条，去重后剩{len(df_cleaned)}条，已保存到：{save_path}")