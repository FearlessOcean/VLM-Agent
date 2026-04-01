@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo   几何绘图脚本批量强制执行工具 (Geometry Drawer Bat)
echo ======================================================

:: 设定目标根目录
set "TARGET_DIR=Traditional_WorkSpace\Review_Folder"

if not exist "%TARGET_DIR%" (
    echo [错误] 找不到文件夹: %TARGET_DIR%
    pause
    exit /b
)

echo [*] 开始扫描所有生成的 python 代码...
echo.

:: 遍历 Review_Folder 下的所有子文件夹
for /d %%i in ("%TARGET_DIR%\*") do (
    set "TASK_PATH=%%i"
    set "CODE_FILE=%%i\generated_code.py"
    
    if exist "!CODE_FILE!" (
        echo [正在运行] !TASK_PATH!
        
        :: 切换到子文件夹路径，这样生成的图片会保存在子文件夹内
        pushd "!TASK_PATH!"
        
        :: 执行 Python
        python generated_code.py
        
        if !errorlevel! equ 0 (
            echo   [OK] 绘制完成.
        ) else (
            echo   [FAIL] 代码运行出错，请检查该目录下的错误日志.
        )
        
        :: 返回主目录
        popd
    ) else (
        echo [跳过] !TASK_PATH! (未发现 generated_code.py)
    )
    echo ------------------------------------------------------
)

echo.
echo [任务结束] 所有代码已尝试运行完毕。
pause