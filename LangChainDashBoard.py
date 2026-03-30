import os
from pathlib import Path

def generate_dashboard(workspace_dir="LangChain-WorkSpace", output_file="dashboard.html"):
    workspace = Path(workspace_dir)
    if not workspace.exists():
        print(f"❌ 找不到工作目录 '{workspace_dir}'，请先运行你的大模型生成代码。")
        return

    # 支持的图片后缀
    valid_extensions = {".jpg", ".jpeg", ".png"}
    # 扫描根目录下的所有原图
    original_images =[
        f for f in workspace.iterdir() 
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]

    if not original_images:
        print(f"⚠️ 在 '{workspace_dir}' 目录下没有找到任何原图，无法生成仪表盘。")
        return

    # ---------------- 仪表盘 HTML 前端模板 ---------------- 
    html_content =[
        "<!DOCTYPE html>",
        "<html lang='zh-CN'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>数学几何绘图审查仪表盘 📐</title>",
        "<style>",
        "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }",
        "h1 { text-align: center; color: #2c3e50; margin-bottom: 40px; }",
        ".card { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 40px; overflow: hidden; border: 1px solid #e1e4e8; }",
        ".card-header { background: #2c3e50; color: white; padding: 15px 25px; font-size: 1.1em; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }",
        ".status { padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; }",
        ".status.success { background: #2ecc71; color: white; }",
        ".status.error { background: #e74c3c; color: white; }",
        ".card-body { padding: 25px; }",
        ".img-comparison { display: flex; gap: 30px; flex-wrap: wrap; margin-bottom: 20px; }",
        ".img-box { flex: 1; min-width: 320px; text-align: center; border: 2px dashed #d1d8e0; padding: 15px; border-radius: 8px; background: #fafbfc; position: relative; }",
        ".img-box img { max-width: 100%; height: auto; max-height: 400px; object-fit: contain; cursor: pointer; transition: transform 0.2s; }",
        ".img-box img:hover { transform: scale(1.02); }",
        ".img-box h3 { margin-top: 0; margin-bottom: 15px; color: #7f8c8d; font-size: 1.1em; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }",
        ".code-section, .error-section { margin-top: 20px; border-top: 1px solid #ecf0f1; padding-top: 15px; }",
        "pre { background: #282c34; color: #abb2bf; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: 'Fira Code', Consolas, Monaco, monospace; font-size: 0.95em; border: 1px solid #1e2127; }",
        ".error-log pre { background: #fdf5f6; color: #cb2431; border: 1px solid #f8c9d1; }",
        "details summary { cursor: pointer; font-weight: bold; color: #0366d6; user-select: none; font-size: 1.05em; padding: 5px 0; }",
        "details summary:hover { color: #005cc5; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>📐 Python & Matplotlib 几何绘图复刻审阅仪表盘</h1>"
    ]

    # 按文件名称做一层排序
    for img_file in sorted(original_images):
        stem = img_file.stem  # 文件名无后缀 (如 q1)
        output_folder = workspace / f"{stem}_output"
        gen_image = output_folder / "question.png"
        code_file = output_folder / "generated_code.py"
        error_file = output_folder / "error_log.txt"

        # 判断状态
        has_error = error_file.exists()
        has_gen_image = gen_image.exists()
        
        status_class = "error" if has_error else "success"
        status_text = "渲染失败 ❌" if has_error else "渲染成功 ✨"

        # 处理相对路径，供 HTML 使用 (兼容 Windows/Mac)
        rel_orig_img = f"{workspace_dir}/{img_file.name}".replace('\\', '/')
        rel_gen_img = f"{workspace_dir}/{output_folder.name}/question.png".replace('\\', '/')

        # 构建任务卡片
        html_content.append("<div class='card'>")
        html_content.append(f"<div class='card-header'><span>📄 任务原图: {img_file.name}</span> <span class='status {status_class}'>{status_text}</span></div>")
        html_content.append("<div class='card-body'>")
        
        # ========== 图片并排对比部分 ==========
        html_content.append("<div class='img-comparison'>")
        
        # 1. 提供给大模型的原始题图
        html_content.append("<div class='img-box'>")
        html_content.append("<h3>🖼️ 提供给 AI 的原图 (Original)</h3>")
        html_content.append(f"<a href='{rel_orig_img}' target='_blank'><img src='{rel_orig_img}' alt='Original'></a>")
        html_content.append("</div>")

        # 2. AI 产出的生成的图
        html_content.append("<div class='img-box'>")
        html_content.append("<h3>✨ AI 生成的 Matplotlib 渲染图 (Result)</h3>")
        if has_gen_image:
            html_content.append(f"<a href='{rel_gen_img}' target='_blank'><img src='{rel_gen_img}' alt='Generated'></a>")
        else:
            html_content.append("<div style='color:#e74c3c; padding: 60px 0; font-size: 18px;'>⚠️ 未生成图片（请查看代码或报错）</div>")
        html_content.append("</div>")

        html_content.append("</div>") # 图片对比结束

        # ========== 代码检查部分 ==========
        if code_file.exists():
            code_text = code_file.read_text(encoding="utf-8")
            # HTML 转义，防止由于代码里的 < > 导致前端页面崩盘
            code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_content.append("<div class='code-section'>")
            # 无报错默认折叠代码，有报错时可以选择展开
            html_content.append("<details><summary>💻 点击查看生成的 Python 代码</summary>")
            html_content.append(f"<pre><code>{code_text}</code></pre>")
            html_content.append("</details>")
            html_content.append("</div>")

        # ========== 报错日志部分 ==========
        if has_error:
            error_text = error_file.read_text(encoding="utf-8")
            error_text = error_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_content.append("<div class='error-section error-log'>")
            # 如果有错误，默认展开报错面板
            html_content.append("<details open><summary>🚨 渲染失败！点击查看报错日志 (Error Log)</summary>")
            html_content.append(f"<pre>{error_text}</pre>")
            html_content.append("</details>")
            html_content.append("</div>")

        html_content.append("</div>") # card-body 结束
        html_content.append("</div>") # card 结束

    html_content.append("</body></html>")

    # 写入最终的 HTML 文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print(f"🎉 仪表盘已生成完毕！")
    print(f"👉 【使用方法】: 请在浏览器中双击打开该文件: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # 执行生成
    generate_dashboard()