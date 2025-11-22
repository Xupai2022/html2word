@echo off
echo 正在激活虚拟环境...
set PYTHONPATH=%~dp0venv\Lib\site-packages;%PYTHONPATH%
set PATH=%~dp0venv\Scripts;%~dp0venv\bin;%PATH%
echo 虚拟环境已激活！
echo.
echo 你可以直接运行 html2word-converter.exe
echo 或运行 Python 脚本:
echo   python src\html2word\converter.py
echo.
