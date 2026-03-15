#!/usr/bin/env python3
"""
快速微信启动 - 自动执行
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

print("开始自动微信启动流程...")
print("=" * 50)

# 1. 先按Win+D显示桌面（查看是否有微信快捷方式）
print("1. 显示桌面 (Win+D)")
mouse_cmd('{"action": "key", "key": "Super_L+d"}')
time.sleep(1)

# 2. 尝试点击桌面常见位置
print("2. 尝试点击桌面图标位置")
positions = [
    (100, 100), (200, 100), (100, 200), (200, 200),
    (150, 150), (250, 150), (150, 250)
]

for x, y in positions:
    print(f"  尝试位置 ({x}, {y})")
    mouse_cmd(f'{{"action": "move", "x": {x}, "y": {y}}}')
    time.sleep(0.3)
    mouse_cmd('{"action": "click", "count": 2}')  # 双击
    time.sleep(1)

# 3. 返回窗口 (Win+D)
print("3. 返回窗口")
mouse_cmd('{"action": "key", "key": "Super_L+d"}')
time.sleep(1)

# 4. 按Win键打开开始菜单
print("4. 打开开始菜单搜索")
mouse_cmd('{"action": "key", "key": "Super_L"}')
time.sleep(1)

# 5. 搜索微信
print("5. 搜索'微信'")
mouse_cmd('{"action": "type", "text": "微信"}')
time.sleep(2)

# 6. 按回车
print("6. 按回车启动")
mouse_cmd('{"action": "key", "key": "Return"}')
time.sleep(3)

# 7. 如果没反应，尝试英文
print("7. 尝试搜索'wechat'")
mouse_cmd('{"action": "key", "key": "Super_L"}')
time.sleep(1)
mouse_cmd('{"action": "type", "text": "wechat"}')
time.sleep(2)
mouse_cmd('{"action": "key", "key": "Return"}')
time.sleep(3)

# 8. 尝试Alt+Tab切换
print("8. 尝试Alt+Tab切换")
mouse_cmd('{"action": "key", "key": "Alt_L+Tab"}')
time.sleep(1)
for _ in range(3):
    mouse_cmd('{"action": "key", "key": "Tab"}')
    time.sleep(0.5)
mouse_cmd('{"action": "key", "key": "Return"}')
time.sleep(2)

print("=" * 50)
print("自动启动流程完成！")
print()
print("请检查：")
print("1. 微信是否已打开？")
print("2. 查看任务栏和桌面")
print("3. 按Alt+Tab查看所有窗口")
print()
print("如果微信已打开，请告诉我下一步操作。")
print("如果未打开，请告诉我您平时如何打开微信。")