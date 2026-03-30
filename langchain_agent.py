import os
import re
import base64
import subprocess
from pathlib import Path

# 导入 LangChain 相关组件
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ================= 你的专属专业 Prompt =================
SYSTEM_PROMPT = """# Role: Python & Matplotlib 几何/函数绘图专家

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
    """把本地图片转为 Base64 字符串供模型读取"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_python_code(markdown_text):
    """使用正则提取大模型返回的 ```python xxx ``` 代码块"""
    match = re.search(r'```python\n(.*?)\n```', markdown_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return markdown_text 

def process_geometry_task(image_path, task_output_dir):
    """
    处理单个图片的任务：
    1. 调用 LangChain 模型识图并写代码
    2. 提取代码并保存
    3. 运行代码生成 question.png
    """
    task_dir = Path(task_output_dir)
    task_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(image_path).suffix.lower().replace('.', '')
    ext = 'jpeg' if ext == 'jpg' else ext
    base64_image = encode_image(image_path)

    # ========================================================
    # 在这里填入你的自定义配置 (API_KEY 和 BASE_URL)
    # ========================================================
    llm = ChatOpenAI(
        api_key="sk-k7fyyns8nfJxqFLYcQJC41rJdBFSBeHjTZuig7lZrOPmEpi5",       # <--- 替换为你的真实 API Key
        base_url="https://hiapi.online/v1",              # <--- 替换为你的 Base URL
        model="gemini-3.1-pro",                                    # <--- 替换为你实际使用的模型名称
        temperature=0.1, 
        max_tokens=4000
    )

    print(f"🚀 正在发送图片给大模型解析并生成代码...")

    messages =[
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=[
            {"type": "text", "text": "请根据以上专家设定，编写代码完美复现这张附图。直接输出代码，不要废话。"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{ext};base64,{base64_image}",
                    "detail": "high" 
                }
            }
        ])
    ]

    try:
        # 1. 触发大模型交互
        response = llm.invoke(messages)
        ai_reply = response.content

        # 2. 剥离并获取纯净的 Python 代码
        clean_code = extract_python_code(ai_reply)

        # 3. 将生成的代码保存到对应任务文件夹
        code_file = task_dir / "generated_code.py"
        code_file.write_text(clean_code, encoding="utf-8")
        print(f"✅ 代码已保存: {code_file}")

        # 4. 直接在对应的文件夹下执行该 python 文件
        print(f"⚙️ 正在执行代码以生成 question.png ...")
        result = subprocess.run(["python", "generated_code.py"], 
            cwd=task_dir, 
            capture_output=True, 
            text=True
        )

        if result.returncode == 0:
            print(f"🎉 图片渲染成功！查看: {task_dir / 'question.png'}")
            if (task_dir / "error_log.txt").exists():
                (task_dir / "error_log.txt").unlink()
        else:
            print(f"❌ 代码执行报错，已记录日志！")
            error_log = task_dir / "error_log.txt"
            error_log.write_text(result.stderr, encoding="utf-8")

    except Exception as e:
        print(f"🚨 API请求或处理过程发生致命错误: {e}")

if __name__ == "__main__":
    # ===========================
    # 设定你的工作目录
    # ===========================
    WORK_DIR = "LangChain-WorkSpace" 
    
    work_path = Path(WORK_DIR)
    
    # 第一次运行自动创建工作目录
    if not work_path.exists():
        work_path.mkdir(parents=True)
        print(f"📁 已自动创建工作目录 '{WORK_DIR}'。")
        print("💡 请将需要处理的图片（.jpg/.png）放入该目录后，重新运行本程序。")
    else:
        # 支持的图片格式
        valid_extensions = {".jpg", ".jpeg", ".png"}
        
        # 扫描目录下所有的图片文件
        image_files =[f for f in work_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
        
        if not image_files:
            print(f"⚠️ 工作目录 '{WORK_DIR}' 下没有找到任何图片文件。")
        else:
            print(f"🔍 扫描到 {len(image_files)} 张图片，开始批量处理流程...")
            
            for img_file in image_files:
                print(f"\n" + "="*50)
                print(f"▶️ 开始处理任务: {img_file.name}")
                
                # 为每张图创建一个单独的结果存放目录，例如： WorkSpace/图1_output/
                output_folder = work_path / f"{img_file.stem}_output"
                
                process_geometry_task(str(img_file), str(output_folder))
            
            print(f"\n🏁 所有任务处理完毕！请前往 '{WORK_DIR}' 目录下查看各输出文件夹。")