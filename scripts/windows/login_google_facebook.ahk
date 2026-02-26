#Requires AutoHotkey v2.0

if (A_Args.Length < 4) {
    MsgBox "Usage: login_google_facebook.ahk <gmail_email> <gmail_password> <facebook_user> <facebook_password>"
    ExitApp 1
}

gEmail := A_Args[1]
gPass := A_Args[2]
fbUser := A_Args[3]
fbPass := A_Args[4]

chrome := "C:\Program Files\Google\Chrome\Application\chrome.exe"

; ---------- Google (Gmail) ----------
Run '"' chrome '" --profile-directory="Profile 4" --new-window "https://accounts.google.com/ServiceLogin?service=mail"'
if !WinWaitActive("Google",, 20) {
    WinWaitActive("Chrome",, 20)
}
Sleep 3500
Send "{Esc}"
Sleep 300
Send "^l"
Sleep 200
SendText "https://accounts.google.com/ServiceLogin?service=mail"
Send "{Enter}"
Sleep 5000
SendText gEmail
Send "{Enter}"
Sleep 4500
SendText gPass
Send "{Enter}"
Sleep 7000

; ---------- Facebook ----------
Run '"' chrome '" --profile-directory="Profile 4" --new-window "https://www.facebook.com/login"'
if !WinWaitActive("Facebook",, 20) {
    WinWaitActive("Chrome",, 20)
}
Sleep 4500
Send "{Esc}"
Sleep 300
Send "^l"
Sleep 200
SendText "https://www.facebook.com/login"
Send "{Enter}"
Sleep 5000
SendText fbUser
Send "{Tab}"
Sleep 200
SendText fbPass
Send "{Enter}"

ExitApp 0
