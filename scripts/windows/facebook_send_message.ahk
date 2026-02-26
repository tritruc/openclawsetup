#Requires AutoHotkey v2.0

if (A_Args.Length < 2) {
    MsgBox "Usage: facebook_send_message.ahk <recipient_name> <message>"
    ExitApp 1
}

recipient := A_Args[1]
msg := A_Args[2]

chrome := "C:\Program Files\Google\Chrome\Application\chrome.exe"
Run '"' chrome '" --profile-directory="Profile 4" --new-tab "https://www.facebook.com/messages/"'

if !WinWaitActive("Facebook",, 15) {
    MsgBox "Facebook window not active"
    ExitApp 2
}

Sleep 2000
Send "{Esc}" ; dismiss popup if any
Sleep 300

; Messenger search (best effort)
Send "^k"
Sleep 700
SendText recipient
Sleep 500
Send "{Enter}"
Sleep 2200

SendText msg
Sleep 300
Send "{Enter}"

ExitApp 0
