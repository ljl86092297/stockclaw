@echo off
chcp 65001 >nul
echo ================================
echo 微信窗口激活工具
echo ================================
echo 时间: %date% %time%
echo.

echo 1. 检查微信进程...
tasklist | findstr /i "WeChat"
if %errorlevel% equ 0 (
    echo   微信正在运行
) else (
    echo   微信未运行，尝试启动...
    start wechat:
    timeout /t 5 /nobreak >nul
)

echo.
echo 2. 激活微信窗口...
echo   按Alt+Tab切换到微信...
echo   请观察屏幕变化...
echo.

echo 3. 发送测试消息...
echo   将模拟按键操作...
echo   请确保微信窗口在前台...
echo.

echo 按任意键开始执行（或Ctrl+C取消）...
pause >nul

echo.
echo 正在执行操作...
echo.

REM 使用VBScript发送按键
echo Set WshShell = WScript.CreateObject("WScript.Shell") > temp.vbs
echo WshShell.AppActivate "微信" >> temp.vbs
echo WScript.Sleep 1000 >> temp.vbs
echo WshShell.SendKeys "%%" >> temp.vbs  REM Alt键
echo WScript.Sleep 500 >> temp.vbs
echo WshShell.SendKeys "{TAB}" >> temp.vbs
echo WScript.Sleep 300 >> temp.vbs
echo WshShell.SendKeys "{TAB}" >> temp.vbs
echo WScript.Sleep 300 >> temp.vbs
echo WshShell.SendKeys "~" >> temp.vbs  REM 回车
echo WScript.Sleep 2000 >> temp.vbs

echo WshShell.SendKeys "^f" >> temp.vbs  REM Ctrl+F
echo WScript.Sleep 1000 >> temp.vbs
echo WshShell.SendKeys "宝宝/:heart十月初一" >> temp.vbs
echo WScript.Sleep 2000 >> temp.vbs
echo WshShell.SendKeys "~" >> temp.vbs  REM 回车
echo WScript.Sleep 1000 >> temp.vbs

echo WshShell.SendKeys "[批处理测试]这是通过批处理发送的消息" >> temp.vbs
echo WScript.Sleep 1000 >> temp.vbs
echo WshShell.SendKeys "~" >> temp.vbs  REM 回车
echo WScript.Sleep 1000 >> temp.vbs

cscript //nologo temp.vbs
del temp.vbs

echo.
echo ================================
echo 操作完成！
echo ================================
echo 请检查：
echo 1. 微信窗口是否已激活？
echo 2. 是否发送了测试消息？
echo 3. 消息内容：[批处理测试]这是通过批处理发送的消息
echo.
echo 如果成功，请回复"批处理成功"
echo 如果失败，请描述看到的现象
echo.
pause