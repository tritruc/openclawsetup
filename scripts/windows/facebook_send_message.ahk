#Requires AutoHotkey v2.0

if (A_Args.Length < 2) {
    MsgBox "Usage: facebook_send_message.ahk <recipient_name> <message>"
    ExitApp 1
}

recipient := A_Args[1]
msg := A_Args[2]

CoordMode "Mouse", "Screen"

chrome := "C:\Program Files\Google\Chrome\Application\chrome.exe"
Run '"' chrome '" --profile-directory="Profile 4" --new-tab "https://www.facebook.com/messages/"'

if !WinWaitActive("Facebook",, 20) {
    MsgBox "Facebook window not active"
    ExitApp 2
}

WinMaximize "A"
Sleep 3000

; Close PIN recovery modal / popups if present
Loop 3 {
    Send "{Esc}"
    Sleep 350
}

; Focus Messenger search box (left panel)
Click 210, 235
Sleep 400
Send "^a"
Sleep 100
Send "{Backspace}"
Sleep 100
SendText recipient
Sleep 1000
Send "{Enter}"
Sleep 2200

; Open first matched conversation if needed
Send "{Enter}"
Sleep 1200

; Focus message composer and send
Click 620, 835
Sleep 350
SendText msg
Sleep 200
Send "{Enter}"

ExitApp 0
