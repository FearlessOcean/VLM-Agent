import requests
import os

def download_aminer_image(image_url, save_path):
    # ⚠️ 这里的 headers 非常关键，AMiner 平台必须有身份验证信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # 请在浏览器按 F12 -> Network -> 随便点一个请求 -> 复制 Request Headers 里的 Cookie 填在这里
        'Cookie': 'buildTimestamp=1774403972' 
    }

    try:
        response = requests.get(image_url, headers=headers, stream=True)
        # 检查是否请求成功
        if response.status_code == 200:
            # 图片没有后缀名，我们强行给它保存为 .png 即可正常查看
            if not save_path.endswith('.png') and not save_path.endswith('.jpg'):
                save_path += '.png'
                
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ 图片下载成功: {save_path}")
        else:
            print(f"❌ 下载失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ 发生错误: {e}")

# 测试下载
url = "https://annot.aminer.cn/files/task-241851-da1513d1-ba5f-4b08-be88-16d61794eb21_screenshot-c941fb04-d2c1-56f4-9c20-3dfd0c4083dc/7444317636223172608"
download_aminer_image(url, "test_image")