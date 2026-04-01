import time
import subprocess
from pathlib import Path

# ==========================================
#                配 置 区 域
# ==========================================

# 1. Git 仓库的根目录 (执行 git add/commit/push 的位置)
GIT_REPO_DIR = r"F:\ZP\VLM-Agent"

# 2. 需要监听的具体目录 (检查包含3个文件的地方)
WATCH_DIR = r"F:\ZP\VLM-Agent\Traditional_WorkSpace\Review_Folder"

# 3. 轮询间隔时间 (单位：秒)
CHECK_INTERVAL = 5  

# 4. 触发条件：每个子文件夹需要达到的文件数量
TARGET_FILE_COUNT = 3  

# ==========================================

def run_git_command(command, cwd):
    """运行指定的 Git 命令"""
    try:
        # 运行命令，capture_output=True 用于捕获输出，text=True 将输出转为字符串
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True,
            encoding='utf-8' # 防止中文系统cmd下的编码报错
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        # 对于 git commit，如果没有文件变动会返回非零退出码，这通常是正常的
        if "nothing to commit" in e.stdout or "无文件要提交" in e.stdout or "nothing to commit" in e.stderr:
            return True, e.stdout
        return False, e.stderr or e.stdout

def check_conditions(base_path):
    """检查是否所有子文件夹都拥有指定数量的文件"""
    p = Path(base_path)
    if not p.exists() or not p.is_dir():
        # 如果监听目录还未创建，不要直接报错退出，而是等待它被创建
        print(f"[等待] 找不到监听目录: {base_path} ，等待创建中...", end="\r")
        return False

    # 获取所有子文件夹 (排除以 '.' 开头的隐藏文件夹)
    subdirs =[d for d in p.iterdir() if d.is_dir() and not d.name.startswith('.')]

    # 如果没有子文件夹，则条件不满足
    if not subdirs:
        return False

    # 遍历所有子文件夹
    for subdir in subdirs:
        # 统计该子文件夹下的文件数量 (仅统计文件，忽略子文件夹)
        file_count = sum(1 for item in subdir.iterdir() if item.is_file())
        
        # 如果任何一个文件夹的文件数量不等于目标数量，返回 False
        if file_count != TARGET_FILE_COUNT:
            return False
            
    # 如果全部遍历完没有触发 return False，说明全部满足！
    print(f"\n[!] 达成条件：{len(subdirs)} 个子文件夹均已包含 {TARGET_FILE_COUNT} 个文件。")
    return True

def auto_git_push():
    """执行 Git 提交和推送流程"""
    print(f"[!] 开始在 {GIT_REPO_DIR} 执行 Git 操作...")
    
    # 1. git add .  (将当前仓库的所有变动加入暂存区)
    success, output = run_git_command(['git', 'add', '.'], GIT_REPO_DIR)
    if not success:
        print(f"[X] Git Add 失败:\n{output}")
        return False

    # 2. git commit
    commit_msg = f"Auto upload: All Review folders reached {TARGET_FILE_COUNT} files"
    success, output = run_git_command(['git', 'commit', '-m', commit_msg], GIT_REPO_DIR)
    if not success:
        print(f"[X] Git Commit 失败:\n{output}")
        return False

    # 3. git push
    success, output = run_git_command(['git', 'push'], GIT_REPO_DIR)
    if not success:
        print(f"[X] Git Push 失败 (可能是网络或远端冲突):\n{output}")
        return False

    print("[√] Git 提交并上传云端成功！")
    return True

def main():
    print("===================================================")
    print(f"  [Git 目录]: {GIT_REPO_DIR}")
    print(f"  [监听目录]: {WATCH_DIR}")
    print(f"  等待 Review_Folder 下的所有子文件夹都包含 {TARGET_FILE_COUNT} 个文件...")
    print("===================================================")

    while True:
        try:
            # 判断条件
            if check_conditions(WATCH_DIR):
                # 触发上传
                if auto_git_push():
                    # 上传成功后，退出脚本防死循环
                    # (如果你希望一直挂机检测下一批文件，请将下方的 break 注释掉，
                    #  并确保其它程序会把旧文件夹删掉，否则会不断重复 git push)
                    break 
                else:
                    print("[!] 上传失败，10秒后重试...")
                    time.sleep(10)
            else:
                # 没满足条件，暂停等待下一轮
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n[!] 监视已手动停止。")
            break
        except Exception as e:
            print(f"\n[X] 发生异常: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()