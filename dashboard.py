import os
import html
from pathlib import Path

# 注意：这里加了 'r' 解决路径字符串中的斜杠转义问题
def generate_dashboard(review_dir=r"Traditional_WorkSpace\Review_Folder"):
    review_path = Path(review_dir).absolute()
    if not review_path.exists():
        print(f"错误：找不到文件夹 {review_path}")
        return

    IMG_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}

    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>几何绘图核验控制台 v2.0</title>
        <style>
            body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f2f5; padding: 20px; color: #333; }
            .task-card { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin: 0 auto 30px auto; max-width: 1200px; padding: 20px; border: 1px solid #e8e8e8; }
            .task-header { font-size: 1.1em; font-weight: bold; border-bottom: 2px solid #f0f0f0; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; }
            .comparison { display: flex; gap: 20px; align-items: flex-start; }
            .img-box { flex: 1; text-align: center; background: #fafafa; padding: 15px; border-radius: 8px; border: 1px solid #eee; }
            .img-box img { max-width: 100%; max-height: 400px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; }
            .controls { flex: 0 0 260px; display: flex; flex-direction: column; gap: 10px; }
            
            .btn { padding: 10px; cursor: pointer; border: none; border-radius: 6px; color: white; transition: all 0.2s; font-weight: bold; font-size: 13px; }
            .btn-blue { background: #1890ff; }
            .btn-blue:hover { background: #40a9ff; }
            .btn-green { background: #52c41a; }
            .btn-green:hover { background: #73d13d; }
            .btn-orange { background: #fa8c16; }
            .btn-orange:hover { background: #ffbb96; }
            
            .status-ok { color: #52c41a; }
            .status-fail { color: #f5222d; }
            .filename-label { font-size: 11px; color: #999; display: block; margin-bottom: 5px; }
            textarea { display: none; }
        </style>
        <script>
            // 复制纯文本
            function copyText(text, btn) {
                navigator.clipboard.writeText(text).then(() => {
                    const oldText = btn.innerText;
                    btn.innerText = "✅ 已复制内容";
                    setTimeout(() => btn.innerText = oldText, 1000);
                });
            }

            // 复制 Markdown 格式代码
            function copyMarkdown(elementId, btn) {
                const code = document.getElementById(elementId).value;
                const mdCode = "```python\\n" + code + "\\n```";
                copyText(mdCode, btn);
                btn.innerText = "✅ 已复制 Markdown";
            }

            // 复制图片到剪贴板
            async function copyImage(imgUrl, btn) {
                try {
                    const response = await fetch(imgUrl);
                    const blob = await response.blob();
                    // 注意：浏览器通常要求复制为 image/png 格式
                    const item = new ClipboardItem({ "image/png": blob });
                    await navigator.clipboard.write([item]);
                    const oldText = btn.innerText;
                    btn.innerText = "✅ 图片已入剪贴板";
                    setTimeout(() => btn.innerText = oldText, 1000);
                } catch (err) {
                    console.error(err);
                    alert("图片复制失败，可能是浏览器安全限制。请尝试：右键图片 -> 复制图像");
                }
            }
        </script>
    </head>
    <body>
        <h1 style="text-align:center;">几何绘图核验控制台</h1>
    """

    # --- 核心修改区：让任务按数字自然排序 ---
    # 1. 先过滤出所有目标文件夹
    tasks_raw =[d for d in review_path.iterdir() if d.is_dir() and d.name.endswith("_task")]
    
    # 2. 定义排序规则：提取 "_task" 前面的部分并转换为整数
    def get_task_num(path_obj):
        prefix = path_obj.name.split('_')[0]
        # 如果前缀是数字，就按数字大小排；否则放到最后面 (float('inf'))
        return int(prefix) if prefix.isdigit() else float('inf')
        
    # 3. 按照数字大小重新排序
    tasks = sorted(tasks_raw, key=get_task_num)
    # ----------------------------------------

    for task_dir in tasks:
        task_name = task_dir.name
        
        # 查找 question.png (AI生成)
        gen_img_file = task_dir / "question.png"
        gen_img_url = gen_img_file.relative_to(review_path).as_posix() if gen_img_file.exists() else None
        
        # 查找其他参考图
        other_imgs =[]
        for f in task_dir.iterdir():
            if f.is_file() and f.suffix.lower() in IMG_EXTS and f.name != "question.png":
                other_imgs.append(f.relative_to(review_path).as_posix())

        # 获取代码
        code_file = task_dir / "generated_code.py"
        code_text = code_file.read_text(encoding="utf-8") if code_file.exists() else ""
        
        # 对代码进行 HTML 转义，防止 HTML 注入破坏 DOM 结构
        safe_code_text = html.escape(code_text)

        html_content += f"""
        <div class="task-card">
            <div class="task-header">
                <span>任务文件夹: {task_name}</span>
                <span class="{'status-ok' if gen_img_url else 'status-fail'}">
                    {'● 生成成功' if gen_img_url else '● 生成失败'}
                </span>
            </div>
            <div class="comparison">
                <!-- 左：参考图 -->
                <div class="img-box">
                    <p style="font-size:12px; color:#666;">原题参考图</p>
                    {''.join([f'<img src="{u}">' for u in other_imgs]) if other_imgs else '无原图'}
                </div>
                
                <!-- 中：AI结果 -->
                <div class="img-box">
                    <p style="font-size:12px; color:#666;">AI 生成图 (question.png)</p>
                    { f'<img src="{gen_img_url}" id="img_{task_name}">' if gen_img_url else '没有图片' }
                    <br>
                    { f'<button class="btn btn-orange" onclick="copyImage(\'{gen_img_url}\', this)">复制该图片</button>' if gen_img_url else '' }
                </div>
                
                <!-- 右：操作区 -->
                <div class="controls">
                    <textarea id="code_{task_name}">{safe_code_text}</textarea>
                    
                    <button class="btn btn-blue" onclick="copyText(document.getElementById('code_{task_name}').value, this)">
                        复制纯代码内容
                    </button>
                    
                    <button class="btn btn-green" onclick="copyMarkdown('code_{task_name}', this)">
                        复制 Markdown 代码块
                    </button>

                    <div style="margin-top:20px; font-size:11px; color:#999; border-top:1px solid #eee; padding-top:10px;">
                        💡 <b>提示：</b><br>
                        如果网站对文件名有严格要求，点击复制图片后在某些网站可能变为 image.png。最稳妥的方法是从文件夹直接拖拽 question.png 上传。
                    </div>
                </div>
            </div>
        </div>
        """

    html_content += "</body></html>"
    
    output_file = review_path / "Review_Dashboard.html"
    output_file.write_text(html_content, encoding="utf-8")
    print(f"✅ 更新完成！控制台: {output_file}")

if __name__ == "__main__":
    generate_dashboard()