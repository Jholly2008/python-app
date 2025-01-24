@echo off
echo Starting Instagram Service...

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: 检查是否需要安装依赖
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)


:: 基于Firefox初始化cookie文件
:: python 615_import_firefox_session.py

:: 启动应用
echo Starting application...
python app.py

:: 保持窗口打开
pause
