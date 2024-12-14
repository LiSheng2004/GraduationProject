@chcp 65001 > nul
@echo off
:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo 正在以管理员身份运行...
    powershell -Command "Start-Process cmd -ArgumentList '/c F:\计算理论\龙卷风接口调用范例-VC\run_test.bat' -Verb RunAs"
    exit
)

:: 切换到目标目录
cd /d "%~dp0"  

:: 执行Python脚本
python "requests.py"

pause
