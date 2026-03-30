import os
from pathlib import Path

def generate_dashboard(review_dir="Review_Folder"):
    review_path = Path(review_dir)
    if not review_path.exists():
        print("错误：找不到 Review_Folder 文件夹")
        return

    # HTML 头部（包含 CSS 样式和复制脚本）
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>几何绘图核验控制台</title>
        <style>
            body { font-family: sans-serif; background: #f4f4f9; padding: 20px; }
            .task-card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; padding: 20px; display: flex; flex-direction: column; }
            .task-header { font-size: 1.2em; font-weight: bold; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; color: #333; }
            .comparison { display: flex; gap: 20px; align-items: flex-start; }
            .img-container { flex: 1; text-align: center; }
            .img-container img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }
            .controls { flex: 0 0 300px; display: flex; flex-direction: column; gap: 10px; }
            .btn { padding: 10px; cursor: pointer; border: none; border-radius: 4px; color: white; transition: 0.3s; font-weight: bold;}
            .btn-copy { background: #4a90e2; }
            .btn-copy:hover { background: #357abd; }
            .btn-copy:active { background: #2a5a8e; }
            .btn-error { background: #ff4d4f; }
            code-box { display: none; } /* 隐藏实际代码，只存数据 */
            .success-tag { color: #52c41a; font-weight: bold; }
            .fail-tag { color: #f5222d; font-weight: bold; }
        </style>
        <script>
            function copyToClipboard(elementId, btn) {
                var text = document.getElementById(elementId).value;
                navigator.clipboard.writeText(text).then(function() {
                    const originalText = btn.innerText;
                    btn.innerText = "已复制！";
                    btn.style.background = "#52c41a";
                    setTimeout(() => {
                        btn.innerText = originalText;
                        btn.style.background = "#4a90e2";
                    }, 1000);
                });
            }
        </script>
    </head>
    <body>
        <h1>几何绘图任务核验控制台</h1>
    """

    # 遍历所有任务文件夹
    tasks = sorted(list(review_path.glob("*_task")))
    
    for task_dir in tasks:
        task_name = task_dir.name
        # 寻找图片
        original_img = next(task_dir.glob("original_*"), None)
        gen_img = task_dir / "question.png"
        code_file = task_dir / "generated_code.py"
        error_file = task_dir / "error_log.txt"

        # 读取代码内容
        code_content = ""
        if code_file.exists():
            with open(code_file, "r", encoding="utf-8") as f:
                code_content = f.read()

        status = '<span class="success-tag">● 生成成功</span>' if gen_img.exists() else '<span class="fail-tag">● 执行失败</span>'
        
        html_content += f"""
        <div class="task-card">
            <div class="task-header">{task_name} {status}</div>
            <div class="comparison">
                <div class="img-container">
                    <p>原图</p>
                    <img src="{original_img.relative_to(review_path) if original_img else ''}">
                </div>
                <div class="img-container">
                    <p>AI生成图</p>
                    <img src="{gen_img.relative_to(review_path) if gen_img.exists() else ''}" alt="未生成图片">
                </div>
                <div class="controls">
                    <button class="btn btn-copy" onclick="copyToClipboard('code_{task_name}', this)">一键复制 Python 代码</button>
                    <textarea id="code_{task_name}" style="display:none;">{code_content}</textarea>
                    
                    {"<p style='color:red; font-size:12px;'>报错详情: <br>" + open(error_file, 'r').read() + "</p>" if error_file.exists() else ""}
                </div>
            </div>
        </div>
        """

    html_content += "</body></html>"

    with open(review_path / "Review_Dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ 控制台已生成: {review_path / 'Review_Dashboard.html'}")
    print("请直接用 Chrome 浏览器打开该文件即可核验。")

if __name__ == "__main__":
    generate_dashboard()