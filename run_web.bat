@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv" (
  python -m venv .venv
  if errorlevel 1 (
    echo 创建虚拟环境失败，请确认已安装 Python 3 并加入 PATH。
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo 激活虚拟环境失败。
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r "dance_generator_rebuilt\requirements.txt"
if errorlevel 1 exit /b 1

echo 启动舞曲生成器 Web...
echo 打开 http://127.0.0.1:8000
python -m dance_generator_rebuilt.web
