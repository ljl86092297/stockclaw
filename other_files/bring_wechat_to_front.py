#!/usr/bin/env python3
"""
确保微信窗口在最前面
"""

import subprocess
import time

def mouse_cmd(cmd):
    result = subprocess.run(
        ['python3', 'openclaw_mouse_control.py', cmd],
        capture_output=True,
        text=True
    )
    return result.stdout

def press_key(keys):
    for key in keys.split('+'):
        mouse_cmd(f'{{"action": "key", "key": "{key}"}}')
        time.sleep(0.1)
    time.sleep(0.5)

def click(x, y):
    mouse_cmd(f'{{"action": "move", "x": {x}, "y": {y}}}')
    time.sleep(0.3)
    mouse_cmd('{"action": "click"}')
    time.sleep(0.5)

print("=== 确保微信窗口在最前面 ===")
print("时间:", time.strftime("%H:%M:%S"))
print()

# 方法1: 强力Alt+Tab组合
print("方法1: 强力Alt+Tab组合")
print("1. 按住Alt，多次按Tab")
press_key('Alt_L')
time.sleep(0.5)

# 模拟按住Alt时多次按Tab
for i in range(8):  # 尝试8次切换
    print(f"  第{i+1}次Tab切换")
    mouse_cmd('{"action": "key", "key": "Tab"}')
    time.sleep(0.3)

# 松开Alt并确认
mouse_cmd('{"action": "key", "key": "Alt_L"}')  # 松开Alt
time.sleep(0.5)
mouse_cmd('{"action": "key", "key": "Return"}')
time.sleep(2)

print("2. 检查是否切换到微信")
print("   等待2秒观察窗口变化...")
time.sleep(2)

# 方法2: 如果微信在任务栏，直接点击
print("\n方法2: 直接点击任务栏微信图标")
print("1. 将鼠标移动到任务栏")
print("   从左侧开始扫描任务栏...")

# 扫描任务栏寻找微信图标
for x in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800]:
    print(f"   尝试位置 x={x}")
    click(x, 1070)  # 任务栏底部
    time.sleep(0.5)
    
    # 点击后等待观察
    time.sleep(1)
    
    # 如果激活了微信，尝试发送测试消息
    print("   尝试发送测试消息...")
    mouse_cmd('{"action": "type", "text": "[测试]窗口激活测试"}')
    time.sleep(0.5)
    mouse_cmd('{"action": "key", "key": "Return"}')
    time.sleep(1)

# 方法3: 使用Win+数字键（如果微信固定在任务栏）
print("\n方法3: Win+数字键快捷方式")
print("尝试Win+1到Win+0")

for num in range(1, 10):
    print(f"  尝试Win+{num}")
    press_key(f'Super_L+{num}')
    time.sleep(1)
    
    # 检查是否激活了微信
    mouse_cmd('{"action": "type", "text": f"[Win+{num}测试]"}')
    time.sleep(0.5)
    mouse_cmd('{"action": "key", "key": "Return"}')
    time.sleep(1)

# 方法4: 最小化所有窗口然后恢复
print("\n方法4: 最小化所有窗口")
print("1. Win+D显示桌面")
press_key('Super_L+d')
time.sleep(1)

print("2. 再次Win+D恢复窗口")
press_key('Super_L+d')
time.sleep(2)

print("3. 尝试Alt+Tab选择微信")
press_key('Alt_L+Tab')
time.sleep(1)
mouse_cmd('{"action": "key", "key": "Tab"}')
time.sleep(0.5)
mouse_cmd('{"action": "key", "key": "Tab"}')
time.sleep(0.5)
mouse_cmd('{"action": "key", "key": "Return"}')
time.sleep(2)

print("\n=== 所有方法尝试完成 ===")
print("请立即检查:")
print("1. 微信窗口是否现在在最前面？")
print("2. 是否看到任何测试消息？")
print("3. 窗口标题栏是否高亮显示？")

print("\n如果微信在最前面了，请告诉我:")
print("1. '微信已在前台'")
print("2. 然后我可以继续发送消息给'宝宝/:heart十月初一'")