param(
  [Parameter(Mandatory=$true)][string]$Phone,
  [Parameter(Mandatory=$true)][string]$Message,
  [string]$BeforePath = "C:\Users\ADMIN\AppData\Local\Temp\zalo_before_send.png",
  [string]$AfterPath  = "C:\Users\ADMIN\AppData\Local\Temp\zalo_after_send.png",
  [string]$SearchPath = "C:\Users\ADMIN\AppData\Local\Temp\zalo_after_search.png"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseOps {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  public const uint LEFTDOWN = 0x0002;
  public const uint LEFTUP = 0x0004;
}
"@

$ErrorActionPreference = 'SilentlyContinue'

function Click([int]$x,[int]$y){
  [MouseOps]::SetCursorPos($x,$y) | Out-Null
  Start-Sleep -Milliseconds 120
  [MouseOps]::mouse_event([MouseOps]::LEFTDOWN,0,0,0,[UIntPtr]::Zero)
  [MouseOps]::mouse_event([MouseOps]::LEFTUP,0,0,0,[UIntPtr]::Zero)
}

function Snap([string]$p){
  $b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size)
  $bmp.Save($p,[System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

function FocusZalo {
  $ws=New-Object -ComObject WScript.Shell
  $null=$ws.AppActivate('Zalo')
  Start-Sleep -Milliseconds 450
  return $ws
}

$ws = FocusZalo

# 1) Search by phone (strictly replace old query)
Click 178 52
Start-Sleep -Milliseconds 120
$ws.SendKeys('^a')
Start-Sleep -Milliseconds 80
$ws.SendKeys('{BACKSPACE}')
Start-Sleep -Milliseconds 80
Set-Clipboard -Value $Phone
$ws.SendKeys('^v')
Start-Sleep -Milliseconds 450

# Try open exact search result by Enter first, then fallback Down+Enter.
$ws.SendKeys('~')
Start-Sleep -Milliseconds 700
Snap $SearchPath

# Fallback select first result row if still on list state.
Click 205 138
Start-Sleep -Milliseconds 450

# 2) Focus message composer
Click 760 744
Start-Sleep -Milliseconds 120
$ws.SendKeys('^a')
Start-Sleep -Milliseconds 80
Set-Clipboard -Value $Message
Start-Sleep -Milliseconds 80
$ws.SendKeys('^v')
Start-Sleep -Milliseconds 250
Snap $BeforePath

# 3) Send by button + Enter fallback
Click 1185 744
Start-Sleep -Milliseconds 250
$ws.SendKeys('~')
Start-Sleep -Milliseconds 900
Snap $AfterPath

Write-Output "SEARCH=$SearchPath"
Write-Output "BEFORE=$BeforePath"
Write-Output "AFTER=$AfterPath"