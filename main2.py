import os
import base64
import re
import traceback
from pathlib import Path
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np

# --- 基础配置 ---
API_KEY = "sk-k7fyyns8nfJxqFLYcQJC41rJdBFSBeHjTZuig7lZrOPmEpi5"
BASE_URL = "https://hiapi.online/v1"
MODEL_NAME = "gemini-3-flash"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

GEOMETRIC_PROMPT = """# Role: Python & Matplotlib 几何/函数绘图专家

## Profile:

你是一个精通 Python 和 Matplotlib 的数学可视化专家。你的任务是根据用户提供的几何、函数、三视图或物理图表图片，编写高质量、高度还原且具有数学严谨性的代码。

## Task Logic (任务逻辑):

1. **深度分析**: 识别图中的几何元素（顶点、直线、圆弧、抛物线等）及关系（平行、垂直、折叠、对称、共线）。
2. **数学建模 (核心)**: 禁止随手估算坐标。必须建立精确的坐标系，使用解析几何的方法计算关键点：
   - 垂直关系：利用斜率负倒数（m1 * m2 = -1）。
   - 折叠问题：计算镜像对称点（Reflection Matrix）。
   - 交点问题：通过联立线性或二次方程组求解精确坐标。
   - 旋转/螺旋：使用旋转矩阵或极坐标方程。
3. **线型区分**:
   - 实线 ('k-'): 用于可见轮廓、主要线段。
   - 虚线 ('k--'): 用于辅助线、被遮挡的棱、折叠前的原始位置。
   - 标注尺寸线: 使用带箭头的 annotate 或尺寸指示线。

## Visual Style Guidelines (视觉风格规范):

1. **专业字体**: 必须配置 `plt.rcParams['mathtext.fontset'] = 'stix'` 和 `font.family: serif`。
2. **数学标签**: 所有字母标签（A, B, x, y, f(x), D' 等）必须包裹在 LaTeX 符号中（如 `$A'$`），默认使用斜体。
3. **标签位置**: 精调 `ha` (水平对齐)、`va` (垂直对齐) 和 `text` 的偏移量，确保文字不压线，且不与几何顶点重叠。
4. **纯净背景**: 隐藏原生坐标轴 `ax.axis('off')`，除非是函数图象（此时使用带箭头的十字交叉轴）。
5. **比例保真**: 必须设置 `ax.set_aspect('equal')` 确保几何形状不被拉伸变形。

## Output Constraints (输出限制):

1. 必须导入 `matplotlib.pyplot` 和 `numpy`。
2. 图片必须命名为 `question.png`。
3. 必须设置 `dpi=300` 和 `bbox_inches='tight'` 以保证印刷级清晰度。
4. **严禁使用 `plt.show()`**，代码末尾仅保留 `plt.savefig('question.png', ...)`。
5. 如果涉及中文，请在代码中包含基础的字体修复逻辑（如尝试设置 SimSun 或 SimHei）。

## Workflow (工作流):

1. 无需说明你识别到的几何关系和采用的数学模型。
2. 提供完整、整洁、带注释、注释精简的 Python 代码。

"""

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def log_error(task_dir, error_msg, trace_detail=None):
    """将错误信息写入任务目录下的文件"""
    with open(task_dir / "error_log.txt", "w", encoding="utf-8") as f:
        f.write(f"ERROR SUMMARY: {error_msg}\n")
        if trace_detail:
            f.write("-" * 30 + "\n")
            f.write(trace_detail)

def process_single_image(image_path, task_dir):
    try:
        img_b64 = encode_image(image_path)
    except Exception as e:
        print(f"  [!] 无法读取图片: {e}")
        return False

    # --- 第一步：请求 API ---
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": GEOMETRIC_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]}
            ],
            temperature=0
        )
        content = response.choices[0].message.content
    except Exception as e:
        err_msg = f"API 请求阶段崩溃: {str(e)}"
        print(f"  [!] {err_msg}")
        log_error(task_dir, err_msg)
        return False

    # --- 第二步：提取代码 ---
    code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
    if not code_match:
        err_msg = "模型未返回有效的 Python 代码块"
        print(f"  [!] {err_msg}")
        log_error(task_dir, err_msg, f"模型原始响应内容内容：\n{content}")
        return False
    
    code = code_match.group(1).strip()
    # 无论成功失败，先保存一次代码备查
    code_file = task_dir / "generated_code.py"
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(code)

    # --- 第三步：执行代码 ---
    old_cwd = os.getcwd()
    os.chdir(task_dir) # 切换到任务目录执行
    
    try:
        # 清理之前的绘图状态
        plt.close('all')
        # 构建执行上下文
        exec_globals = {
            "plt": plt,
            "np": np,
            "__builtins__": __builtins__
        }
        exec(code, exec_globals)
        plt.close('all')
        os.chdir(old_cwd)
        return True
    except Exception as e:
        os.chdir(old_cwd)
        trace_inner = traceback.format_exc()
        print(f"  [!] 代码执行逻辑错误 (请检查 error_log.txt)")
        log_error(task_dir, f"Python Execution Error: {str(e)}", trace_inner)
        return False

def start_batch_job(input_folder_name):
    input_path = Path(input_folder_name)
    output_root = Path("Review_Folder")
    output_root.mkdir(exist_ok=True)

    files = list(input_path.glob("*.png")) + list(input_path.glob("*.jpg")) + list(input_path.glob("*.jpeg"))
    
    if not files:
        print(f"错误：在 {input_folder_name} 中没找到图片。")
        return

    print(f"开始处理任务，共 {len(files)} 件...")

    for img_p in files:
        task_name = f"{img_p.stem}_task"
        task_dir = output_root / task_name
        task_dir.mkdir(exist_ok=True)
        
        # 复制原图进文件夹方便肉眼比对
        with open(img_p, "rb") as s, open(task_dir / f"origin_{img_p.name}", "wb") as d:
            d.write(s.read())

        print(f"\n>>> 正在处理: {img_p.name}")
        success = process_single_image(img_p, task_dir)
        
        if success:
            print(f"  [+] 成功！绘图已保存为 question.png")
        else:
            print(f"  [-] 失败！请进入 {task_name} 查看 error_log.txt")

if __name__ == "__main__":
    # 使用前确保此文件夹存在并放入图片
    source_dir = "source_images" 
    if os.path.exists(source_dir):
        start_batch_job(source_dir)
    else:
        os.makedirs(source_dir)
        print(f"请将图片放入 {source_dir} 后运行")