import requests
import os
import time
import json
import re

# ================= 核心配置区 =================
# 你最新抓到的通行证 Token
TOKEN = "Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQ4ODY4MDYsImlhdCI6MTc3NDg3OTYwNiwibmJmIjoxNzc0ODc5NjA2LCJzdWIiOiIyMzExMDM5NzIzNjUwOTY4MDB8Knzmm7nmtbfmtIt8KnxjOTQxZmIwNC1kMmMxLTU2ZjQtOWMyMC0zZGZkMGM0MDgzZGN8KnwyNTdiNjkzOS1hYmJkLTQ5NjUtOWE1Ni1kNGU0YjgxZjhkMTEifQ.WslKSImoXi_juaa4YrkjcOsrRVpBZE-QZCkdjnUBqbjnKWoDoHp8HpY7lAY1KmUMsMDpH8E5nB5FkLQQSWEeew"

TASK_ID = 241851
START_DATE = "1774832400"
TAGGER_ID = "c941fb04-d2c1-56f4-9c20-3dfd0c4083dc"

# 完美伪装的请求头（包含你发现的 Cookie！）
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'authorization': TOKEN,
    'content-type': 'application/json',
    'cookie': 'buildTimestamp=1774403972',  # <-- 你发现的版本号时间戳
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36'
}

# 创建保存图片的文件夹
SAVE_DIR = "dataset_images"
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
        print(f"❌ 获取题目失败，状态码: {response.status_code}")
        return None

def reset_task(prompt_id):
    """【新技能】无痕重置为未标注"""
    url = "https://annot.aminer.cn/api/v1/annotations/annot/reset"
    payload = {
        "prompt_id": prompt_id,
        "tagger_id": TAGGER_ID
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    return response.status_code == 200

def run_bot():
    print("🤖 终极无痕潜行外挂已启动！只拿图，不留痕...")
    
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
            
        print(f"✅ 第 {page} 页抓到了 {len(tasks)} 道题目！开始逐一处理：")
        
        for task in tasks:
            prompt_id = task.get('id') or task.get('prompt_id') or task.get('prompt', {}).get('id')
            
            if not prompt_id:
                continue
                
            print(f"\n▶ 开始处理题目 ID: {prompt_id}")
            
            # 1. 魔法提取图片链接并下载
            task_str = json.dumps(task)
            img_urls = re.findall(r'http://open\.annot\.xhanz\.cn/pub/files/[^"]+', task_str)
            
            if img_urls:
                target_img = img_urls[0]
                print(f"  [图片] 嗅探到目标图片: {target_img}")
                try:
                    img_data = requests.get(target_img).content
                    filename = target_img.split('/')[-1] + ".png"
                    filepath = os.path.join(SAVE_DIR, f"{prompt_id[:8]}_{filename}")
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    print(f"  [下载] 成功保存到文件夹 -> {filepath}")
                except Exception as e:
                    print(f"  [下载] ❌ 图片下载失败: {e}")
            else:
                print("  [图片] ⚠️ 本题未找到图片链接。")
                
            # 2. 发送“重置为未标注”指令（无痕模式）
            print("  [操作] 正在发送【重置为未标注】指令...")
            success = reset_task(prompt_id)
            if success:
                print("  [结果] ✅ 重置成功！服务器已被抹除记录。")
            else:
                print("  [结果] ❌ 重置失败。")
                
            # 3. 休息一下，避免触发服务器风控
            time.sleep(1.5)

if __name__ == "__main__":
    run_bot()