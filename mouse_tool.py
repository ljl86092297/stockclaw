#!/usr/bin/env python3
"""
OpenClaw鼠标控制工具 - 集成到OpenClaw系统
"""

import subprocess
import json
import os
import sys

def execute_mouse_command(command_json):
    """执行鼠标控制命令"""
    try:
        # 直接调用我们的鼠标控制脚本
        result = subprocess.run(
            ['python3', 'openclaw_mouse_control.py', command_json],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return json.dumps({'success': False, 'error': e.stderr})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})

def main():
    """主函数：处理OpenClaw工具调用"""
    if len(sys.argv) != 2:
        print("Usage: python3 mouse_tool.py <command_json>")
        sys.exit(1)
    
    command_json = sys.argv[1]
    result = execute_mouse_command(command_json)
    print(result)

if __name__ == "__main__":
    main()