#!/usr/bin/env python3
import subprocess
import time
import sys
import os

def test_xdotool():
    """测试xdotool功能"""
    print("=== 测试xdotool ===")
    try:
        # 测试获取鼠标位置
        result = subprocess.run(['xdotool', 'getmouselocation'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ xdotool可用: {result.stdout.strip()}")
            
            # 测试移动鼠标
            print("测试鼠标移动...")
            subprocess.run(['xdotool', 'mousemove', '100', '100'])
            time.sleep(1)
            
            # 测试点击
            print("测试鼠标点击...")
            subprocess.run(['xdotool', 'click', '1'])
            time.sleep(0.5)
            
            # 返回原位置
            coords = result.stdout.strip().split()
            x = coords[0].split(':')[1]
            y = coords[1].split(':')[1]
            subprocess.run(['xdotool', 'mousemove', x, y])
            
            return True
        else:
            print("✗ xdotool命令执行失败")
            return False
    except Exception as e:
        print(f"✗ xdotool测试失败: {e}")
        return False

def test_pyautogui():
    """测试pyautogui功能"""
    print("\n=== 测试pyautogui ===")
    try:
        import pyautogui
        print("✓ pyautogui导入成功")
        
        # 获取屏幕信息
        screen_width, screen_height = pyautogui.size()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()
        print(f"当前鼠标位置: ({current_x}, {current_y})")
        
        # 测试移动鼠标
        print("测试鼠标移动...")
        pyautogui.moveTo(200, 200, duration=0.5)
        time.sleep(0.5)
        
        # 测试点击
        print("测试鼠标点击...")
        pyautogui.click()
        time.sleep(0.5)
        
        # 返回原位置
        pyautogui.moveTo(current_x, current_y, duration=0.5)
        
        return True
    except ImportError:
        print("✗ pyautogui未安装")
        return False
    except Exception as e:
        print(f"✗ pyautogui测试失败: {e}")
        return False

def test_keyboard_control():
    """测试键盘控制"""
    print("\n=== 测试键盘控制 ===")
    try:
        # 使用xdotool测试键盘输入
        print("测试键盘输入...")
        subprocess.run(['xdotool', 'type', 'Hello from OpenClaw!'])
        time.sleep(0.5)
        
        # 测试回车键
        subprocess.run(['xdotool', 'key', 'Return'])
        
        print("✓ 键盘控制测试完成")
        return True
    except Exception as e:
        print(f"✗ 键盘控制测试失败: {e}")
        return False

def main():
    print("开始测试鼠标控制功能...")
    print(f"DISPLAY环境变量: {os.environ.get('DISPLAY', '未设置')}")
    
    # 测试各种控制方法
    methods = [
        ("xdotool", test_xdotool),
        ("pyautogui", test_pyautogui),
        ("keyboard", test_keyboard_control)
    ]
    
    available_methods = []
    for name, test_func in methods:
        try:
            if test_func():
                available_methods.append(name)
        except Exception as e:
            print(f"{name}测试异常: {e}")
    
    print(f"\n=== 测试总结 ===")
    if available_methods:
        print(f"✓ 可用的控制方法: {', '.join(available_methods)}")
        print("\n下一步:")
        print("1. 可以创建自动化脚本")
        print("2. 可以集成到OpenClaw工具中")
        print("3. 可以执行复杂的鼠标/键盘操作")
    else:
        print("✗ 未找到可用的控制方法")
        print("\n建议:")
        print("1. 检查DISPLAY环境变量")
        print("2. 确保X11转发正常工作")
        print("3. 尝试安装其他工具如xte、xinput等")

if __name__ == "__main__":
    main()