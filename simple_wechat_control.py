#!/usr/bin/env python3
"""
最简单的微信控制脚本
通过WSL调用Windows Python执行
"""

import subprocess
import time

print("=== 微信控制 - 简单方法 ===")
print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
print()

# 方法1: 直接通过cmd发送按键
print("方法1: 通过cmd发送按键到微信")
print("1. 激活微信窗口")

# 创建VBScript发送按键
vbs_script = '''
Set WshShell = WScript.CreateObject("WScript.Shell")
' 尝试激活微信窗口
WshShell.AppActivate "微信"
WScript.Sleep 1000

' 发送测试消息
WshShell.SendKeys "^f"  ' Ctrl+F搜索
WScript.Sleep 1000
WshShell.SendKeys "宝宝/:heart十月初一"
WScript.Sleep 2000
WshShell.SendKeys "{ENTER}"
WScript.Sleep 1000
WshShell.SendKeys "[VBS测试]这是通过VBScript发送的消息"
WScript.Sleep 1000
WshShell.SendKeys "{ENTER}"
'''

# 保存并执行VBScript
with open('/tmp/wechat_control.vbs', 'w', encoding='utf-8') as f:
    f.write(vbs_script)

print("2. 执行VBScript控制脚本")
try:
    result = subprocess.run(
        ['cmd.exe', '/c', 'cscript', '//nologo', '//wsl.localhost/Ubuntu/tmp/wechat_control.vbs'],
        capture_output=True,
        text=True,
        timeout=10
    )
    print("   执行结果:", result.returncode)
except Exception as e:
    print("   执行失败:", e)

print()
print("方法2: 使用Windows Python的pyautogui")
print("注意: 需要Windows Python环境")

windows_python_code = '''
import pyautogui
import time
import subprocess

print("=== Windows Python控制微信 ===")

# 检查微信是否运行
result = subprocess.run(["tasklist", "|", "findstr", "WeChat"], 
                       shell=True, capture_output=True)
if "WeChat" in result.stdout.decode("gbk", errors="ignore"):
    print("微信正在运行")
else:
    print("微信未运行")

# 激活微信窗口（假设在任务栏）
print("激活微信窗口...")
pyautogui.hotkey("alt", "tab")
time.sleep(1)
pyautogui.press("tab")
time.sleep(0.5)
pyautogui.press("tab")
time.sleep(0.5)
pyautogui.press("enter")
time.sleep(2)

# 发送消息
print("发送测试消息...")
pyautogui.hotkey("ctrl", "f")  # 搜索
time.sleep(1)
pyautogui.write("宝宝/:heart十月初一")
time.sleep(2)
pyautogui.press("enter")
time.sleep(1)
pyautogui.write("[Python测试]这是通过Windows Python发送的消息")
time.sleep(1)
pyautogui.press("enter")

print("操作完成！")
'''

print("3. 尝试在Windows Python中执行")
try:
    # 通过cmd调用Windows Python
    result = subprocess.run(
        ['cmd.exe', '/c', 'python', '-c', windows_python_code],
        capture_output=True,
        text=True,
        timeout=15
    )
    print("   Windows Python输出:", result.stdout[:200] if result.stdout else "无输出")
except Exception as e:
    print("   执行失败:", e)

print()
print("=== 所有方法尝试完成 ===")
print("请检查微信:")
print("1. 窗口是否被激活？")
print("2. 是否收到测试消息？")
print("3. 消息内容是否包含'[测试]'字样？")
print()
print("如果看到任何变化，请描述:")
print("- '微信窗口激活了'")
print("- '收到了X条测试消息'")
print("- '没看到任何变化'")