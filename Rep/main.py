import requests
import os
import time
import uuid
import json
import re

# ================= 核心配置区 =================
# 你的专属通行证（直接从你发的代码里提取的，不用改）
TOKEN = "Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQ4ODU2MDcsImlhdCI6MTc3NDg3ODQwNywibmJmIjoxNzc0ODc4NDA3LCJzdWIiOiIyMzExMDM5NzIzNjUwOTY4MDB8Knzmm7nmtbfmtIt8KnxjOTQxZmIwNC1kMmMxLTU2ZjQtOWMyMC0zZGZkMGM0MDgzZGN8Knw1OTMxMmIzNy0zM2UzLTQzMmItOTlmNS0yYzg5ZjRlMmVhMTQifQ.9zsiq0okmiMqvPIrRxJM8YgIbYEjOL_3IjnVgegttsbotp2wNLX952ERipfpls1HnskM4EgpPuYJoKwGoCHbwA"
TASK_ID = 241851
START_DATE = "1774832400"
TAGGER_ID = "c941fb04-d2c1-56f4-9c20-3dfd0c4083dc"

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'authorization': TOKEN,
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36',
    'cookie': 'buildTimestamp=1774403972'
}

# 创建保存图片的文件夹
SAVE_DIR = "../dataset_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_task_page(page):
    """获取一整页的新题目"""
    print(f"\n📡 正在向服务器索要第 {page} 页的题目...")
    url = f"https://annot.aminer.cn/api/v1/annotations/annot/prompts/task/{TASK_ID}/date/{START_DATE}/v2?page={page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 获取题目失败，服务器状态码: {response.status_code}")
        return None

def submit_skip(prompt_id):
    """提交跳过指令"""
    url = "https://annot.aminer.cn/api/v1/annotations/annot/responses"
    # 伪造一个独一无二的答题卡ID（假装是浏览器刚生成的）
    fake_response_id = str(uuid.uuid4()) 
    
    payload = {
        "tagger_id": TAGGER_ID,
        "prompt_id": prompt_id,
        "responses":[{
            "id": fake_response_id,
            "payload": {
                "judge": {"is_skip": 1, "is_correct": 0},
                "note": "修复错误；",
                "inside-form-item-radio-is_skip": 1,
                "inside-form-item-radio-is_correct": 0
            }
        }],
        "task_id": TASK_ID
    }
    
    response = requests.put(url, headers=HEADERS, json=payload)
    return response.status_code == 200

def run_bot():
    print("🤖 全自动外挂已启动！准备开始疯狂干活...")
    
    # 从第1页开始一直往下爬（最多999页）
    for page in range(1, 999):
        data = get_task_page(page)
        if not data:
            break
            
        # 智能解析服务器返回的数据列表
        tasks =[]
        if isinstance(data, list):
            tasks = data
        elif isinstance(data, dict):
            # 有时数据包在 data、items 或 prompts 字段里
            tasks = data.get('data', data.get('items', data.get('prompts',[])))
            
        if not tasks:
            print("🎉 恭喜！当前所有的题目已经全部处理完毕（或者此页没数据了）！")
            break
            
        print(f"✅ 第 {page} 页抓到了 {len(tasks)} 道题目！开始逐一处理：")
        
        # 逐个处理这一页里的每一道题
        for task in tasks:
            # 提取这道题的 ID
            prompt_id = task.get('id') or task.get('prompt_id') or task.get('prompt', {}).get('id')
            
            if not prompt_id:
                print("\n⚠️ 遇到未知的结构，跳过本题...")
                continue
                
            print(f"\n▶ 开始处理题目 ID: {prompt_id}")
            
            # 1. 魔法提取图片链接并下载
            task_str = json.dumps(task)
            # 匹配上一条数据里我们发现的那个图片服务器的域名
            img_urls = re.findall(r'http://open\.annot\.xhanz\.cn/pub/files/[^"]+', task_str)
            
            if img_urls:
                target_img = img_urls[0]
                print(f"  [图片] 嗅探到目标图片: {target_img}")
                try:
                    img_data = requests.get(target_img).content
                    # 截取URL最后一段数字作为文件名
                    filename = target_img.split('/')[-1] + ".png"
                    filepath = os.path.join(SAVE_DIR, f"{prompt_id[:8]}_{filename}")
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    print(f"  [下载] 成功保存到文件夹 -> {filepath}")
                except Exception as e:
                    print(f"  [下载] ❌ 图片下载失败: {e}")
            else:
                print("  [图片] ⚠️ 本题未找到相关的图片链接，直接跳过下载。")
                
            # 2. 发送跳过指令
            print("  [操作] 正在向服务器发送跳过指令...")
            success = submit_skip(prompt_id)
            if success:
                print("  [结果] ✅ 跳过成功！")
            else:
                print("  [结果] ❌ 跳过失败，可能是服务器开小差了。")
                
            # 3. 休息一下，装作是真人在操作（非常关键！太快会被服务器封禁IP）
            time.sleep(1.5)

if __name__ == "__main__":
    run_bot()