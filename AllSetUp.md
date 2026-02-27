# AllSetUp.md — Full OpenClaw Setup + System Change Ledger

> Canonical reproducible guide. Any agent can use this file to rebuild this environment and behavior.
> Language priority: Vietnamese. Safety-first. Elderly-friendly responses.

---

## 0) Principles (must follow)

1. Every system-affecting change must be appended to this file.
2. After each such change: **commit immediately** and **push immediately**.
3. Never store raw secrets in git. Use placeholders + secret sources.
4. Keep this file runnable by another agent on a fresh machine.

---

## 1) Target behavior of this assistant

- Assistant name: **Linh**
- Role: **Trợ lý AI cho gia đình**
- Tone: **lịch sự, rõ ràng, ưu tiên an toàn**
- Language: **Tiếng Việt**
- Signature emoji: **🌿**
- Pronoun: assistant xưng **"em"**, gọi user là **"Boss"**
- Accessibility: ưu tiên người lớn tuổi mờ mắt (câu ngắn, rõ, từng bước, dễ đọc)

---

## 2) Environment snapshot (current machine)

- Host: `DESKTOP-4BJR7KN` (WSL2 Linux)
- Kernel: `6.6.87.2-microsoft-standard-WSL2`
- Node: `v25.6.1`
- OpenClaw version: `2026.2.25`
- OpenClaw CLI path: `/home/manduong/.nvm/versions/node/v24.13.1/bin/openclaw`
- Workspace: `/home/manduong/.openclaw/workspace`

Tool availability confirmed:
- `whisper`: `/home/linuxbrew/.linuxbrew/bin/whisper`
- `gemini`: `/home/linuxbrew/.linuxbrew/bin/gemini`
- `gh`: `/home/linuxbrew/.linuxbrew/bin/gh`

---

## 3) Fresh machine bootstrap (reproducible)

## 3.1 Prerequisites

Install these first:
- Node.js (>= 22, recommended latest LTS/current)
- Git
- GitHub CLI (`gh`)
- Whisper CLI (`whisper`) for local voice transcription

Example (Linuxbrew/Homebrew style):

```bash
brew install gh openai-whisper
```

## 3.2 Install OpenClaw CLI

Use one of:

```bash
npm i -g openclaw@latest
# or
pnpm add -g openclaw@latest
```

Verify:

```bash
openclaw --version
openclaw --help
```

## 3.3 Initialize/OpenClaw onboarding

```bash
openclaw onboard
# or
openclaw configure
```

Set workspace to your repo folder.

## 3.4 Configure Telegram channel (without exposing secret)

Required settings:
- `channels.telegram.enabled: true`
- `channels.telegram.dmPolicy: pairing`
- `channels.telegram.botToken: <FROM_SECRET_STORE>`

Streaming preview for easier monitoring:

```bash
openclaw config set channels.telegram.streaming partial
```

## 3.5 Enable Vietnamese voice-note transcription (local Whisper)

```bash
openclaw config set tools.media.audio '{
  enabled: true,
  maxBytes: 26214400,
  models: [
    {
      type: "cli",
      command: "whisper",
      args: ["--model", "base", "--language", "Vietnamese", "{{MediaPath}}"],
      timeoutSeconds: 120
    }
  ]
}'
```

## 3.6 Restart and verify

```bash
openclaw gateway restart
openclaw status --deep
```

Expected:
- Gateway reachable
- Telegram channel = `ON / OK`

## 3.7 Pair Telegram user

1. User DM bot with `/start`
2. User receives pairing code
3. Owner approves:

```bash
openclaw pairing approve telegram <PAIRING_CODE>
```

## 3.8 Enable local desktop actions from chat (WSL -> Windows host)

Create helper scripts in workspace:

- `scripts/open_url.sh`
- `scripts/open_youtube_search.sh`
- `scripts/open_chrome_profile_url.sh`
- `scripts/open_gmail.sh`
- `scripts/open_facebook.sh`

Make executable:

```bash
chmod +x scripts/open_url.sh scripts/open_youtube_search.sh scripts/open_chrome_profile_url.sh scripts/open_gmail.sh scripts/open_facebook.sh
```

Usage examples:

```bash
scripts/open_url.sh "https://www.youtube.com"
scripts/open_youtube_search.sh "karaoke con bướm xinh"
scripts/open_chrome_profile_url.sh "https://mail.google.com" "AutomatedAccount"
scripts/open_gmail.sh
scripts/open_facebook.sh
```

Account/profile binding:

- Chrome profile for owner account: `AutomatedAccount` (directory: `Profile 4`)
- Account email in profile: `manduongne3@gmail.com`
- Rule: Gmail/Facebook actions default to `AutomatedAccount` unless owner overrides.

Execution policy:

- Prefer end-to-end execution (do task directly), avoid tutorial-style responses.
- For Facebook actions requiring UI clicks (search person, send message), use Chrome Relay automation.
- If Chrome Relay is not attached, request one-time attachment (click OpenClaw Browser Relay icon on the active tab), then continue task automatically.

Implementation opens Windows apps through:

- `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- `Start-Process` for URL/Chrome profile launch

## 3.9 Auto-start OpenClaw on Windows login (WSL host)

Template file in repo:

- `scripts/OpenClaw-Autostart.bat`

Copy template to Windows Startup folder:

```bash
cp scripts/OpenClaw-Autostart.bat "/mnt/c/Users/ADMIN/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/OpenClaw-Autostart.bat"
```

This ensures OpenClaw gateway starts automatically when Windows user logs in.

## 3.10 Task asset hierarchy + execution skill

Use this hierarchy for all operation assets:

```text
ops/
  platforms/
    <platform>/
      <function>/
        <task-file>
```

Current examples:

- `ops/platforms/facebook/messaging/send-message.md`
- `ops/platforms/gmail/actions/open-gmail.md`
- `ops/platforms/youtube/search/open-youtube-search.md`

Custom workspace skill for execution-first behavior:

- `skills/family-exec/SKILL.md`
- `skills/family-exec/references/facebook-messaging-playbook.md`

---

## 4) GitHub sync setup (mandatory for this workflow)

## 4.1 Git identity

```bash
git config --global user.name "tritruc"
git config --global user.email "vudinhcmm.py@gmail.com"
```

## 4.2 Repo remote + auth

```bash
git remote add origin <GITHUB_REPO_URL>
gh auth login
git push -u origin master
```

If `master` is not your default branch, replace with `main` (or your branch).

---

## 5) Operational rules for future agents

When doing ANY system-affecting action:
1. Execute change.
2. Append this file (section 6 Change Ledger).
3. Commit immediately.
4. Push immediately.
5. If push fails, report exact error + exact fix commands.

Commit message format:

```text
setup: <what changed>
```

Ledger entry template:

```markdown
### <UTC timestamp> — <title>
- Why:
- Commands:
  - `...`
- Files/paths touched:
- Capability impact:
- Verification:
- Rollback:
- GitHub push status:
```

---

## 6) Change Ledger (chronological)

### 2026-02-26 11:24 UTC — Bootstrap identity + user preferences
- Why: establish assistant personality and user preferences.
- Commands:
  - file edits in `IDENTITY.md`, `USER.md`, `memory/2026-02-26.md`
- Files/paths touched:
  - `IDENTITY.md`, `USER.md`, `memory/2026-02-26.md`
- Capability impact:
  - assistant now aligned to Vietnamese, safety-first family support style.
- Verification:
  - files contain Linh/Boss/em/🌿 settings.
- Rollback:
  - revert commit.
- GitHub push status:
  - Not pushed (remote missing at that time).

### 2026-02-26 11:24 UTC — Configure global git identity
- Why: fix commit failure (`Author identity unknown`).
- Commands:
  - `git config --global user.name "tritruc"`
  - `git config --global user.email "vudinhcmm.py@gmail.com"`
- Files/paths touched:
  - global git config (`~/.gitconfig`)
- Capability impact:
  - commits now work.
- Verification:
  - `git config --global --get user.name/email`
- Rollback:
  - unset both keys.
- GitHub push status:
  - Local only.

### 2026-02-26 11:57 UTC — Approve Telegram pairing
- Why: allow owner DM access to bot.
- Commands:
  - `openclaw pairing approve telegram CCDW24CJ`
- Files/paths touched:
  - OpenClaw pairing state (internal)
- Capability impact:
  - Telegram user `6542038310` authorized.
- Verification:
  - `openclaw status --deep` + DM test.
- Rollback:
  - revoke pairing / tighten dmPolicy.
- GitHub push status:
  - N/A (runtime state).

### 2026-02-26 11:59 UTC — Enable Telegram streaming preview
- Why: user wants streaming-like progress while assistant is answering.
- Commands:
  - `openclaw config set channels.telegram.streaming partial`
  - `openclaw gateway restart`
- Files/paths touched:
  - `~/.openclaw/openclaw.json`
- Capability impact:
  - Telegram replies now show live preview updates.
- Verification:
  - `openclaw config get channels.telegram.streaming` => `partial`
- Rollback:
  - set `channels.telegram.streaming` to `off` and restart.
- GitHub push status:
  - Local only.

### 2026-02-26 12:09 UTC — Enable Vietnamese voice-note transcription via Whisper
- Why: process voice commands and act on spoken requests.
- Commands:
  - configured `tools.media.audio` with Whisper CLI model `base`, `--language Vietnamese`
  - `openclaw gateway restart`
- Files/paths touched:
  - `~/.openclaw/openclaw.json`
- Capability impact:
  - inbound Telegram voice/audio can be transcribed then interpreted.
- Verification:
  - `openclaw config get tools.media.audio`
  - send a Telegram voice note and confirm transcript-based response.
- Rollback:
  - `openclaw config unset tools.media.audio` (or set `enabled=false`) + restart.
- GitHub push status:
  - Local only.

### 2026-02-26 12:10 UTC — Add system-change documentation policy
- Why: enforce reproducible setup history.
- Commands:
  - edit `AGENTS.md`
  - create/update setup docs (`CongCu.md`)
- Files/paths touched:
  - `AGENTS.md`, `CongCu.md`, `USER.md`, `memory/2026-02-26.md`
- Capability impact:
  - workflow now requires documentation and GitHub sync after system changes.
- Verification:
  - policy text present in `AGENTS.md`.
- Rollback:
  - revert commit.
- GitHub push status:
  - local commit created; push failed (no remote configured).

### 2026-02-26 12:15 UTC — Promote `AllSetUp.md` as canonical setup ledger
- Why: user requested one universal file any agent can follow end-to-end.
- Commands:
  - create `AllSetUp.md`
  - update `AGENTS.md` rule to require `AllSetUp.md`
- Files/paths touched:
  - `AllSetUp.md`, `AGENTS.md`, `memory/2026-02-26.md`
- Capability impact:
  - standardized, portable setup guide for future agents.
- Verification:
  - this file exists and includes full bootstrap + ledger.
- Rollback:
  - revert commit.
- GitHub push status:
  - FAILED: `fatal: No configured push destination.`
  - Fix required:
    1. `git remote add origin <GITHUB_REPO_URL>`
    2. `gh auth login`
    3. `git push -u origin master`

### 2026-02-26 12:22 UTC — Connect repository to GitHub + publish branch
- Why: user provided GitHub repository URL for immediate sync workflow.
- Commands:
  - `git remote add origin https://github.com/tritruc/openclawsetup.git`
  - `git branch -M main`
  - `git push -u origin main`
- Files/paths touched:
  - local git metadata (`.git/config`, branch refs)
- Capability impact:
  - enables immediate commit+push automation for future setup/config changes.
- Verification:
  - `git remote -v`
  - `git branch --show-current` -> `main`
  - `git push -u origin main` succeeds.
- Rollback:
  - `git remote remove origin`
  - rename branch back if needed: `git branch -M master`
- GitHub push status:
  - FAILED: `fatal: could not read Username for 'https://github.com': No such device or address`
  - Fix required:
    1. `gh auth login` (HTTPS, GitHub.com, authenticate this machine)
    2. verify: `gh auth status`
    3. retry: `git push -u origin main`

### 2026-02-26 12:28 UTC — GitHub authentication success + first sync to remote
- Why: complete mandatory commit/push workflow to Boss GitHub repository.
- Commands:
  - `gh auth login` (device flow)
  - `gh auth status`
  - `git push -u origin main`
- Files/paths touched:
  - `~/.config/gh/hosts.yml` (gh auth)
  - git remote tracking refs
- Capability impact:
  - assistant can now push setup/config logs to GitHub immediately after each change.
- Verification:
  - `gh auth status` shows logged in account `tritruc`
  - push succeeded: `main -> main`
- Rollback:
  - `gh auth logout`
  - `git remote remove origin` (if needed)
- GitHub push status:
  - SUCCESS (`origin/main` tracking configured)

### 2026-02-26 12:34 UTC — Verify OpenClaw auto-start on boot/session
- Why: user requested OpenClaw to run automatically when machine starts.
- Commands:
  - `openclaw gateway status`
  - `systemctl --user is-enabled openclaw-gateway.service`
  - `systemctl --user is-active openclaw-gateway.service`
- Files/paths touched:
  - none (verification only)
- Capability impact:
  - confirmed gateway user service is `enabled` + `active`.
- Verification:
  - status output shows systemd enabled and running.
- Rollback:
  - N/A.
- GitHub push status:
  - SUCCESS (included in commit `ded71c4`, pushed to `origin/main`).

### 2026-02-26 12:35 UTC — Add local machine action scripts (open URL / YouTube search)
- Why: allow owner to ask via chat to open content on their machine (example: YouTube karaoke).
- Commands:
  - create `scripts/open_url.sh`
  - create `scripts/open_youtube_search.sh`
  - `chmod +x scripts/open_url.sh scripts/open_youtube_search.sh`
  - test: `scripts/open_youtube_search.sh "karaoke con bướm xinh"`
- Files/paths touched:
  - `scripts/open_url.sh`
  - `scripts/open_youtube_search.sh`
  - `AGENTS.md`
  - `TOOLS.md`
  - `AllSetUp.md`
- Capability impact:
  - assistant can open URLs and YouTube searches on Windows desktop from WSL host.
- Verification:
  - script output: `Opened on Windows host: <url>`.
- Rollback:
  - remove scripts and revert docs/config commits.
- GitHub push status:
  - SUCCESS (included in commit `ded71c4`, pushed to `origin/main`).

### 2026-02-26 12:38 UTC — Add Windows Startup autostart bridge for OpenClaw
- Why: ensure OpenClaw starts automatically on Windows login, not only when WSL session is manually started.
- Commands:
  - create template: `scripts/OpenClaw-Autostart.bat`
  - copy to startup folder:
    - `cp scripts/OpenClaw-Autostart.bat "/mnt/c/Users/ADMIN/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/OpenClaw-Autostart.bat"`
  - startup command inside batch:
    - `wsl.exe -d Ubuntu -- bash -lc "systemctl --user start openclaw-gateway.service"`
- Files/paths touched:
  - `scripts/OpenClaw-Autostart.bat`
  - Windows startup folder batch file (outside repo)
  - `AllSetUp.md`
- Capability impact:
  - gateway auto-starts at Windows login, enabling Telegram control quickly after boot.
- Verification:
  - batch file exists and command is valid.
- Rollback:
  - delete startup file from Windows Startup folder.
- GitHub push status:
  - SUCCESS (included in commit `630a98e`, pushed to `origin/main`).

### 2026-02-26 14:05 UTC — Bind Gmail/Facebook actions to Chrome profile `AutomatedAccount`
- Why: owner confirmed Gmail + Facebook are logged in under profile name `AutomatedAccount`.
- Commands:
  - scan profiles from Chrome Local State (`.../User Data/Local State`)
  - update scripts:
    - `scripts/open_chrome_profile_url.sh` (resolve profile by name -> profile directory)
    - `scripts/open_gmail.sh`
    - `scripts/open_facebook.sh`
  - test:
    - `scripts/open_gmail.sh`
    - `scripts/open_facebook.sh`
- Files/paths touched:
  - `scripts/open_chrome_profile_url.sh`
  - `scripts/open_gmail.sh`
  - `scripts/open_facebook.sh`
  - `AGENTS.md`
  - `TOOLS.md`
  - `USER.md`
  - `AllSetUp.md`
- Capability impact:
  - Gmail/Facebook actions now default to profile name `AutomatedAccount` (mapped to `Profile 4`).
  - More robust profile handling even if directory mapping changes.
- Verification:
  - output confirms profile resolution:
    - `Opened in Chrome profile [Profile 4] (hint: AutomatedAccount): ...`
- Rollback:
  - revert these script/doc changes and restore fixed profile directory behavior.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-26 14:11 UTC — Enforce execution-first behavior for Telegram tasks
- Why: owner reported assistant gave guidance instead of finishing requested Facebook task.
- Commands:
  - update behavior rules in `AGENTS.md` (execute end-to-end by default)
  - update `AllSetUp.md` execution policy for Gmail/Facebook tasks
- Files/paths touched:
  - `AGENTS.md`
  - `AllSetUp.md`
  - `memory/2026-02-26.md`
- Capability impact:
  - assistant prioritizes doing the task directly; asks follow-up only when technically required.
  - formalized Chrome Relay requirement for full Facebook UI automation.
- Verification:
  - rule text present in AGENTS/AllSetUp.
- Rollback:
  - revert corresponding commit.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-26 14:33 UTC — Add platform/function/task hierarchy + custom execution skill
- Why: owner requested stronger completion behavior and structured storage for all automation assets.
- Commands:
  - create hierarchy folders:
    - `ops/platforms/facebook/messaging/`
    - `ops/platforms/gmail/actions/`
    - `ops/platforms/youtube/search/`
  - add task files:
    - `ops/platforms/facebook/messaging/send-message.md`
    - `ops/platforms/gmail/actions/open-gmail.md`
    - `ops/platforms/youtube/search/open-youtube-search.md`
  - create custom skill:
    - `skills/family-exec/SKILL.md`
    - `skills/family-exec/references/facebook-messaging-playbook.md`
  - verify skill discovery: `openclaw skills list`
- Files/paths touched:
  - `ops/...`
  - `skills/family-exec/...`
  - `AGENTS.md`
  - `USER.md`
  - `AllSetUp.md`
  - `memory/2026-02-26.md`
- Capability impact:
  - assistant now has explicit execution-first skill for local actions + Facebook messaging flow.
  - reusable structure for future scripts/tasks by platform and function.
- Verification:
  - `openclaw skills list` shows `family-exec` with source `openclaw-workspace`.
- Rollback:
  - remove new `ops/` + `skills/family-exec/` folders and revert commit.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-26 14:41 UTC — Fix Chrome stray tab bug (`0.0.0.4`) for profile launch
- Why: owner reported incorrect tabs opening (`0.0.0.4`) when launching Facebook/Gmail.
- Root cause:
  - Chrome profile arg contained space (`Profile 4`) and was not quoted robustly in PowerShell `Start-Process` argument string.
  - This caused argument splitting and stray navigation.
- Commands:
  - patch `scripts/open_chrome_profile_url.sh` to build fully quoted arg string:
    - `--profile-directory="Profile 4" --new-tab "<url>"`
  - test:
    - `scripts/open_facebook.sh`
    - `scripts/open_gmail.sh`
- Files/paths touched:
  - `scripts/open_chrome_profile_url.sh`
  - `AllSetUp.md`
  - `memory/2026-02-26.md`
- Capability impact:
  - Facebook/Gmail open command is now deterministic with `AutomatedAccount` profile.
- Verification:
  - scripts execute successfully and no new malformed URL is emitted by launcher.
- Rollback:
  - revert script to previous version (not recommended).
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-26 14:56 UTC — Evaluate Camoufox + install fallback automation engine
- Why: owner requested trying Camoufox / other apps to reduce UI control limitations.
- Commands:
  - create venv: `python3 -m venv .venv-camoufox`
  - install packages: `source .venv-camoufox/bin/activate && pip install camoufox playwright`
  - fetch browser: `camoufox fetch`
  - smoke test: `python scripts/camoufox_smoke_test.py`
  - install AutoHotkey on Windows user: `winget install --id AutoHotkey.AutoHotkey -e --accept-source-agreements --accept-package-agreements`
  - add fallback scripts/docs:
    - `scripts/windows/facebook_send_message.ahk`
    - `scripts/run_facebook_send_ahk.sh`
    - `ops/platforms/facebook/messaging/autohotkey-fallback.md`
    - `ops/platforms/facebook/messaging/camoufox-evaluation.md`
- Files/paths touched:
  - `.venv-camoufox/` (local environment)
  - Windows user install path for AutoHotkey
  - scripts and ops docs listed above
  - `AGENTS.md`, `TOOLS.md`, `AllSetUp.md`, `memory/2026-02-26.md`
- Capability impact:
  - Camoufox engine available for separate Firefox-based automation profile.
  - AutoHotkey fallback available for UI-level keyboard automation when Relay is unavailable.
- Verification:
  - `camoufox version` shows package and binary versions.
  - smoke test returns Facebook page title.
  - `winget list AutoHotkey` shows installed user package.
- Rollback:
  - remove venv `.venv-camoufox`
  - `camoufox remove`
  - uninstall AutoHotkey via `winget uninstall AutoHotkey.AutoHotkey`
  - remove fallback scripts/docs.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-26 15:06 UTC — Add login automation script for Gmail + Facebook (AutoHotkey)
- Why: owner requested direct auto-login execution instead of manual steps.
- Commands:
  - create script: `scripts/windows/login_google_facebook.ahk`
  - create wrapper: `scripts/run_login_google_facebook_ahk.sh`
  - test run with owner-provided runtime credentials (not persisted)
- Files/paths touched:
  - `scripts/windows/login_google_facebook.ahk`
  - `scripts/run_login_google_facebook_ahk.sh`
  - `TOOLS.md`, `AllSetUp.md`, `memory/2026-02-26.md`
- Capability impact:
  - assistant can trigger best-effort auto-login workflow for Gmail/Facebook in owner Chrome profile.
- Verification:
  - wrapper executes without runtime script error.
- Rollback:
  - remove the 2 scripts and revert docs.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-26 15:20 UTC — Handle Messenger PIN recovery popup in AHK fallback
- Why: owner reported Messenger requested PIN recovery code and blocked message send flow.
- Commands:
  - patch `scripts/windows/facebook_send_message.ahk`:
    - maximize window
    - send multiple `Esc` to dismiss modal
    - click sidebar search, locate recipient, open conversation
    - click composer and send message
  - re-run fallback sender:
    - `scripts/run_facebook_send_ahk.sh "Dương Công Mãn" "hahaha"`
- Files/paths touched:
  - `scripts/windows/facebook_send_message.ahk`
  - `ops/platforms/facebook/messaging/autohotkey-fallback.md`
  - `AllSetUp.md`
  - `memory/2026-02-26.md`
- Capability impact:
  - better resilience when PIN-recovery modal appears before sending.
- Verification:
  - command executes without script runtime error.
- Rollback:
  - revert script to prior simpler version.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-27 00:55 UTC — Enable Zalo Personal stack (zalouser) + install zca CLI
- Why: owner requested daily reminder automation on Zalo without OA.
- Commands:
  - `curl -fsSL https://get.zca-cli.dev/install.sh | bash`
  - `zca --version`
  - `~/.nvm/versions/node/v24.13.1/bin/openclaw plugins enable zalouser`
  - `~/.nvm/versions/node/v24.13.1/bin/openclaw channels add --channel zalouser`
  - `~/.nvm/versions/node/v24.13.1/bin/openclaw status`
- Files/paths touched:
  - `~/.local/bin/zca`
  - `~/.openclaw/openclaw.json`
  - `~/.openclaw/openclaw.json.bak`
- Capability impact:
  - machine now has `zca` binary available;
  - OpenClaw Zalo Personal channel is configured/enabled (authentication still required).
- Verification:
  - `zca --version` => `0.0.24`
  - `openclaw status` shows `Zalo Personal: ON` (state WARN until auth).
- Rollback:
  - disable plugin: `openclaw plugins disable zalouser`
  - remove channel account: `openclaw channels remove --channel zalouser`
  - uninstall zca: `curl -fsSL https://get.zca-cli.dev/install.sh | bash -s uninstall`
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-27 01:03 UTC — Create local web app for visual reminder management (ZaloUser)
- Why: owner requested a direct visual app/web to view/edit/delete reminders, manage sender accounts, and track reminder status.
- Commands:
  - `mkdir -p apps/zalo-reminder-manager`
  - create app server: `apps/zalo-reminder-manager/app.py`
  - create launcher: `scripts/run_zalo_reminder_manager.sh`
  - `chmod +x scripts/run_zalo_reminder_manager.sh`
  - `python3 -m py_compile apps/zalo-reminder-manager/app.py`
  - run app: `scripts/run_zalo_reminder_manager.sh`
- Files/paths touched:
  - `apps/zalo-reminder-manager/app.py`
  - `apps/zalo-reminder-manager/README.md`
  - `scripts/run_zalo_reminder_manager.sh`
  - runtime DB: `apps/zalo-reminder-manager/reminders.db`
- Capability impact:
  - new web UI at `http://127.0.0.1:8799` for:
    - account management (`account_id`, `zca profile`, self id)
    - recipient management (name, phone, threadId, group flag)
    - reminder CRUD (time, timezone, retry interval, ack requirement)
    - scheduler loop + listener loop + logs
  - supports rule: 08:00 GMT+7 reminder and retry every 30 minutes until valid date reply.
- Verification:
  - `curl http://127.0.0.1:8799/api/health` returns `{ "ok": true, ... }`
  - `curl http://127.0.0.1:8799/api/system/status` returns JSON status.
- Rollback:
  - stop app process;
  - remove app files and DB;
  - remove launcher script.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

### 2026-02-27 01:06 UTC — Run reminder web app as persistent user service
- Why: owner needs the reminder manager always available and scheduler running continuously.
- Commands:
  - create service: `~/.config/systemd/user/zalo-reminder-manager.service`
  - `systemctl --user daemon-reload`
  - `systemctl --user enable --now zalo-reminder-manager.service`
  - `systemctl --user status --no-pager zalo-reminder-manager.service`
- Files/paths touched:
  - `~/.config/systemd/user/zalo-reminder-manager.service`
  - symlink: `~/.config/systemd/user/default.target.wants/zalo-reminder-manager.service`
  - `scripts/systemd/zalo-reminder-manager.service`
  - `apps/zalo-reminder-manager/README.md`
- Capability impact:
  - app web + scheduler/listener now auto-start with user systemd session, not tied to one terminal process.
- Verification:
  - service state: `active (running)`
  - `curl http://127.0.0.1:8799/api/health` => `{ "ok": true, ... }`
- Rollback:
  - `systemctl --user disable --now zalo-reminder-manager.service`
  - remove service file and reload daemon.
- GitHub push status:
  - SUCCESS (pushed to `origin/main`).

---

### 2026-02-27 01:11 UTC — Update Windows Startup BAT to open Ubuntu terminal and bootstrap OpenClaw
- Why: owner requested that on Windows login it should auto-open Ubuntu terminal so OpenClaw can run reliably.
- Commands:
  - `write scripts/OpenClaw-Autostart.bat` (new logic: open Windows Terminal -> Ubuntu -> run startup commands -> keep shell open)
  - `cp scripts/OpenClaw-Autostart.bat "/mnt/c/Users/ADMIN/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/OpenClaw-Autostart.bat"`
  - Test command: `/mnt/c/Windows/System32/wsl.exe -d Ubuntu -- bash -lc "export PATH=...; cd /home/manduong/.openclaw/workspace; (systemctl --user start openclaw-gateway.service || ~/.nvm/versions/node/v24.13.1/bin/openclaw gateway start || true); systemctl --user start zalo-reminder-manager.service >/dev/null 2>&1 || true; echo '[OpenClaw] Startup done.'"`
- Files/paths touched:
  - `scripts/OpenClaw-Autostart.bat`
  - `C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenClaw-Autostart.bat`
- Capability impact:
  - On Windows login, Startup BAT opens Ubuntu terminal and runs OpenClaw bootstrap commands.
  - Keeps terminal open (`exec bash`) so owner can see runtime output immediately.
- Verification:
  - Manual run of WSL bootstrap command returned: `[OpenClaw] Startup done.`
  - Startup BAT file updated in Windows Startup folder.
- Rollback:
  - Restore previous BAT content, or delete Startup BAT from Startup folder.
- GitHub push status:
  - SUCCESS (commit `2943908` pushed to `origin/main`).

### 2026-02-27 01:22 UTC — Fix Windows Startup BAT quote bug (0x80070002) and verify Telegram delivery
- Why: Startup opened terminal but failed with `error 2147942402 (0x80070002)` around `" exec bash"`; owner also reported Telegram chat appeared not working.
- Root cause:
  - Windows Terminal (`wt.exe`) command parsing conflicted with embedded quoted shell string (`exec bash`) in BAT.
- Commands:
  - Rewrite BAT to avoid `wt.exe` parsing path and launch `wsl.exe` directly:
    - `write scripts/OpenClaw-Autostart.bat`
  - Sync Startup copy:
    - `cp scripts/OpenClaw-Autostart.bat "C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenClaw-Autostart.bat"`
  - Verify bootstrap command in WSL:
    - `/mnt/c/Windows/System32/wsl.exe -d Ubuntu -- bash -lc "cd /home/manduong/.openclaw/workspace; export PATH=...; ...; echo '[OpenClaw] Startup done.'"`
  - Verify Telegram send path:
    - `message.send(channel=telegram,target=6542038310,...)`
- Files/paths touched:
  - `scripts/OpenClaw-Autostart.bat`
  - `C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenClaw-Autostart.bat`
- Capability impact:
  - On Windows login, autostart now opens Ubuntu terminal via `wsl.exe` without the quote/launch error.
  - OpenClaw bootstrap commands execute from terminal start sequence.
  - Telegram outbound delivery validated.
- Verification:
  - Telegram test send succeeded: `ok=true`, `messageId=70`, `chatId=6542038310`.
  - `openclaw status`: Telegram channel `ON/OK`.
- Rollback:
  - Restore previous BAT using `wt.exe` path if desired.
- GitHub push status:
  - SUCCESS (commit `b2169a4` pushed to `origin/main`).

### 2026-02-27 01:29 UTC — Auto-launch OpenClaw TUI bound to Telegram session on Windows startup
- Why: owner requested that after boot, terminal should go straight into OpenClaw TUI and be linked to Telegram bot session.
- Commands:
  - `write scripts/autostart_openclaw_tui.sh`
  - `chmod +x scripts/autostart_openclaw_tui.sh`
  - `write scripts/OpenClaw-Autostart.bat`
  - `cp scripts/OpenClaw-Autostart.bat "C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenClaw-Autostart.bat"`
  - smoke test: `OPENCLAW_TUI_BOOT_MESSAGE="✅ TUI autostart test: Telegram session linked" timeout 35s scripts/autostart_openclaw_tui.sh`
- Files/paths touched:
  - `scripts/autostart_openclaw_tui.sh`
  - `scripts/OpenClaw-Autostart.bat`
  - `C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenClaw-Autostart.bat`
- Capability impact:
  - On Windows login, startup now opens Ubuntu and runs OpenClaw TUI automatically.
  - TUI default session pinned to Telegram direct session: `agent:main:telegram:direct:6542038310`.
  - TUI launched with `--deliver`, so replies from TUI are delivered to Telegram route.
- Verification:
  - TUI smoke output showed active session: `session telegram:direct:6542038310 (openclaw-tui)`.
  - `openclaw health --json` lists recent session key `agent:main:telegram:direct:6542038310`.
- Rollback:
  - Restore previous `scripts/OpenClaw-Autostart.bat`.
  - Remove `scripts/autostart_openclaw_tui.sh` from startup flow.
- GitHub push status:
  - SUCCESS (commit `d098436` pushed to `origin/main`).

## 7) Secret handling checklist (do not skip)

Never commit these raw values:
- Telegram bot token
- OpenAI/Gemini/any provider API key
- Gateway auth token

Use placeholders in docs:
- `<TELEGRAM_BOT_TOKEN>`
- `<OPENAI_API_KEY>`
- `<GITHUB_TOKEN_OR_OAUTH>`

Store secrets in:
- environment variables, or
- local OpenClaw config outside shared git repo, or
- dedicated secret manager.

## [2026-02-27 02:05:02 UTC] Remote access hardening for UltraViewer (autostart + watchdog + anti-sleep)

### Why
Boss yêu cầu đảm bảo luôn giữ quyền truy cập từ xa, giảm tối đa thao tác tay sau khi bật máy.

### What changed
1. Bật **tự khởi động UltraViewer** qua 2 lớp dự phòng:
   - Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (value `UltraViewer`)
   - Startup shortcut: `C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\UltraViewer.lnk`
2. Tạo **watchdog script** để tự mở lại UltraViewer nếu bị tắt:
   - Script: `%APPDATA%\UltraViewer\watchdog-ultraviewer.ps1`
3. Tạo **Scheduled Task** chạy watchdog mỗi 2 phút:
   - Task: `UltraViewerWatchdog2Min`
4. Tắt sleep/hibernate khi cắm điện để tránh mất kết nối:
   - `standby-timeout-ac = 0`
   - `hibernate-timeout-ac = 0`
5. Cập nhật rule vận hành trong `USER.md`:
   - Ưu tiên execution-first tuyệt đối; agent phải tự thử mọi cách trước khi yêu cầu Boss thao tác tay.

### Exact commands run
```bash
# prepare and run PowerShell config script
cat > /mnt/c/Users/ADMIN/AppData/Local/Temp/config_ultraviewer_remote.ps1 <<'PS1'
# (script body created by agent; includes Run key, Startup link, watchdog, schtasks, powercfg)
PS1
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\ADMIN\AppData\Local\Temp\config_ultraviewer_remote.ps1"

# verify
a) reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v UltraViewer
b) schtasks /Query /TN UltraViewerWatchdog2Min
c) powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE
```

### Files / config paths touched
- `C:\Users\ADMIN\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\UltraViewer.lnk`
- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (value: `UltraViewer`)
- `%APPDATA%\UltraViewer\watchdog-ultraviewer.ps1`
- Scheduled Task: `UltraViewerWatchdog2Min`
- `/home/manduong/.openclaw/workspace/USER.md`

### Capability impact
- Khi user đăng nhập Windows, UltraViewer sẽ tự mở lại.
- Nếu UltraViewer bị tắt ngoài ý muốn, watchdog sẽ tự bật lại trong tối đa ~2 phút.
- Máy giảm nguy cơ rớt kết nối do sleep khi cắm sạc.

### Verification result
- `Run\UltraViewer` tồn tại và trỏ đúng exe.
- Startup folder có `UltraViewer.lnk`.
- Task `UltraViewerWatchdog2Min` tồn tại (`Ready`, có Next Run Time).
- `STANDBYIDLE` AC = `0x00000000`.

### Limitations / notes
- Task ONLOGON thứ 2 (`UltraViewerWatchdogAtLogon`) bị `Access is denied`; không cần thiết vì đã có `Run` + Startup + watchdog định kỳ.
- Thiết lập “mật khẩu UltraViewer cố định” chưa auto-set bằng CLI (UltraViewer không có API/CLI public ổn định). Có thể cần thao tác UI đúng cửa sổ app để chốt mật khẩu cố định.

### Rollback
```powershell
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v UltraViewer /f
schtasks /Delete /TN "UltraViewerWatchdog2Min" /F
Remove-Item "$env:APPDATA\UltraViewer\watchdog-ultraviewer.ps1" -Force
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\UltraViewer.lnk" -Force
powercfg /change standby-timeout-ac 30
powercfg /change hibernate-timeout-ac 180
```

## [2026-02-27 05:41:26 UTC] Added stable Zalo desktop send-message execution flow

### What changed
- Added runbook: `ops/platforms/zalo/messaging/send-message-phone.md`
- Added PowerShell automation: `scripts/windows/zalo_send_message.ps1`
- Added WSL wrapper: `scripts/run_zalo_send.sh`

### Capability impact
- Agent can execute a repeatable Zalo send flow (search by phone -> open chat -> paste message -> send -> before/after proof screenshots).

### Verification
- Flow validated in live session by sending messages and capturing before/after screenshots.

### Rollback
- Remove files:
  - `ops/platforms/zalo/messaging/send-message-phone.md`
  - `scripts/windows/zalo_send_message.ps1`
  - `scripts/run_zalo_send.sh`

## [2026-02-27 05:51:40 UTC] Integrated Zalo desktop send flow into Reminder Manager + strict daily ack format

### What changed
- Updated `apps/zalo-reminder-manager/app.py`:
  - Reminder send now **prefers local desktop automation** (`scripts/run_zalo_send.sh`) when target has phone.
  - Fallback remains `zca msg send` then `openclaw message send`.
  - Daily stop condition changed to strict ack format:
    - `DD/MM/YYYY đã xong` or `YYYY-MM-DD đã xong`
  - Reminder template now instructs users to reply with exact format above.
- Updated `apps/zalo-reminder-manager/README.md` to reflect new ack syntax and send path.
- Restarted systemd user service: `zalo-reminder-manager.service`.

### Commands run
```bash
python3 -m py_compile apps/zalo-reminder-manager/app.py
systemctl --user restart zalo-reminder-manager.service
systemctl --user is-active zalo-reminder-manager.service
```

### Impact
- Daily spam/nhắc chỉ dừng khi người nhận trả lời đúng mẫu `"<ngày> đã xong"`.
- Sending path now aligns with verified human-like Zalo desktop flow for better reliability on this machine.

### Rollback
- Revert `apps/zalo-reminder-manager/app.py` + `README.md` to previous commit.
- Restart service:
```bash
systemctl --user restart zalo-reminder-manager.service
```

## [2026-02-27 06:00:00 UTC] Made Zalo reminder scheduler deterministic and service-centric (agent-independent)

### What changed
- Updated `apps/zalo-reminder-manager/app.py`:
  - Scheduler now uses **anchor slots** from `daily_time` + `retry_interval_min` (e.g. 13:00, 13:03, 13:06) instead of drift from last-send.
  - Added `send_count()` DB helper and slot-based due check.
  - Listener restart now uses exponential backoff (15s -> max 300s) to avoid noisy tight loops when zca license/auth is broken.
- Updated README wording to emphasize standalone service operation.
- Restarted `zalo-reminder-manager.service`.

### Verification
- `python3 -m py_compile apps/zalo-reminder-manager/app.py` OK
- `systemctl --user is-active zalo-reminder-manager.service` => `active`

### Rollback
- Revert `apps/zalo-reminder-manager/app.py` and `apps/zalo-reminder-manager/README.md` to previous commit and restart service.

## [2026-02-27 06:20:00 UTC] Hardened desktop-only Zalo send flow (no direct Zalo API path)

### What changed
- Updated `scripts/windows/zalo_send_message.ps1` to enforce full UI flow:
  1) focus Zalo
  2) clear and paste phone into search
  3) Enter + fallback click first result
  4) focus composer, paste message
  5) click send + Enter fallback
- Added extra proof screenshot at search stage:
  - `zalo_after_search.png`
- Updated wrapper output in `scripts/run_zalo_send.sh` to include 3 proof screenshots.

### Why
- Prevent drift/nhầm luồng caused by partial focus and ambiguous result selection.
- Ensure sending is strictly via desktop automation (human-like), not direct Zalo service APIs.

### Verification
- Ran: `scripts/run_zalo_send.sh "0913885625" "test luong moi"`
- Returned paths for `SEARCH`, `BEFORE`, `AFTER` screenshots.

### Rollback
- Revert `scripts/windows/zalo_send_message.ps1` and `scripts/run_zalo_send.sh` to previous commit.

## [2026-02-27 07:10:32 UTC] Added configurable reminder ack_text (default `ok`)

### What changed
- Updated `apps/zalo-reminder-manager/app.py`:
  - Added `DEFAULT_ACK_TEXT = "ok"`.
  - Reminders now store `ack_text` (DB migration auto-adds `ack_text` column for old DBs).
  - Ack matching logic now supports:
    - exact `ack_text` (default `ok`),
    - `ack_text` template with `{date}` placeholder,
    - backward compatibility for `<date> đã xong`.
  - Default reminder message now includes reminder-specific ack hint.
  - UI now has `rAck` field to configure ack phrase per reminder.
- Updated `apps/zalo-reminder-manager/README.md` for new ack behavior.
- Set existing reminder #1 `ack_text='ok'`.

### Verification
- `python3 -m py_compile apps/zalo-reminder-manager/app.py` OK.
- DB column exists: `PRAGMA table_info(reminders)` includes `ack_text`.
- Service active after restart.

### Rollback
- Revert app/README and restart service.

## [2026-02-27 07:41:15 UTC] Enforced next-day start when schedule time already passed

### What changed
- Updated `apps/zalo-reminder-manager/app.py`:
  - Added `start_date` field for reminders (auto-migrated on startup).
  - On create/update reminder, if current local time is already past `daily_time`, app sets `start_date = tomorrow`.
  - Scheduler now skips sends before `start_date`.
- Updated reminder #1 (0913885625):
  - `daily_time=14:15`, `retry_interval_min=1`, `timezone=Asia/Ho_Chi_Minh`, `ack_text=ok`, `start_date=2026-02-28`.

### Why
- Match required behavior: if user sets a time that already passed today, first send must start next day (not immediately today).

### Verification
- DB schema includes `start_date`.
- Reminder #1 shows `start_date=2026-02-28` while current VN time was 14:41.

### Rollback
- Revert app.py and set `start_date` to NULL for reminders if needed.

## [2026-02-27 07:50:55 UTC] Auto-send confirmation after valid ACK reply

### What changed
- Updated `apps/zalo-reminder-manager/app.py`:
  - After detecting valid ACK reply, app now sends confirmation message:
    - `✅ Đã nhận xác nhận. Em sẽ dừng nhắc trong hôm nay (YYYY-MM-DD).`
  - Added `send_ack_confirmation()` with same transport strategy:
    - prefer desktop automation (`run_zalo_send.sh`) when phone is available,
    - fallback to `zca` and `openclaw message send`.
  - Added log events: `ack_confirm_send`, `ack_confirm_error`.
- Updated `apps/zalo-reminder-manager/README.md` to document confirmation message behavior.
- Restarted `zalo-reminder-manager.service`.

### Verification
- `python3 -m py_compile apps/zalo-reminder-manager/app.py` OK.
- service status: `active`.

### Rollback
- Revert app.py/README and restart service.

## [2026-02-27 07:58:34 UTC] Added desktop-only ACK detection via OCR (no Zalo API listener dependency)

### What changed
- Added desktop capture script:
  - `scripts/windows/zalo_capture_chat.ps1` (open chat by phone + screenshot current chat view)
- Added OCR parser:
  - `scripts/ocr_ack_check.js` using `tesseract.js` (local OCR)
- Added runner:
  - `scripts/run_zalo_check_ack.sh <phone> [ack_text]` -> outputs `ACK_FOUND=1/0`
- Integrated into `apps/zalo-reminder-manager/app.py` scheduler:
  - before sending retry, run desktop ACK probe
  - if ACK detected: write `daily_acks`, log `ack`, send confirmation message, skip further sends
  - added log event `ack_probe`

### Dependency
- Installed workspace-local npm dependency: `tesseract.js`

### Verification
- `scripts/run_zalo_check_ack.sh "0913885625" "ok"` returned `ACK_FOUND=1`
- Service restarted and active.

### Note
- Current reminder #1 is intentionally `active=0` for anti-spam safety until owner re-enables.

## [2026-02-27 08:10:10 UTC] Fixed reminder behavior: keep sending until NEW ack arrives

### Problem
- OCR ack probe could match old `ok` already visible in chat history, causing premature stop.

### Fix
- Added `ack_baselines` table to store per-day baseline `user_ok_count` after first send.
- Updated OCR script `scripts/ocr_ack_check.js` to output `USER_OK_COUNT`.
- Scheduler logic now:
  1) sends first scheduled message,
  2) records baseline user-ok count,
  3) only stops when current `USER_OK_COUNT` increases above baseline (new ack event).

### Safety reset
- Cleared today's `daily_acks` + baseline and re-enabled reminder #1.

### Verification
- `run_zalo_check_ack.sh ...` now reports `ACK_FOUND=0` when only old history is present.
- Service restarted and active.

## [2026-02-27 08:19:19 UTC] Final hardening for false-stop bug (OCR ACK)

### What changed
- Switched default ACK phrase to `ok đã xong` (longer, less OCR-noise-prone).
- OCR checker now rejects too-short ack text (<4 chars), so `ok` alone is no longer accepted in OCR mode.
- Added guard to prevent duplicate confirmation sends:
  - `was_ack_confirmed_today()` checks `ack_confirm_send` log before sending confirm.
- Updated UI default ack field and README defaults accordingly.
- Updated reminder #1 ack_text to `ok đã xong`; reset today's ack/baseline state.

### Why
- Prevent false positives where historical/noisy OCR text containing `ok` caused premature stop.

### Verification
- app compiled and service restarted successfully.
- reminder #1 now uses `ack_text='ok đã xong'`.

### Rollback
- Revert app.py / ocr_ack_check.js / README and restart service.

## [2026-02-27 08:26:35 UTC] Removed ACK phrase echo from reminder messages (prevent self-match false stops)

### Problem
- OCR ACK detection looked for `ack_text` in chat image.
- Reminder message itself previously echoed the same phrase, causing self-content contamination and unstable stop behavior.

### Fix
- Updated `send_reminder()` text generation in `app.py`:
  - no longer appends exact ack phrase into outgoing reminder body,
  - uses generic confirmation line instead.
- Kept ack phrase as external/shared rule (`ack_text='ok đã xong'`) for detector.
- Reset today state for reminder #1:
  - cleared `daily_acks` and `ack_baselines`, re-enabled active.

### Verification
- service restarted successfully.
- reminder state reset for clean re-test.

## [2026-02-27 08:39:10 UTC] Final redesign of ACK flow: daily code confirmation (anti-loop)

### Why
Current OCR-based `ok`/plain-text ACK was too noisy and caused false stop / endless loop behavior.

### What changed
- `app.py` redesigned ACK strategy:
  - Default `ack_text` is now keyword `xong`.
  - For each reminder/day, system generates deterministic 4-digit code from `(reminder_id, local_date)`.
  - Expected ACK phrase is now: `xong <code>` (example: `xong 5760`).
  - Reminder message now includes:
    - `Mã xác nhận hôm nay: <code>`
    - `Khi xong, nhắn: XONG + MÃ`
    - and does **not** echo the exact full phrase to avoid OCR self-match.
- Desktop ACK probe now receives full expected phrase (`xong <code>`) and logs `EXPECT=...` for debugging.
- Inbound matcher (when listener available) also checks against the same expected phrase.
- `ocr_ack_check.js` improved:
  - short ack phrases are rejected;
  - adds compact-match fallback for OCR spacing errors.
- UI defaults updated to keyword mode (`xong`).

### Runtime reset
- Reminder #1 reconfigured and reset:
  - `active=1`, `daily_time=15:00`, `retry_interval_min=1`, `ack_text='xong'`, `start_date=today`
  - cleared today's `daily_acks` and `ack_baselines`.

### Verification
- Computed today expected phrase: `xong 5760`.
- `run_zalo_check_ack.sh "0913885625" "xong 5760"` returns `ACK_FOUND=0` before user confirms (correct).

### Rollback
- Revert `app.py` and `scripts/ocr_ack_check.js` to previous commit.
- Restart `zalo-reminder-manager.service`.
