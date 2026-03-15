#!/usr/bin/env python3
"""
打开微信的自动化脚本
通过鼠标和键盘操作打开微信应用程序
"""

import subprocess
import time
import os

class WeChatOpener:
    def __init__(self):
        self.display = os.environ.get('DISPLAY', ':0')
        print(f"微信打开助手 (DISPLAY={self.display})")
    
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
            print(f"鼠标命令执行失败: {e}")
            return None
    
    def get_screen_info(self):
        """获取屏幕信息"""
        try:
            # 尝试使用xrandr获取屏幕分辨率
            result = subprocess.run(
                ['xrandr', '--current'],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.split('\n')
            for line in lines:
                if '*' in line:  # 当前分辨率
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and '+' in part:
                            res, _ = part.split('+', 1)
                            width, height = map(int, res.split('x'))
                            return {'width': width, 'height': height}
        except:
            pass
        
        # 默认值
        return {'width': 1920, 'height': 1080}
    
    def open_application_menu(self):
        """打开应用程序菜单（假设是Ubuntu/GNOME）"""
        print("1. 打开应用程序菜单...")
        
        # 方法1：按Super键（Windows键）打开菜单
        self.execute_mouse_command('{"action": "key", "key": "Super"}')
        time.sleep(1)
        
        # 方法2：或者点击左下角（假设是GNOME）
        screen = self.get_screen_info()
        if screen['width'] > 0:
            # 点击左下角区域
            self.execute_mouse_command(f'{{"action": "move", "x": 50, "y": {screen["height"]-50}}}')
            time.sleep(0.5)
            self.execute_mouse_command('{"action": "click"}')
            time.sleep(1)
        
        return True
    
    def search_wechat(self):
        """搜索微信"""
        print("2. 搜索微信...")
        
        # 输入"wechat"进行搜索
        self.execute_mouse_command('{"action": "type", "text": "wechat"}')
        time.sleep(1)
        
        # 如果没找到，尝试中文
        self.execute_mouse_command('{"action": "type", "text": "微信"}')
        time.sleep(2)
        
        return True
    
    def click_wechat_icon(self):
        """点击微信图标"""
        print("3. 点击微信图标...")
        
        # 假设微信图标在搜索结果的第一项
        # 移动到大概位置并点击
        screen = self.get_screen_info()
        
        # 搜索结果的典型位置（中间偏上）
        click_x = screen['width'] // 2
        click_y = screen['height'] // 3
        
        self.execute_mouse_command(f'{{"action": "move", "x": {click_x}, "y": {click_y}}}')
        time.sleep(0.5)
        self.execute_mouse_command('{"action": "click"}')
        time.sleep(2)
        
        # 如果没点到，尝试双击
        self.execute_mouse_command('{"action": "click", "count": 2}')
        time.sleep(2)
        
        return True
    
    def check_if_wechat_is_running(self):
        """检查微信是否在运行"""
        print("4. 检查微信是否已打开...")
        
        try:
            # 检查进程
            result = subprocess.run(
                ['pgrep', '-f', 'wechat'],
                capture_output=True,
                text=True
            )
            
            result_cn = subprocess.run(
                ['pgrep', '-f', '微信'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 or result_cn.returncode == 0:
                print("   ✓ 微信正在运行")
                return True
            else:
                print("   ✗ 微信未运行")
                return False
                
        except Exception as e:
            print(f"   检查失败: {e}")
            return False
    
    def alternative_methods(self):
        """备用方法：尝试其他打开方式"""
        print("5. 尝试备用方法...")
        
        # 方法1：尝试通过终端打开
        print("   方法1: 通过终端打开")
        try:
            subprocess.run(['which', 'wechat'], capture_output=True)
            subprocess.Popen(['wechat'], start_new_session=True)
            time.sleep(3)
            return True
        except:
            pass
        
        # 方法2：尝试常见的安装位置
        print("   方法2: 查找常见位置")
        common_paths = [
            '/usr/bin/wechat',
            '/usr/local/bin/wechat',
            '/opt/wechat/wechat',
            os.path.expanduser('~/.local/bin/wechat'),
            '/Applications/WeChat.app/Contents/MacOS/WeChat',  # macOS
            'C:\\Program Files\\Tencent\\WeChat\\WeChat.exe'   # Windows (WSL需要特殊处理)
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"   找到微信: {path}")
                try:
                    subprocess.Popen([path], start_new_session=True)
                    time.sleep(3)
                    return True
                except:
                    continue
        
        # 方法3：使用xdg-open（Linux桌面环境）
        print("   方法3: 使用xdg-open")
        try:
            subprocess.Popen(['xdg-open', 'wechat://'], start_new_session=True)
            time.sleep(3)
            return True
        except:
            pass
        
        return False
    
    def run(self):
        """主执行流程"""
        print("开始尝试打开微信...")
        
        # 首先检查是否已经在运行
        if self.check_if_wechat_is_running():
            print("\n✓ 微信已经在运行中！")
            return True
        
        print("\n微信未运行，开始打开流程...")
        
        # 记录开始时间
        start_time = time.time()
        
        # 尝试主要方法：通过应用程序菜单
        try:
            self.open_application_menu()
            self.search_wechat()
            self.click_wechat_icon()
            time.sleep(3)  # 等待应用启动
        except Exception as e:
            print(f"主要方法失败: {e}")
        
        # 检查是否成功
        if self.check_if_wechat_is_running():
            print(f"\n✓ 成功打开微信！ (耗时: {time.time()-start_time:.1f}秒)")
            return True
        
        # 如果主要方法失败，尝试备用方法
        print("\n主要方法失败，尝试备用方法...")
        if self.alternative_methods():
            time.sleep(3)
            if self.check_if_wechat_is_running():
                print(f"\n✓ 通过备用方法成功打开微信！ (耗时: {time.time()-start_time:.1f}秒)")
                return True
        
        # 所有方法都失败
        print(f"\n✗ 无法打开微信 (耗时: {time.time()-start_time:.1f}秒)")
        print("\n建议:")
        print("1. 请确保微信已安装在系统中")
        print("2. 您可以手动打开微信，然后我可以帮您进行其他操作")
        print("3. 或者告诉我微信的具体位置，我可以直接打开它")
        
        return False

def main():
    """主函数"""
    opener = WeChatOpener()
    success = opener.run()
    
    if success:
        print("\n接下来我可以帮您:")
        print("1. 操作微信界面")
        print("2. 发送消息")
        print("3. 其他自动化任务")
    else:
        print("\n请提供更多信息:")
        print("1. 您的操作系统类型 (Ubuntu/Fedora/macOS/Windows)")
        print("2. 微信的安装位置")
        print("3. 或者手动打开微信后告诉我")

if __name__ == "__main__":
    main()