import requests
import json
import csv
import os
from typing import Dict, List, Any, Optional

def fetch_ctrip_attractions(page_index: int = 1, count: int = 10) -> Optional[Dict]:
    """
    获取携程景点列表数据
    
    Args:
        page_index: 页码，从1开始
        count: 每页数量
    
    Returns:
        返回JSON响应数据，请求失败返回None
    """
    cookies = {
        'UBT_VID': '1763382479749.13a8GtXW3P5J',
        'Hm_lvt_a8d6737197d542432f4ff4abc6e06384': '1763382480',
        'HMACCOUNT': 'E0B9E8224ADF1206',
        'MKT_CKID': '1763382479876.z77yi.njgb',
        'GUID': '09031178411654044234',
        '_RGUID': '29c49f95-1653-4b5b-967b-d5c0aaa61d4e',
        'MKT_Pagesource': 'H5',
        'nfes_isSupportWebP': '1',
        'nfes_isSupportWebP': '1',
        'Hm_lpvt_a8d6737197d542432f4ff4abc6e06384': '1763382588',
        'Union': 'OUID=&AllianceID=4902&SID=22921635&SourceID=&createtime=1763382588&Expires=1763987388341',
        'MKT_OrderClick': 'ASID=490222921635&AID=4902&CSID=22921635&OUID=&CT=1763382588342&CURL=https%3A%2F%2Fwww.ctrip.com%2F%3Fallianceid%3D4902%26sid%3D22921635%26msclkid%3Dc61ae724524d194b58238e3f4680351d%26keywordid%3D82533150992350&VAL={"pc_vid":"1763382479749.13a8GtXW3P5J"};',
        '_ubtstatus': '%7B%22vid%22%3A%221763382479749.13a8GtXW3P5J%22%2C%22sid%22%3A1%2C%22pvid%22%3A10%2C%22pid%22%3A0%7D',
        '_pd': '%7B%22_o%22%3A1%2C%22s%22%3A3%2C%22_s%22%3A0%7D',
        '_bfa': '1.1763382479749.13a8GtXW3P5J.1.1763385626643.1763454189742.2.1.10650142842',
        '_jzqco': '%7C%7C%7C%7C1763382480625%7C1.2063646721.1763382479874.1763385627432.1763454190567.1763385627432.1763454190567.undefined.0.0.11.11',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/json',
        'cookieorigin': 'https://you.ctrip.com',
        'origin': 'https://you.ctrip.com',
        'priority': 'u=1, i',
        'referer': 'https://you.ctrip.com/',
        'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'x-ctx-ubt-pageid': '10650142842',
        'x-ctx-ubt-pvid': '1',
        'x-ctx-ubt-sid': '2',
        'x-ctx-ubt-vid': '1763382479749.13a8GtXW3P5J',
        'x-ctx-wclient-req': 'a25042e298f3dad5079a95e975c3b0ba',
    }

    params = {
        '_fxpcqlniredt': '09031178411654044234',
        'x-traceID': '09031178411654044234-1763454200208-3396853',
    }

    json_data = {
        'head': {
            'cid': '09031178411654044234',
            'ctok': '',
            'cver': '1.0',
            'lang': '01',
            'sid': '8888',
            'syscode': '999',
            'auth': '',
            'xsid': '',
            'extension': [],
        },
        'scene': 'online',
        'districtId': 104,
        'index': page_index,
        'sortType': 1,
        'count': count,
        'filter': {
            'filterItems': [],
        },
        'coordinate': {
            'latitude': 22.33893178511237,
            'longitude': 114.17097715578561,
            'coordinateType': 'WGS84',
        },
        'returnModuleType': 'product',
    }

    try:
        response = requests.post(
            'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList',
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None

def extract_attraction_data(card_data: Dict) -> Dict:
    """
    从景点card数据中提取所需字段
    
    Args:
        card_data: 单个景点card数据字典
    
    Returns:
        提取后的景点数据
    """
    # 安全地获取嵌套字段
    poi_id = card_data.get('poiId', '')
    poi_name = card_data.get('poiName', '')
    
    # 所在地区和区域名称
    district_name = card_data.get('districtName', '')
    zone_name = card_data.get('zoneName', '') or card_data.get('displayField', '')
    
    # 景区等级和热度
    sight_level_str = card_data.get('sightLevelStr', '')
    heat_score = card_data.get('heatScore', '')
    
    # 评论相关
    comment_count = card_data.get('commentCount', '')
    comment_score = card_data.get('commentScore', '')
    
    # 距离
    distance_str = card_data.get('distanceStr', '')
    
    # 标签和特色
    tags = card_data.get('tagNameList', [])
    if isinstance(tags, list):
        tags_str = '、'.join([str(tag) for tag in tags])
    else:
        tags_str = ''
    
    short_features = card_data.get('shortFeatures', [])
    if isinstance(short_features, list):
        short_features_str = '；'.join([str(feature) for feature in short_features])
    else:
        short_features_str = ''
    
    # 价格相关
    is_free = card_data.get('isFree', False)
    is_free_str = '是' if is_free else '否'
    
    price = card_data.get('price', '')
    price_type_desc = card_data.get('priceTypeDesc', '')
    
    # 详情链接
    detail_url_info = card_data.get('detailUrlInfo', {})
    if isinstance(detail_url_info, dict):
        detail_url = detail_url_info.get('url', '')
    else:
        detail_url = ''
    
    return {
        '景点ID': poi_id,
        '景点名称': poi_name,
        '所在地区': district_name,
        '区域名称': zone_name,
        '景区等级': sight_level_str,
        '热度分': heat_score,
        '评论数量': comment_count,
        '评分': comment_score,
        '距离市中心': distance_str,
        '标签': tags_str,
        '短特色': short_features_str,
        '是否免费': is_free_str,
        '门票价格': price,
        '价格类型': price_type_desc,
        '详情链接': detail_url
    }

def save_to_csv(data_list: List[Dict], filename: str = "携程景点数据.csv"):
    """
    将景点数据保存到CSV文件
    
    Args:
        data_list: 景点数据列表
        filename: CSV文件名
    """
    # 定义表头
    fieldnames = [
        '景点ID', '景点名称', '所在地区', '区域名称', '景区等级', 
        '热度分', '评论数量', '评分', '距离市中心', '标签', 
        '短特色', '是否免费', '门票价格', '价格类型', '详情链接'
    ]
    
    # 检查文件是否存在
    file_exists = os.path.exists(filename)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # 如果文件不存在，写入表头
            if not file_exists:
                writer.writeheader()
                print(f"创建新文件 {filename} 并写入表头")
            
            # 写入数据
            for data in data_list:
                writer.writerow(data)
            
            print(f"成功写入 {len(data_list)} 条数据到 {filename}")
            
    except Exception as e:
        print(f"写入CSV文件失败: {e}")

def crawl_ctrip_attractions(start_page: int = 1, end_page: int = 5, page_size: int = 10):
    """
    爬取携程景点数据的主函数
    
    Args:
        start_page: 起始页码
        end_page: 结束页码
        page_size: 每页数量
    """
    all_attractions = []
    
    for page in range(start_page, end_page + 1):
        print(f"正在爬取第 {page} 页...")
        
        # 获取数据
        response_data = fetch_ctrip_attractions(page, page_size)
        
        if not response_data:
            print(f"第 {page} 页数据获取失败，跳过")
            continue
        
        try:
            # 检查响应状态
            if response_data.get('ResponseStatus', {}).get('Ack') != 'Success':
                print(f"第 {page} 页响应状态异常: {response_data.get('ResponseStatus', {})}")
                continue
            
            # 解析数据 - 景点数据在attractionList数组中，每个item的card字段中
            attractions_list = response_data.get('attractionList', [])
            
            if not attractions_list:
                print(f"第 {page} 页没有景点数据")
                break
            
            # 提取数据
            page_data = []
            for item in attractions_list:
                card_data = item.get('card', {})
                if card_data:  # 确保card数据存在
                    attraction_data = extract_attraction_data(card_data)
                    page_data.append(attraction_data)
            
            if not page_data:
                print(f"第 {page} 页没有有效数据")
                continue
            
            # 保存到CSV
            save_to_csv(page_data)
            all_attractions.extend(page_data)
            
            print(f"第 {page} 页爬取完成，共 {len(page_data)} 条数据")
            
            # 检查是否还有更多数据
            has_more = response_data.get('hasMore', False)
            if not has_more:
                print("没有更多数据，爬取结束")
                break
            
        except Exception as e:
            print(f"第 {page} 页数据处理失败: {e}")
            continue
    
    print(f"爬取完成！总共获取 {len(all_attractions)} 条景点数据")
    return all_attractions

# 使用示例
if __name__ == "__main__":
    # 爬取前30页，每页10条数据
    attractions_data = crawl_ctrip_attractions(start_page=1, end_page=30, page_size=10)
    
    # 如果需要查看数据，可以打印前几条
    if attractions_data:
        print("\n前3条数据示例:")
        for i, item in enumerate(attractions_data[:3]):
            print(f"第{i+1}条: {item}")