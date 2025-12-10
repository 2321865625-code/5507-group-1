import requests
import json
import csv
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import datetime
import hashlib

# ---------------------- 基础配置 ----------------------
# 动态生成基础信息，避免固定值
def generate_dynamic_params():
    timestamp = str(int(time.time() * 1000))
    guid = hashlib.md5(timestamp.encode()).hexdigest()[:20]
    
    cookies = {
        'GUID': guid,
        'nfes_isSupportWebP': '1',
        'UBT_VID': f'{timestamp}.{hashlib.md5(timestamp.encode()).hexdigest()[:8]}',
        'MKT_CKID': f'{timestamp}.{hashlib.md5(timestamp.encode()).hexdigest()[:8]}',
        '_RGUID': hashlib.md5(timestamp.encode()).hexdigest(),
        '_bfa': f'1.{timestamp}.{hashlib.md5(timestamp.encode()).hexdigest()[:8]}.1.{int(time.time() * 1000)}.{int(time.time() * 1000) + 1000}.1.2.290510',
        '_jzqco': f'%7C%7C%7C%7C{timestamp}%7C1.{random.random()}.{timestamp}.{timestamp}.{int(time.time() * 1000)}.{timestamp}.{int(time.time() * 1000)}.0.0.0.2.2',
    }
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
    ]
    
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookieorigin': 'https://you.ctrip.com',
        'origin': 'https://you.ctrip.com',
        'priority': 'u=1, i',
        'referer': f'https://you.ctrip.com/sight/beijing1/{POI_ID}.html',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random.choice(user_agents),
        'x-ctx-ubt-pageid': str(random.randint(290000, 290999)),
        'x-ctx-ubt-pvid': str(random.randint(1, 10)),
        'x-ctx-ubt-sid': str(random.randint(1, 10)),
        'x-ctx-ubt-vid': f'{timestamp}.{hashlib.md5(timestamp.encode()).hexdigest()[:8]}',
        'x-ctx-wclient-req': hashlib.md5(timestamp.encode()).hexdigest()[:32],
    }
    
    params = {
        '_fxpcqlniredt': guid,
        'x-traceID': f'{guid}-{timestamp}-{random.randint(1000000, 9999999)}',
    }
    
    return cookies, headers, params

# 爬取配置
POI_ID = 76342  # 景点ID
TOTAL_PAGES = 500  # 总爬取页数
PAGE_SIZE = 10  # 每页评论数
MAX_RETRIES = 5  # 增加重试次数
THREAD_NUM = 5   # 减少线程数，降低频率
RANDOM_DELAY = (2, 6)  # 增加等待时间
PROXY = None  # 可配置代理，如：{'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'}

# 文件配置
CSV_HEADERS = [
    '评论ID', '用户ID', '用户名', '用户等级', '用户头像', '评论内容',
    '发布时间', '发布地点', '总评分', '景色评分', '趣味评分', '性价比评分',
    '点赞数', '回复数', '图片数量', '图片链接', '是否精选', '发布类型', '景点ID'
]
SINGLE_CSV = f'{POI_ID}_评论.csv'
TOTAL_CSV = '全部评论.csv'

# 会话管理
session = requests.Session()
file_lock = Lock()

# ---------------------- 工具函数 ----------------------
def convert_date(date_str):
    """转换携程日期格式"""
    if not date_str or 'Date' not in date_str:
        return ''
    try:
        timestamp = int(date_str.split('(')[1].split('+')[0]) // 1000
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return ''

def get_proxy():
    """获取代理（如果需要）"""
    return PROXY

def random_sleep(min_seconds=1, max_seconds=5):
    """随机睡眠，增加人类行为模拟"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

def fetch_page(page_index):
    """爬取单页评论"""
    # 每次请求都生成新的参数
    cookies, headers, params = generate_dynamic_params()
    
    json_data = {
        'arg': {
            'channelType': 2,
            'collapseType': 0,
            'commentTagId': 0,
            'pageIndex': page_index,
            'pageSize': PAGE_SIZE,
            'poiId': POI_ID,
            'sourceType': 1,
            'sortType': 3,
            'starType': 0,
        },
        'head': {
            'cid': cookies['GUID'],
            'ctok': '',
            'cver': '1.0',
            'lang': '01',
            'sid': '8888',
            'syscode': '09',
            'auth': '',
            'xsid': '',
            'extension': [],
        },
    }

    for retry in range(MAX_RETRIES):
        try:
            # 随机等待，模拟人类行为
            random_sleep(*RANDOM_DELAY)
            
            # 随机决定是否使用代理
            proxies = get_proxy() if random.random() > 0.7 else None
            
            response = session.post(
                API_URL,
                params=params,
                cookies=cookies,
                headers=headers,
                json=json_data,
                timeout=15,  # 增加超时时间
                proxies=proxies,
                verify=False  # 跳过SSL验证（谨慎使用）
            )
            
            # 检查是否被反爬
            if response.status_code == 403:
                print(f'第{page_index}页触发反爬机制（403），等待后重试...')
                time.sleep(30)  # 长时间等待
                continue
                
            if response.status_code == 429:
                print(f'第{page_index}页请求过于频繁（429），等待后重试...')
                time.sleep(60)  # 更长时间等待
                continue
                
            response.raise_for_status()
            data = response.json()

            # 校验响应
            if data.get('code') != 200 or data.get('msg') != '请求成功':
                error_msg = data.get('msg', '未知错误')
                print(f'第{page_index}页请求失败：{error_msg}')
                
                # 如果是特定错误，等待更长时间
                if '频繁' in error_msg or '限制' in error_msg:
                    time.sleep(30)
                    continue
                return []

            # 解析评论数据
            comments = []
            items = data.get('result', {}).get('items', [])
            
            if not items:
                print(f'第{page_index}页无数据，可能已到末尾')
                return []
                
            for item in items:
                user_info = item.get('userInfo', {})
                scores_list = item.get('scores', [])
                images_list = item.get('images', [])

                scores = {}
                for score_item in scores_list:
                    scores[score_item.get('name', '')] = score_item.get('score', 0)

                images = [img.get('imageSrcUrl', '') for img in images_list if img.get('imageSrcUrl')]

                comment = {
                    '评论ID': item.get('commentId', ''),
                    '用户ID': user_info.get('userId', ''),
                    '用户名': user_info.get('userNick', ''),
                    '用户等级': user_info.get('userMember', ''),
                    '用户头像': user_info.get('userImage', ''),
                    '评论内容': item.get('content', '').strip().replace('\n', ' '),
                    '发布时间': convert_date(item.get('publishTime', '')),
                    '发布地点': item.get('ipLocatedName', ''),
                    '总评分': item.get('score', 0),
                    '景色评分': scores.get('景色', 0),
                    '趣味评分': scores.get('趣味', 0),
                    '性价比评分': scores.get('性价比', 0),
                    '点赞数': item.get('usefulCount', 0),
                    '回复数': item.get('replyCount', 0),
                    '图片数量': len(images),
                    '图片链接': '|'.join(images) if images else '',
                    '是否精选': item.get('isPicked', False),
                    '发布类型': item.get('publishTypeTag', ''),
                    '景点ID': POI_ID
                }
                comments.append(comment)

            print(f'第{page_index}页爬取成功，获取{len(comments)}条评论')
            return comments

        except requests.exceptions.RequestException as e:
            print(f'第{page_index}页网络错误（重试{retry+1}/{MAX_RETRIES}）：{str(e)}')
            if retry == MAX_RETRIES - 1:
                return []
            # 指数退避策略
            time.sleep(2 ** retry + random.uniform(1, 3))
        except json.JSONDecodeError as e:
            print(f'第{page_index}页JSON解析错误：{str(e)}')
            return []
        except Exception as e:
            print(f'第{page_index}页未知错误：{str(e)}')
            return []

def save_to_csv(comments, is_total=False):
    """保存评论到CSV文件"""
    with file_lock:
        # 保存单个景点CSV
        with open(SINGLE_CSV, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(comments)

        # 保存汇总CSV
        if is_total:
            with open(TOTAL_CSV, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerows(comments)

def batch_crawl(pages):
    """批量爬取页面，支持断点续爬"""
    successful_pages = 0
    
    with ThreadPoolExecutor(max_workers=THREAD_NUM) as executor:
        future_to_page = {executor.submit(fetch_page, page): page for page in pages}
        
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                comments = future.result()
                if comments:
                    save_to_csv(comments, is_total=True)
                    successful_pages += 1
                else:
                    print(f'第{page}页爬取失败或无数据')
            except Exception as e:
                print(f'第{page}页任务处理失败：{str(e)}')
    
    return successful_pages

# ---------------------- 主函数 ----------------------
def main():
    # 清空历史文件
    with open(SINGLE_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        pass
    with open(TOTAL_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        pass

    print(f'开始爬取景点ID：{POI_ID}，共{TOTAL_PAGES}页评论')
    start_time = time.time()

    # 分批爬取，避免一次性请求过多
    batch_size = 50  # 每批50页
    all_pages = list(range(1, TOTAL_PAGES + 1))
    batches = [all_pages[i:i + batch_size] for i in range(0, len(all_pages), batch_size)]
    
    total_successful = 0
    
    for i, batch in enumerate(batches, 1):
        print(f'开始第{i}批爬取，共{len(batch)}页...')
        batch_success = batch_crawl(batch)
        total_successful += batch_success
        
        # 批次间休息
        if i < len(batches):
            rest_time = random.randint(10, 30)
            print(f'批次完成，休息{rest_time}秒...')
            time.sleep(rest_time)

    end_time = time.time()
    total_time = end_time - start_time
    print(f'爬取完成！成功爬取{total_successful}页，总耗时：{total_time:.2f}秒')
    print(f'成功率：{total_successful/TOTAL_PAGES*100:.2f}%')
    print(f'单个景点评论文件：{SINGLE_CSV}')
    print(f'汇总评论文件：{TOTAL_CSV}')

if __name__ == '__main__':
    API_URL = 'https://m.ctrip.com/restapi/soa2/13444/json/getCommentCollapseList'
    
    # 忽略SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        import requests
    except ImportError:
        print('请先安装依赖：pip install requests')
        exit()
    
    main()