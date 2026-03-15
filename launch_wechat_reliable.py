#!/usr/bin/env python3
"""
可靠的微信启动脚本
针对WSL环境优化
"""

import subprocess
import time
import os
import sys

def run_windows_command(cmd):
    """在Windows中执行命令"""
    try:
        # 通过cmd.exe执行
        full_cmd = f'cmd.exe /c "{cmd}"'
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def run_powershell_command(cmd):
    """通过PowerShell执行命令"""
    try:
        full_cmd = f'powershell.exe -Command "{cmd}"'
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def check_wechat_process():
    """检查微信进程（Windows端）"""
    try:
        # 使用tasklist检查Windows进程
        cmd = 'tasklist | findstr /i wechat'
        result = subprocess.run(
            f'cmd.exe /c "{cmd}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return "WeChat.exe" in result.stdout
    except:
        return False

def launch_wechat():
    """启动微信"""
    print("=== 尝试启动微信 ===")
    
    methods = [
        # 方法1：直接启动
        ("直接启动", 'start wechat:'),
        
        # 方法2：通过URI协议
        ("URI协议", 'start weixin:'),
        
        # 方法3：尝试常见路径
        ("常见路径", 'start "C:\\Program Files\\Tencent\\WeChat\\WeChat.exe"'),
        ("常见路径x86", 'start "C:\\Program Files (x86)\\Tencent\\WeChat\\WeChat.exe"'),
        
        # 方法4：用户目录
        ("用户目录", 'start "%LOCALAPPDATA%\\Tencent\\WeChat\\WeChat.exe"'),
        
        # 方法5：搜索并启动
        ("搜索启动", 'for /f "tokens=*" %i in (\'where wechat.exe\') do start "" "%i"'),
        
        # 方法6：通过开始菜单
        ("开始菜单", 'start shell:AppsFolder\\TencentWeChatLimited.WeChat'),
    ]
    
    for method_name, command in methods:
        print(f"\n尝试方法: {method_name}")
        print(f"命令: {command}")
        
        try:
            if run_windows_command(command):
                print("  ✓ 命令执行成功")
                time.sleep(3)  # 等待启动
                
                # 检查是否启动成功
                if check_wechat_process():
                    print("  ✓ 微信进程已启动")
                    return True
                else:
                    print("  ✗ 微信进程未检测到")
            else:
                print("  ✗ 命令执行失败")
                
        except Exception as e:
            print(f"  ✗ 异常: {e}")
    
    return False

def alternative_methods():
    """备用方法"""
    print("\n=== 尝试备用方法 ===")
    
    # 方法A：创建桌面快捷方式并点击
    print("\n方法A: 模拟用户操作")
    try:
        # 按Win键打开开始菜单
        subprocess.run(['xdotool', 'key', 'Super_L'], timeout=2)
        time.sleep(1)
        
        # 输入"wechat"
        subprocess.run(['xdotool', 'type', 'wechat'], timeout=2)
        time.sleep(2)
        
        # 按回车
        subprocess.run(['xdotool', 'key', 'Return'], timeout=2)
        time.sleep(3)
        
        if check_wechat_process():
            print("  ✓ 通过模拟操作可能已启动")
            return True
    except:
        pass
    
    # 方法B：使用wslg（如果可用）
    print("\n方法B: 使用WSLg")
    try:
        # 尝试通过Linux端启动（如果安装了Linux版微信）
        result = subprocess.run(
            ['which', 'wechat'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            wechat_path = result.stdout.strip()
            print(f" 找到Linux版微信: {wechat_path}")
            subprocess.Popen([wechat_path], start_new_session=True)
            time.sleep(3)
            return True
    except:
        pass
    
    return False

def main():
    """主函数"""
    print("微信启动助手 - WSL环境专用")
    print("=" * 50)
    
    # 首先检查是否已经在运行
    print("\n1. 检查微信是否已在运行...")
    if check_wechat_process():
        print("✓ 微信已经在运行中！")
        print("\n微信登录界面应该已经显示")
        print("如果看不到，请检查:")
        print("1. 任务栏是否有微信图标")
        print("2. 通知区域是否有微信")
        print("3. 按Alt+Tab切换窗口")
        return True
    
    print("微信未运行，开始启动流程...")
    
    # 尝试主要方法
    if launch_wechat():
        print("\n" + "=" * 50)
        print("✓ 微信启动成功！")
        print("\n请检查:")
        print("1. 桌面或任务栏上的微信窗口")
        print("2. 系统通知区域的微信图标")
        print("3. 按Alt+Tab查看所有窗口")
        return True
    
    # 尝试备用方法
    print("\n主要方法失败，尝试备用方法...")
    if alternative_methods():
        print("\n" + "=" * 50)
        print("✓ 通过备用方法可能已启动微信")
        return True
    
    # 所有方法都失败
    print("\n" + "=" * 50)
    print("✗ 无法启动微信")
    print("\n可能的原因:")
    print("1. 微信未安装在Windows系统中")
    print("2. WSL图形支持配置问题")
    print("3. 微信需要手动安装或更新")
    
    print("\n建议:")
    print("1. 请手动打开微信，然后我可以帮您操作")
    print("2. 或者告诉我微信的具体情况:")
    print("   - 是否已安装微信")
    print("   - 平时如何打开微信")
    print("   - 微信的安装位置")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("下一步:")
        print("1. 我可以帮您操作微信界面")
        print("2. 自动填写登录信息（如果您提供）")
        print("3. 执行其他微信操作")
    else:
        print("\n" + "=" * 50)
        print("需要您的帮助:")
        print("请告诉我:")
        print("1. 您的Windows用户名是什么？")
        print("2. 您平时如何打开微信？")
        print("3. 微信是否已安装？")
    
    sys.exit(0 if success else 1)