@echo off
chcp 65001 > nul 2>&1

echo.
echo 正在启动 Topos Power...
echo ----------------------------------------

:: 进入脚本所在目录，避免从其他路径启动时找不到 src。
cd /d "%~dp0"

:: 优先使用项目虚拟环境中的 Python。
if exist ".venv\Scripts\python.exe" (
    echo 找到 .venv，使用虚拟环境 Python...
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    echo 未找到 .venv，使用系统 Python...
    where py > nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=py"
    ) else (
        where python > nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=python"
        ) else (
            echo.
            echo 未找到 Python，请安装 Python 3 或创建虚拟环境
            echo.
            pause
            exit /b 1
        )
    )
)

:: src 布局下，即使尚未执行 pip install -e . 也能直接运行。
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

:: 提前给出依赖提示，但把最终错误交给 Python 输出。
%PYTHON_CMD% -c "import PyQt6" > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 警告: PyQt6 未安装，请运行: pip install -r requirements.txt
    echo.
)

echo.
echo 启动 Topos Power...
echo ----------------------------------------
%PYTHON_CMD% -m topos_power
set "EXIT_CODE=%errorlevel%"

echo.
echo 程序已退出（代码: %EXIT_CODE%）
pause
exit /b %EXIT_CODE%
