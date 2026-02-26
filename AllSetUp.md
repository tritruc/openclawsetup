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

Make executable:

```bash
chmod +x scripts/open_url.sh scripts/open_youtube_search.sh
```

Usage examples:

```bash
scripts/open_url.sh "https://www.youtube.com"
scripts/open_youtube_search.sh "karaoke con bướm xinh"
```

Implementation opens Windows apps through:

- `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- `Start-Process '<url>'`

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

---

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
