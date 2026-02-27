$ErrorActionPreference = 'Stop'
$uvExe = 'C:\Program Files (x86)\UltraViewer\UltraViewer_Desktop.exe'
if (!(Test-Path $uvExe)) { throw "UltraViewer exe not found: $uvExe" }

# 1) Auto-start via HKCU Run
New-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Force | Out-Null
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'UltraViewer' -Value ('"' + $uvExe + '"')

# 2) Startup folder shortcut (redundant)
$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup 'UltraViewer.lnk'
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = $uvExe
$s.WorkingDirectory = 'C:\Program Files (x86)\UltraViewer'
$s.Save()

# 3) Watchdog script + scheduled task
$taskName = 'UltraViewerWatchdog'
$scriptPath = Join-Path $env:APPDATA 'UltraViewer\watchdog-ultraviewer.ps1'
@"
$uvExe = 'C:\Program Files (x86)\UltraViewer\UltraViewer_Desktop.exe'
if (-not (Get-Process -Name 'UltraViewer_Desktop' -ErrorAction SilentlyContinue)) {
  Start-Process -FilePath $uvExe -WindowStyle Minimized
}
"@ | Set-Content -Path $scriptPath -Encoding UTF8

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $scriptPath + '"')
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn
$triggerOnce = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
$triggerOnce.Repetition.Interval = 'PT2M'
$triggerOnce.Repetition.Duration = 'P1D'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($triggerLogon, $triggerOnce) -Settings $settings -Description 'Restart UltraViewer automatically if not running' -Force | Out-Null

# 4) Keep awake on AC
powercfg /change standby-timeout-ac 0 | Out-Null
powercfg /change hibernate-timeout-ac 0 | Out-Null

# 5) Start now if not running
if (-not (Get-Process -Name 'UltraViewer_Desktop' -ErrorAction SilentlyContinue)) {
  Start-Process -FilePath $uvExe
}

Write-Output 'OK_AUTOSTART_WATCHDOG_CONFIGURED'
