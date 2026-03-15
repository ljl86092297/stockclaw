#!/usr/bin/env python3
"""
微信操作助手 - 基础功能
"""

import subprocess
import time
import os

class WeChatOperator:
    def __init__(self):
        self.display = os.environ.get('DISPLAY', ':0')
        print(f"微信操作助手 (DISPLAY={self.display})")
    
    def execute_mouse_command(self, command_json):
        """执行鼠标命令"""
        try:
            result = subprocess.run(
                ['python3', 'openclaw_mouse_control.py', command_json],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"命令执行失败: {e}")
            return None
    
    def get_screen_info(self):
        """获取屏幕信息"""
        try:
            result = subprocess.run(
                ['xrandr', '--current'],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.split('\n')
            for line in lines:
                if '*' in line:
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and '+' in part:
                            res, _ = part.split('+', 1)
                            width, height = map(int, res.split('x'))
                            return {'width': width, 'height': height}
        except:
            pass
        return {'width': 1920, 'height': 1080}
    
    def focus_wechat_window(self):
        """聚焦微信窗口"""
        print("聚焦微信窗口...")
        
        # 尝试通过wmctrl找到微信窗口
        try:
            # 查找包含"WeChat"或"微信"的窗口
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'WeChat' in line or '微信' in line:
                    window_id = line.split()[0]
                    # 激活窗口
                    subprocess.run(['wmctrl', '-i', '-a', window_id])
                    print(f"  找到微信窗口: {window_id}")
                    time.sleep(1)
                    return True
        except:
            pass
        
        # 备用方法：按Alt+Tab切换到微信
        print("  使用Alt+Tab切换...")
        self.execute_mouse_command('{"action": "key", "key": "Alt_L+Tab"}')
        time.sleep(1)
        self.execute_mouse_command('{"action": "key", "key": "Tab"}')
        time.sleep(1)
        self.execute_mouse_command('{"action": "key", "key": "Return"}')
        time.sleep(1)
        
        return True
    
    def send_message_to_contact(self, contact_name, message):
        """给指定联系人发送消息"""
        print(f"准备给 {contact_name} 发送消息...")
        
        # 1. 聚焦微信
        self.focus_wechat_window()
        time.sleep(1)
        
        # 2. 打开搜索框 (Ctrl+F)
        print("  打开搜索框...")
        self.execute_mouse_command('{"action": "key", "key": "Control_L+f"}')
        time.sleep(1)
        
        # 3. 输入联系人名称
        print(f"  搜索联系人: {contact_name}")
        self.execute_mouse_command(f'{{"action": "type", "text": "{contact_name}"}}')
        time.sleep(2)
        
        # 4. 按回车选择第一个结果
        print("  选择联系人...")
        self.execute_mouse_command('{"action": "key", "key": "Return"}')
        time.sleep(1)
        
        # 5. 输入消息
        print(f"  输入消息: {message}")
        self.execute_mouse_command(f'{{"action": "type", "text": "{message}"}}')
        time.sleep(1)
        
        # 6. 发送消息 (Ctrl+Enter或回车)
        print("  发送消息...")
        self.execute_mouse_command('{"action": "key", "key": "Control_L+Return"}')
        time.sleep(0.5)
        
        # 备用：普通回车
        self.execute_mouse_command('{"action": "key", "key": "Return"}')
        
        print(f"✓ 消息已发送给 {contact_name}")
        return True
    
    def take_screenshot(self, filename="wechat_screenshot.png"):
        """截取屏幕截图"""
        print(f"截取屏幕截图: {filename}")
        
        try:
            # 使用scrot截屏
            subprocess.run(['scrot', filename], check=True)
            print(f"  截图已保存: {filename}")
            return True
        except:
            try:
                # 使用import命令（ImageMagick）
                subprocess.run(['import', '-window', 'root', filename], check=True)
                print(f"  截图已保存: {filename}")
                return True
            except:
                print("  截图失败，请安装scrot或imagemagick")
                return False
    
    def demonstrate_basic_operations(self):
        """演示基本操作"""
        print("\n=== 微信基本操作演示 ===")
        
        # 获取屏幕信息
        screen = self.get_screen_info()
        print(f"屏幕分辨率: {screen['width']}x{screen['height']}")
        
        # 聚焦微信
        self.focus_wechat_window()
        
        # 演示点击不同区域
        print("\n1. 点击左侧联系人列表区域")
        left_x = screen['width'] // 6
        left_y = screen['height'] // 2
        self.execute_mouse_command(f'{{"action": "move", "x": {left_x}, "y": {left_y}}}')
        self.execute_mouse_command('{"action": "click"}')
        time.sleep(1)
        
        print("2. 点击中间聊天区域")
        middle_x = screen['width'] // 2
        middle_y = screen['height'] // 2
        self.execute_mouse_command(f'{{"action": "move", "x": {middle_x}, "y": {middle_y}}}')
        self.execute_mouse_command('{"action": "click"}')
        time.sleep(1)
        
        print("3. 点击底部输入框区域")
        bottom_x = screen['width'] // 2
        bottom_y = screen['height'] - 100
        self.execute_mouse_command(f'{{"action": "move", "x": {bottom_x}, "y": {bottom_y}}}')
        self.execute_mouse_command('{"action": "click"}')
        time.sleep(1)
        
        print("4. 输入测试文本")
        self.execute_mouse_command('{"action": "type", "text": "这是OpenClaw的测试消息"}')
        time.sleep(1)
        
        print("5. 清空输入（按退格键）")
        for _ in range(20):
            self.execute_mouse_command('{"action": "key", "key": "BackSpace"}')
            time.sleep(0.05)
        
        print("\n✓ 基本操作演示完成")
        return True

def main():
    """主函数"""
    operator = WeChatOperator()
    
    print("微信操作助手已启动")
    print("\n可用功能:")
    print("1. 聚焦微信窗口")
    print("2. 发送消息给联系人")
    print("3. 截取屏幕截图")
    print("4. 演示基本操作")
    
    # 演示基本操作
    operator.demonstrate_basic_operations()
    
    print("\n请告诉我您希望完成什么具体操作:")
    print("- 发送消息给 [联系人名称]")
    print("- 查看聊天记录")
    print("- 发送文件")
    print("- 其他操作")

if __name__ == "__main__":
    main()