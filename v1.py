import os
import base64
import re
import sys
from pathlib import Path
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np

# --- 基础配置 ---
API_KEY = "sk-k7fyyns8nfJxqFLYcQJC41rJdBFSBeHjTZuig7lZrOPmEpi5"
BASE_URL = "https://hiapi.online/v1"
# MODEL_NAME = "gpt-4o"
MODEL_NAME = "gemini-3-flash"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# --- 针对几何复现量身定制的 Prompt ---
GEOMETRIC_PROMPT = """你是一个专业的几何数学绘图员。
任务：请分析图片中的几何图形，并写出 Python 代码将其精准复现。

要求：
1. **静默分析**：识别图形中的数学关系（平行、垂直、等长、切点、角度标注、辅助线等）。
2. **绘图标准**：
   - 使用 matplotlib.pyplot。
   - 必须包含图中所有的字母标注（A, B, O, x, y, θ 等）和数值。
   - 保持原始图形的几何比例。
   - 线条清晰，文字无遮挡。
   - 隐藏背景坐标轴（除非原图中有坐标轴）。
3. **输出规范**：
   - 只输出 python 代码块。
   - 代码最后一行必须是：plt.savefig('question.png', dpi=300, bbox_inches='tight')
   - 不要输出任何解释文字。
"""

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def process_single_image(image_path, task_dir):
    """处理单张图片：获取代码 -> 保存代码 -> 执行绘图"""
    img_b64 = encode_image(image_path)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": GEOMETRIC_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]}
            ],
            temperature=0,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content
        code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
        
        if code_match:
            code = code_match.group(1).strip()
            
            # 1. 在任务文件夹内保存生成的源码，方便人工复核
            code_file = task_dir / "generated_code.py"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # 2. 切换当前工作目录到任务文件夹，确保图片保存在正确位置
            old_cwd = os.getcwd()
            os.chdir(task_dir)
            
            try:
                # 3. 执行绘图逻辑
                local_vars = {"plt": plt, "np": np}
                exec(code, local_vars)
                plt.close('all')
                return True
            except Exception as e:
                print(f"执行代码出错: {e}")
                return False
            finally:
                os.chdir(old_cwd) # 切换回主目录
        return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def start_batch_job(input_folder_name):
    input_path = Path(input_folder_name)
    output_root = Path("Review_Folder") # 所有结果的总目录
    
    if not output_root.exists():
        output_root.mkdir()

    # 遍历所有图片
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp")
    files = []
    for ext in extensions:
        files.extend(input_path.glob(ext))

    print(f"找到 {len(files)} 张待处理图片...")

    for img_p in files:
        # 为每张图片创建独立文件夹，名字为：原文件名_result
        task_name = f"{img_p.stem}_task"
        task_dir = output_root / task_name
        task_dir.mkdir(exist_ok=True)
        
        print(f"正在处理 [{img_p.name}] -> 目标目录: {task_dir}")
        
        # 将原图也拷贝一份进去，方便并排核验
        with open(img_p, "rb") as src, open(task_dir / f"original_{img_p.name}", "wb") as dst:
            dst.write(src.read())

        success = process_single_image(img_p, task_dir)
        if success:
            print(f"✅ 处理完成: {task_name}/question.png")
        else:
            print(f"❌ 处理失败: {task_name}")

if __name__ == "__main__":
    # 步骤：
    # 1. 将你需要处理的几何图片放在当前目录下的 'source_images' 文件夹中
    # 2. 运行此程序
    source_dir = "source_images" 
    
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"已创建 {source_dir} 文件夹，请把几何图片放入其中后重新运行。")
    else:
        start_batch_job(source_dir)