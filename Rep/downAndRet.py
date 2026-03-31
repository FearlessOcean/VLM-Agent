import requests
import os
import time
import json
import re

# ================= 核心配置区 =================
TOKEN = "Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQ5MjkyMzIsImlhdCI6MTc3NDkyMjAzMiwibmJmIjoxNzc0OTIyMDMyLCJzdWIiOiIyMzExMDM5NzIzNjUwOTY4MDB8Knzmm7nmtbfmtIt8KnxjOTQxZmIwNC1kMmMxLTU2ZjQtOWMyMC0zZGZkMGM0MDgzZGN8Knw2ZTAzZmIwYS01OTJjLTQ4NzMtYTFiMi02OTcyOWRjMDE2M2UifQ.HkNRGxT-ZoubPGYiCaFi_8pWqLLhIYWnJhrp7IlocMGNYdqw_Ov8CucvCwqwTWL-f2vRs6KKvY7w_0L0SudAxA"

TASK_ID = 241851
START_DATE = "1774918800"
TAGGER_ID = "c941fb04-d2c1-56f4-9c20-3dfd0c4083dc"

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'authorization': TOKEN,
    'content-type': 'application/json',
    'cookie': 'buildTimestamp=1774403972',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36'
}

SAVE_DIR = "dataset_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_task_page(page):
    url = f"https://annot.aminer.cn/api/v1/annotations/annot/prompts/task/{TASK_ID}/date/{START_DATE}/v2?page={page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def get_task_detail(prompt_uuid):
    url = f"https://annot.aminer.cn/api/v1/bench/questions/{prompt_uuid}?uid="
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def reset_task(prompt_uuid):
    url = "https://annot.aminer.cn/api/v1/annotations/annot/reset"
    payload = {
        "prompt_id": prompt_uuid,
        "tagger_id": TAGGER_ID
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    return response.status_code == 200

def run_bot():
    print("🤖 终极无痕潜行外挂已启动！只拿图，不留痕...")
    img_counter = 1  # 顺序计数器
    
    for page in range(1, 999):
        data = get_task_page(page)
        if not data:
            break
            
        tasks =[]
        if isinstance(data, list):
            tasks = data
        elif isinstance(data, dict):
            tasks = data.get('data', data.get('items', data.get('prompts',[])))
            
        if not tasks:
            print("🎉 恭喜！当前所有的题目已经全部处理完毕！")
            break
            
        print(f"\n✅ 第 {page} 页抓到了 {len(tasks)} 道题目！开始逐一处理：")
        
        for task in tasks:
            # 【修复1】精准提取真UUID (03693ad5...)，避开数字ID干扰
            prompt_uuid = task.get('prompt_id')
            if not prompt_uuid or not isinstance(prompt_uuid, str):
                prompt_uuid = task.get('prompt', {}).get('id')
                
            if not prompt_uuid:
                continue
                
            print(f"\n▶ 开始处理题目 UUID: {prompt_uuid}")
            
            detail_data = get_task_detail(prompt_uuid)
            if not detail_data:
                print("  [详情] ❌ 获取题目详情失败，跳过...")
                continue
                
            detail_str = json.dumps(detail_data, ensure_ascii=False)
            target_img = None
            
            # 【修复2】专门解析 ![origin](网址) 格式
            md_images = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', detail_str)
            if md_images:
                target_img = md_images[0]
            else:
                # 备用方案：提取普通网址并过滤
                all_urls = re.findall(r'https?://[^\s"\'\)]+', detail_str)
                img_urls = [u for u in all_urls if any(k in u.lower() for k in['.png', '.jpg', '/files/', 'oss'])]
                if img_urls:
                    target_img = img_urls[0]
            
            if target_img:
                print(f"  [图片] 🎯 成功嗅探到目标图片: {target_img}")
                try:
                    img_data = requests.get(target_img).content
                    # 【修复3】按顺序强制保存为 .png
                    filename = f"{img_counter}.png"
                    filepath = os.path.join(SAVE_DIR, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    print(f"  [下载] 📥 成功保存: {filename}")
                    
                    img_counter += 1  # 计数器加一
                except Exception as e:
                    print(f"  [下载] ❌ 图片下载失败: {e}")
            else:
                print("  [图片] ⚠️ 这道题详情里真没有图片，纯文本题。")
                
            print("  [操作] 正在发送【重置为未标注】指令...")
            success = reset_task(prompt_uuid)
            if success:
                print("  [结果] ✅ 重置成功！服务器已被抹除记录。")
            else:
                print("  [结果] ❌ 重置失败。")
                
            time.sleep(1.5)

if __name__ == "__main__":
    run_bot()