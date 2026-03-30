import os
from pathlib import Path

def generate_dashboard(workspace_dir="LangChain-WorkSpace", output_file="dashboard.html"):
    workspace = Path(workspace_dir)
    if not workspace.exists():
        print(f"❌ 找不到工作目录 '{workspace_dir}'，请先运行大模型生成代码。")
        return

    # 支持的图片后缀
    valid_extensions = {".jpg", ".jpeg", ".png"}
    original_images = sorted([
        f for f in workspace.iterdir() 
        if f.is_file() and f.suffix.lower() in valid_extensions
    ])

    if not original_images:
        print(f"⚠️ 在 '{workspace_dir}' 目录下没有找到任何原图，无法生成仪表盘。")
        return

    # ---------------- 极简表格 HTML & JS 脚本 ---------------- 
    html_content =[
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>测试结果对照看板</title>",
        "<style>",
        "  body { font-family: sans-serif; margin: 20px; }",
        "  h1 { text-align: center; }",
        "  table { width: 100%; border-collapse: collapse; margin-top: 20px; }",
        "  th, td { border: 1px solid #ccc; padding: 15px 10px; text-align: center; vertical-align: top; }",
        "  th { background-color: #f2f2f2; }",
        "  img { max-width: 350px; max-height: 350px; object-fit: contain; }",
        "  .code-cell { text-align: left; max-width: 450px; }",
        "  pre { background: #f8f9fa; padding: 10px; overflow-x: auto; font-size: 13px; border: 1px solid #ddd; margin-top: 5px; }",
        "  .error-text { color: red; font-weight: bold; }",
        "  .success-text { color: green; font-weight: bold; }",
        "  details { margin-top: 10px; }",
        "  summary { cursor: pointer; color: #0366d6; font-weight: bold; margin-bottom: 8px; }",
        "  .btn { cursor: pointer; padding: 6px 12px; font-size: 13px; border: 1px solid #bbb; border-radius: 4px; background: #fff; transition: background 0.2s; font-weight: bold; }",
        "  .btn:hover { background: #e9ecef; }",
        "  .btn-container { margin-top: 10px; }",
        "  .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px dashed #ddd; padding-bottom: 10px; }",
        "</style>",
        "<script>",
        "  // 复制图片到剪贴板",
        "  async function copyImg(imgId, btn) {",
        "      const originalText = btn.innerHTML;",
        "      try {",
        "          const img = document.getElementById(imgId);",
        "          const canvas = document.createElement('canvas');",
        "          canvas.width = img.naturalWidth || img.width;",
        "          canvas.height = img.naturalHeight || img.height;",
        "          const ctx = canvas.getContext('2d');",
        "          ctx.drawImage(img, 0, 0);",
        "          canvas.toBlob(async (blob) => {",
        "              await navigator.clipboard.write([new ClipboardItem({'image/png': blob})]);",
        "              btn.innerHTML = '✅ 已复制图片';",
        "              setTimeout(() => btn.innerHTML = originalText, 2000);",
        "          }, 'image/png');",
        "      } catch (err) {",
        "          alert('复制失败，浏览器可能因本地权限拦截，请右键图片复制。');",
        "      }",
        "  }",
        "  // 复制代码（含Markdown包裹）到剪贴板",
        "  async function copyMd(codeId, btn) {",
        "      const originalText = btn.innerHTML;",
        "      try {",
        "          /* 此处关键修正：改为 textContent 从而在代码被折叠（隐藏）时不丢失文本内容 */ ",
        "          const codeText = document.getElementById(codeId).textContent;",
        "          const markdown = '```python\\n' + codeText + '\\n```';",
        "          await navigator.clipboard.writeText(markdown);",
        "          btn.innerHTML = '✅ 已复制 Markdown';",
        "          setTimeout(() => btn.innerHTML = originalText, 2000);",
        "      } catch (err) {",
        "          alert('复制失败！');",
        "      }",
        "  }",
        "</script>",
        "</head>",
        "<body>",
        "<h1>📊 测试结果对照看板</h1>",
        "<table>",
        "  <tr>",
        "    <th width='15%'>任务原图名称</th>",
        "    <th width='25%'>原图 (Original)</th>",
        "    <th width='25%'>生成图 (Generated)</th>",
        "    <th width='35%'>运行状态 & 代码</th>",
        "  </tr>"
    ]

    for idx, img_file in enumerate(original_images):
        stem = img_file.stem
        output_folder = workspace / f"{stem}_output"
        gen_image = output_folder / "question.png"
        code_file = output_folder / "generated_code.py"
        error_file = output_folder / "error_log.txt"

        has_error = error_file.exists()
        has_gen_image = gen_image.exists()

        rel_orig_img = f"{workspace_dir}/{img_file.name}".replace('\\', '/')
        rel_gen_img = f"{workspace_dir}/{output_folder.name}/question.png".replace('\\', '/')
        
        # 赋予每一行的图片和代码唯一 ID，用于 JS 抓取
        img_id = f"gen_img_{idx}"
        code_id = f"code_{idx}"

        html_content.append("  <tr>")
        
        # 1. 任务名称
        html_content.append(f"    <td><strong>{img_file.name}</strong></td>")
        
        # 2. 原图
        html_content.append(f"    <td><a href='{rel_orig_img}' target='_blank'><img src='{rel_orig_img}'></a></td>")
        
        # 3. 生成图
        if has_gen_image:
            html_content.append(f"    <td>")
            html_content.append(f"      <a href='{rel_gen_img}' target='_blank'><img id='{img_id}' src='{rel_gen_img}'></a>")
            html_content.append(f"      <div class='btn-container'>")
            html_content.append(f"          <button class='btn' onclick='copyImg(\"{img_id}\", this)'>📋 复制图片</button>")
            html_content.append(f"      </div>")
            html_content.append(f"    </td>")
        else:
            html_content.append("    <td class='error-text'><br><br>未生成图片<br>(渲染失败)</td>")

        # 4. 代码与状态区
        html_content.append("    <td class='code-cell'>")
        
        # ---- 顶部常驻栏：渲染状态 & 外部的一键复制按钮 ----
        html_content.append("      <div class='top-bar'>")
        if has_error:
            html_content.append("        <span class='error-text'>❌ 渲染报错</span>")
        else:
            html_content.append("        <span class='success-text'>✅ 渲染成功</span>")
        
        if code_file.exists():
            html_content.append(f"        <button class='btn' onclick='copyMd(\"{code_id}\", this)'>📋 复制代码</button>")
        
        html_content.append("      </div>")

        # ---- 报错面板（仅报错时出现并默认展开） ----
        if has_error:
            error_text = error_file.read_text(encoding="utf-8").replace("<", "&lt;").replace(">", "&gt;")
            html_content.append(f"      <details open><summary>查看报错日志</summary><pre>{error_text}</pre></details>")

        # ---- 代码面板（成功生成时默认折叠） ----
        if code_file.exists():
            code_text = code_file.read_text(encoding="utf-8").replace("<", "&lt;").replace(">", "&gt;")
            # 如果有错展开，没错就折叠
            open_attr = "open" if has_error else ""
            html_content.append(f"      <details {open_attr}><summary>查看 Python 源码</summary>")
            html_content.append(f"        <pre id='{code_id}'>{code_text}</pre>")
            html_content.append(f"      </details>")
        
        html_content.append("    </td>")
        html_content.append("  </tr>")

    html_content.append("</table>")
    html_content.append("</body>")
    html_content.append("</html>")

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print(f"🎉 仪表盘带复制功能（按钮外置版）生成完毕！")
    print(f"👉 请在浏览器中打开: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    generate_dashboard()