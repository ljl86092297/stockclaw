#!/usr/bin/env python3
"""
OpenClaw鼠标控制工具
通过xdotool实现鼠标和键盘控制
"""

import subprocess
import time
import sys
import json
import os

class MouseController:
    def __init__(self):
        self.display = os.environ.get('DISPLAY', ':0')
        print(f"初始化鼠标控制器 (DISPLAY={self.display})")
    
    def get_mouse_position(self):
        """获取当前鼠标位置"""
        try:
            result = subprocess.run(
                ['xdotool', 'getmouselocation'],
                capture_output=True,
                text=True,
                check=True
            )
            # 解析输出: x:123 y:456 screen:0 window:789
            parts = result.stdout.strip().split()
            pos = {}
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    pos[key] = value
            return {
                'x': int(pos.get('x', 0)),
                'y': int(pos.get('y', 0)),
                'screen': int(pos.get('screen', 0)),
                'window': pos.get('window', '0')
            }
        except Exception as e:
            print(f"获取鼠标位置失败: {e}")
            return None
    
    def move_mouse(self, x, y, relative=False, duration=0):
        """移动鼠标到指定位置"""
        try:
            cmd = ['xdotool']
            if relative:
                cmd.extend(['mousemove_relative', '--', str(x), str(y)])
            else:
                cmd.extend(['mousemove', str(x), str(y)])
            
            if duration > 0:
                # 模拟平滑移动
                current = self.get_mouse_position()
                if current:
                    steps = int(duration * 10)  # 每0.1秒一步
                    if steps > 1:
                        dx = (x - current['x']) / steps
                        dy = (y - current['y']) / steps
                        for i in range(1, steps + 1):
                            step_x = int(current['x'] + dx * i)
                            step_y = int(current['y'] + dy * i)
                            subprocess.run(['xdotool', 'mousemove', str(step_x), str(step_y)], 
                                         capture_output=True)
                            time.sleep(duration / steps)
                        return True
            
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"移动鼠标失败: {e}")
            return False
    
    def click(self, button=1, count=1):
        """点击鼠标"""
        try:
            for _ in range(count):
                subprocess.run(['xdotool', 'click', str(button)], 
                             capture_output=True, check=True)
                time.sleep(0.1)
            return True
        except Exception as e:
            print(f"点击失败: {e}")
            return False
    
    def double_click(self, button=1):
        """双击"""
        return self.click(button, 2)
    
    def right_click(self):
        """右键点击"""
        return self.click(3)
    
    def scroll(self, amount):
        """滚动鼠标滚轮"""
        try:
            # 正数向上滚动，负数向下滚动
            subprocess.run(['xdotool', 'click', '4' if amount > 0 else '5'], 
                         capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"滚动失败: {e}")
            return False
    
    def drag(self, start_x, start_y, end_x, end_y, button=1):
        """拖拽操作"""
        try:
            # 移动到起点
            self.move_mouse(start_x, start_y)
            time.sleep(0.1)
            
            # 按下鼠标
            subprocess.run(['xdotool', 'mousedown', str(button)], 
                         capture_output=True, check=True)
            time.sleep(0.1)
            
            # 移动到终点
            self.move_mouse(end_x, end_y)
            time.sleep(0.1)
            
            # 释放鼠标
            subprocess.run(['xdotool', 'mouseup', str(button)], 
                         capture_output=True, check=True)
            
            return True
        except Exception as e:
            print(f"拖拽失败: {e}")
            return False
    
    def type_text(self, text):
        """输入文本"""
        try:
            # 使用type命令输入文本
            subprocess.run(['xdotool', 'type', '--clearmodifiers', text], 
                         capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"输入文本失败: {e}")
            return False
    
    def press_key(self, key):
        """按下按键"""
        try:
            subprocess.run(['xdotool', 'key', key], 
                         capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"按键失败: {e}")
            return False
    
    def execute_command(self, command):
        """执行鼠标控制命令"""
        try:
            cmd_data = json.loads(command)
            action = cmd_data.get('action')
            
            if action == 'get_position':
                pos = self.get_mouse_position()
                return json.dumps({'success': True, 'position': pos})
            
            elif action == 'move':
                x = cmd_data.get('x', 0)
                y = cmd_data.get('y', 0)
                relative = cmd_data.get('relative', False)
                duration = cmd_data.get('duration', 0)
                success = self.move_mouse(x, y, relative, duration)
                return json.dumps({'success': success})
            
            elif action == 'click':
                button = cmd_data.get('button', 1)
                count = cmd_data.get('count', 1)
                success = self.click(button, count)
                return json.dumps({'success': success})
            
            elif action == 'type':
                text = cmd_data.get('text', '')
                success = self.type_text(text)
                return json.dumps({'success': success})
            
            elif action == 'key':
                key = cmd_data.get('key', '')
                success = self.press_key(key)
                return json.dumps({'success': success})
            
            elif action == 'drag':
                start_x = cmd_data.get('start_x', 0)
                start_y = cmd_data.get('start_y', 0)
                end_x = cmd_data.get('end_x', 0)
                end_y = cmd_data.get('end_y', 0)
                button = cmd_data.get('button', 1)
                success = self.drag(start_x, start_y, end_x, end_y, button)
                return json.dumps({'success': success})
            
            else:
                return json.dumps({'success': False, 'error': f'未知动作: {action}'})
                
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})

def main():
    """主函数：演示鼠标控制功能"""
    controller = MouseController()
    
    print("=== OpenClaw鼠标控制演示 ===")
    
    # 1. 获取当前鼠标位置
    print("\n1. 获取鼠标位置:")
    pos = controller.get_mouse_position()
    if pos:
        print(f"   当前位置: x={pos['x']}, y={pos['y']}")
    
    # 2. 移动鼠标
    print("\n2. 移动鼠标到(500, 300):")
    if controller.move_mouse(500, 300, duration=0.5):
        print("   移动成功")
    
    # 3. 点击
    print("\n3. 左键点击:")
    if controller.click():
        print("   点击成功")
    
    # 4. 输入文本
    print("\n4. 输入文本:")
    if controller.type_text("Hello from OpenClaw!"):
        print("   输入成功")
    
    # 5. 按回车键
    print("\n5. 按回车键:")
    if controller.press_key("Return"):
        print("   按键成功")
    
    # 6. 返回原位置
    print("\n6. 返回原位置:")
    if pos and controller.move_mouse(pos['x'], pos['y'], duration=0.5):
        print("   返回成功")
    
    print("\n=== 演示完成 ===")
    print("\n可用命令格式 (JSON):")
    print('  {"action": "get_position"}')
    print('  {"action": "move", "x": 100, "y": 200, "relative": false, "duration": 0.5}')
    print('  {"action": "click", "button": 1, "count": 1}')
    print('  {"action": "type", "text": "Hello"}')
    print('  {"action": "key", "key": "Return"}')
    print('  {"action": "drag", "start_x": 100, "start_y": 100, "end_x": 300, "end_y": 300}')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行模式：执行单个命令
        controller = MouseController()
        result = controller.execute_command(sys.argv[1])
        print(result)
    else:
        # 交互演示模式
        main()