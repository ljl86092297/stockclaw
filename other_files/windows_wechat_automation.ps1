# Windows PowerShell脚本 - 微信自动化
# 通过Windows原生环境执行

Write-Host "=== Windows微信自动化脚本 ===" -ForegroundColor Cyan
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# 检查微信进程
Write-Host "1. 检查微信进程..." -ForegroundColor Yellow
$wechatProcesses = Get-Process -Name "WeChat*" -ErrorAction SilentlyContinue

if ($wechatProcesses.Count -eq 0) {
    Write-Host "  微信未运行，尝试启动..." -ForegroundColor Red
    
    # 尝试启动微信
    $wechatPaths = @(
        "C:\Program Files\Tencent\WeChat\WeChat.exe",
        "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
        "$env:LOCALAPPDATA\Tencent\WeChat\WeChat.exe"
    )
    
    $started = $false
    foreach ($path in $wechatPaths) {
        if (Test-Path $path) {
            Write-Host "  找到微信: $path" -ForegroundColor Green
            Start-Process $path
            $started = $true
            Start-Sleep -Seconds 5
            break
        }
    }
    
    if (-not $started) {
        Write-Host "  未找到微信，尝试通过开始菜单启动..." -ForegroundColor Yellow
        Start-Process "wechat:"
        Start-Sleep -Seconds 5
    }
} else {
    Write-Host "  微信正在运行 (进程数: $($wechatProcesses.Count))" -ForegroundColor Green
}

# 激活微信窗口
Write-Host "`n2. 激活微信窗口..." -ForegroundColor Yellow

# 方法1: 使用Windows API激活窗口
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WindowHelper {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
}
"@

# 查找微信窗口
Write-Host "  查找微信窗口..." -ForegroundColor Gray
$wechatWindow = [WindowHelper]::FindWindow("WeChatMainWndForPC", "微信")

if ($wechatWindow -ne [IntPtr]::Zero) {
    Write-Host "  找到微信窗口句柄: $wechatWindow" -ForegroundColor Green
    
    # 激活窗口
    [WindowHelper]::ShowWindow($wechatWindow, 9)  # SW_RESTORE = 9
    [WindowHelper]::SetForegroundWindow($wechatWindow)
    Write-Host "  已激活微信窗口" -ForegroundColor Green
} else {
    Write-Host "  未找到微信窗口，尝试其他方法..." -ForegroundColor Yellow
    
    # 方法2: 通过进程激活
    $wechatProcess = Get-Process -Name "WeChatAppEx" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($wechatProcess) {
        Write-Host "  通过进程激活..." -ForegroundColor Gray
        $wshell = New-Object -ComObject WScript.Shell
        $wshell.AppActivate($wechatProcess.MainWindowTitle)
        Write-Host "  已尝试激活" -ForegroundColor Green
    }
}

Start-Sleep -Seconds 2

# 发送测试消息
Write-Host "`n3. 发送测试消息..." -ForegroundColor Yellow

# 模拟按键操作
Write-Host "  模拟按键: Ctrl+F (搜索)" -ForegroundColor Gray
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("^f")  # Ctrl+F
Start-Sleep -Seconds 1

Write-Host "  输入: 宝宝/:heart十月初一" -ForegroundColor Gray
[System.Windows.Forms.SendKeys]::SendWait("宝宝/:heart十月初一")
Start-Sleep -Seconds 2

Write-Host "  按回车选择" -ForegroundColor Gray
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 1

Write-Host "  输入测试消息" -ForegroundColor Gray
[System.Windows.Forms.SendKeys]::SendWait("[Windows自动化测试]这是通过PowerShell发送的消息")
Start-Sleep -Seconds 1

Write-Host "  按回车发送" -ForegroundColor Gray
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 1

Write-Host "`n=== 操作完成 ===" -ForegroundColor Cyan
Write-Host "请检查微信:"
Write-Host "1. 微信窗口是否已激活？"
Write-Host "2. 是否发送了测试消息？"
Write-Host "3. 消息内容: [Windows自动化测试]这是通过PowerShell发送的消息"
Write-Host ""
Write-Host "如果成功，回复'Windows方法成功'"
Write-Host "如果失败，描述看到的现象"