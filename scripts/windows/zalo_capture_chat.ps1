param(
  [Parameter(Mandatory=$true)][string]$Phone,
  [string]$OutPath = "C:\Users\ADMIN\AppData\Local\Temp\zalo_chat_capture.png"
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

function Click([int]$x,[int]$y){
  [MouseOps]::SetCursorPos($x,$y) | Out-Null
  Start-Sleep -Milliseconds 110
  [MouseOps]::mouse_event([MouseOps]::LEFTDOWN,0,0,0,[UIntPtr]::Zero)
  [MouseOps]::mouse_event([MouseOps]::LEFTUP,0,0,0,[UIntPtr]::Zero)
}

$ws=New-Object -ComObject WScript.Shell
$null=$ws.AppActivate('Zalo')
Start-Sleep -Milliseconds 450

# search + open chat
Click 178 52
Start-Sleep -Milliseconds 120
$ws.SendKeys('^a')
Start-Sleep -Milliseconds 80
$ws.SendKeys('{BACKSPACE}')
Start-Sleep -Milliseconds 70
Set-Clipboard -Value $Phone
$ws.SendKeys('^v')
Start-Sleep -Milliseconds 420
$ws.SendKeys('~')
Start-Sleep -Milliseconds 450
Click 205 138
Start-Sleep -Milliseconds 650

# capture full primary screen
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size)
$bmp.Save($OutPath,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

Write-Output $OutPath