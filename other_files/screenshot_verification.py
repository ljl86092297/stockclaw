#!/usr/bin/env python3
"""
屏幕截图验证系统
通过截图对比验证操作效果
"""

import subprocess
import time
import os
import hashlib

class ScreenshotVerification:
    def __init__(self):
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        print(f"截图验证系统启动 (保存目录: {self.screenshot_dir})")
    
    def take_screenshot(self, name):
        """截取屏幕截图"""
        timestamp = time.strftime("%H%M%S")
        filename = f"{self.screenshot_dir}/{name}_{timestamp}.png"
        
        print(f"  截取截图: {filename}")
        
        # 尝试多种截图方法
        methods = [
            # 方法1: scrot (Linux)
            ["scrot", filename],
            # 方法2: import (ImageMagick)
            ["import", "-window", "root", filename],
            # 方法3: gnome-screenshot
            ["gnome-screenshot", "-f", filename],
        ]
        
        for method in methods:
            try:
                result = subprocess.run(
                    method,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    print(f"    ✓ 截图成功 ({method[0]}, {file_size}字节)")
                    return filename
            except:
                continue
        
        print("    ✗ 所有截图方法都失败")
        return None
    
    def compare_screenshots(self, before, after, operation):
        """比较两张截图"""
        if not before or not after:
            print("    ⚠️ 缺少截图，无法比较")
            return False
        
        print(f"  比较截图: {operation}")
        
        # 方法1: 文件大小比较
        size_before = os.path.getsize(before)
        size_after = os.path.getsize(after)
        print(f"    文件大小: 前={size_before}字节, 后={size_after}字节")
        
        # 方法2: 文件哈希比较
        hash_before = self.file_hash(before)
        hash_after = self.file_hash(after)
        print(f"    文件哈希: 前={hash_before[:16]}..., 后={hash_after[:16]}...")
        
        if hash_before == hash_after:
            print("    ⚠️ 截图完全相同，可能操作无效")
            return False
        else:
            print("    ✓ 截图有变化，操作可能有效")
            return True
    
    def file_hash(self, filename):
        """计算文件哈希"""
        try:
            with open(filename, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return "error"
    
    def verify_wechat_operation(self, operation_name, command_json):
        """验证微信操作"""
        print(f"\n=== 验证操作: {operation_name} ===")
        
        # 1. 操作前截图
        print("1. 操作前截图")
        before_screenshot = self.take_screenshot(f"before_{operation_name}")
        
        # 2. 执行操作
        print("2. 执行操作")
        time.sleep(1)
        self.execute_command(command_json)
        time.sleep(2)  # 等待界面响应
        
        # 3. 操作后截图
        print("3. 操作后截图")
        after_screenshot = self.take_screenshot(f"after_{operation_name}")
        
        # 4. 比较截图
        print("4. 比较截图变化")
        has_changes = self.compare_screenshots(before_screenshot, after_screenshot, operation_name)
        
        # 5. 分析结果
        if has_changes:
            print(f"  ✅ {operation_name} 可能有效（界面有变化）")
            return True
        else:
            print(f"  ⚠️ {operation_name} 可能无效（界面无变化）")
            return False
    
    def execute_command(self, command_json):
        """执行命令"""
        try:
            result = subprocess.run(
                ['python3', 'openclaw_mouse_control.py', command_json],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def test_wechat_shortcuts(self):
        """系统测试微信快捷键"""
        print("\n=== 系统测试微信快捷键 ===")
        
        # 微信可能使用的快捷键组合
        shortcuts = [
            ("Ctrl+F", "搜索", '{"action": "key", "key": "Control_L+f"}'),
            ("Ctrl+N", "新建聊天", '{"action": "key", "key": "Control_L+n"}'),
            ("Ctrl+W", "关闭窗口", '{"action": "key", "key": "Control_L+w"}'),
            ("Alt+S", "发送消息", '{"action": "key", "key": "Alt_L+s"}'),
            ("Alt+C", "联系人", '{"action": "key", "key": "Alt_L+c"}'),
            ("Alt+F", "文件", '{"action": "key", "key": "Alt_L+f"}'),
            ("F5", "刷新", '{"action": "key", "key": "F5"}'),
            ("Esc", "取消/返回", '{"action": "key", "key": "Escape"}'),
        ]
        
        results = []
        for name, description, command in shortcuts:
            print(f"\n测试: {name} ({description})")
            success = self.verify_wechat_operation(f"shortcut_{name}", command)
            results.append((name, description, success))
            time.sleep(2)
        
        # 分析结果
        print("\n=== 快捷键测试结果 ===")
        effective_shortcuts = []
        for name, description, success in results:
            status = "✅ 有效" if success else "❌ 无效"
            print(f"{name} ({description}): {status}")
            if success:
                effective_shortcuts.append((name, description))
        
        print(f"\n发现的有效快捷键: {len(effective_shortcuts)}/{len(shortcuts)}")
        for name, description in effective_shortcuts:
            print(f"  • {name}: {description}")
        
        return effective_shortcuts

def main():
    """主函数"""
    print("屏幕截图验证系统")
    print("=" * 60)
    
    verifier = ScreenshotVerification()
    
    # 测试当前屏幕状态
    print("\n1. 测试当前屏幕状态")
    test_screenshot = verifier.take_screenshot("initial_test")
    if test_screenshot:
        print(f"  初始截图: {test_screenshot}")
    else:
        print("  ⚠️ 无法截图，系统可能不支持")
        print("  需要安装截图工具: sudo apt install scrot 或 imagemagick")
        return
    
    # 系统测试微信快捷键
    effective_shortcuts = verifier.test_wechat_shortcuts()
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 验证系统总结:")
    
    if effective_shortcuts:
        print("✅ 发现有效快捷键，可以继续操作")
        print("推荐使用:")
        for name, description in effective_shortcuts[:3]:
            print(f"  {name}: {description}")
    else:
        print("❌ 未发现有效快捷键")
        print("可能需要:")
        print("1. 手动操作微信界面")
        print("2. 使用图像识别定位元素")
        print("3. 学习微信界面布局")
    
    print("\n💡 下一步:")
    print("1. 使用有效的快捷键操作微信")
    print("2. 通过截图验证每个步骤")
    print("3. 建立完整的操作流程")

if __name__ == "__main__":
    main()