# CongCu.md — Nhật ký cấu hình hệ thống & hướng dẫn tái dựng OpenClaw

> Mục tiêu: ghi lại **đầy đủ thay đổi ảnh hưởng hệ thống** để một agent khác có thể dựng lại môi trường nhanh, đúng, và an toàn.

## 1) Thông tin môi trường hiện tại

- Host: `DESKTOP-4BJR7KN` (WSL2 Linux)
- Kernel: `6.6.87.2-microsoft-standard-WSL2`
- Node: `v25.6.1`
- OpenClaw: `2026.2.25`
- Workspace: `/home/manduong/.openclaw/workspace`
- OpenClaw CLI path: `/home/manduong/.nvm/versions/node/v24.13.1/bin/openclaw`

### Kênh đang bật

- Telegram: `enabled=true`, trạng thái `OK`
- Bot username hiện tại: `@linh0205_bot`

### Công cụ STT/TTS liên quan

- `whisper` (local CLI) có sẵn tại `/home/linuxbrew/.linuxbrew/bin/whisper`
- `gemini` CLI có sẵn (dự phòng)

---

## 2) Cấu hình OpenClaw quan trọng (đang áp dụng)

> **Không lưu secret thô vào git.** Nếu cần token/API key, dùng env vars hoặc secret store.

### Telegram streaming (để theo dõi phản hồi realtime)

```bash
openclaw config set channels.telegram.streaming partial
```

### Xử lý voice/audio bằng Whisper local

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

### Sau mỗi thay đổi config

```bash
openclaw gateway restart
openclaw status --deep
```

---

## 3) Playbook dựng mới nhanh (máy mới)

1. Cài OpenClaw CLI và đảm bảo chạy được `openclaw --version`.
2. Cài Whisper CLI (`whisper`) và kiểm tra `which whisper`.
3. Cấu hình Git identity (nếu cần commit tự động):
   ```bash
   git config --global user.name "tritruc"
   git config --global user.email "vudinhcmm.py@gmail.com"
   ```
4. Cấu hình Telegram channel:
   - `channels.telegram.enabled=true`
   - `channels.telegram.botToken=<FROM_SECRET_STORE>`
   - `channels.telegram.dmPolicy=pairing`
5. Bật streaming Telegram: `channels.telegram.streaming=partial`.
6. Bật `tools.media.audio` dùng Whisper local như khối config ở mục (2).
7. Restart gateway + kiểm tra `openclaw status --deep` phải thấy Telegram `OK`.
8. Pair user Telegram:
   - User nhắn `/start` vào bot để nhận pairing code
   - Chủ bot chạy: `openclaw pairing approve telegram <PAIRING_CODE>`

---

## 4) Quy ước nhật ký thay đổi bắt buộc

Mỗi thay đổi ảnh hưởng hệ thống phải thêm vào mục **Change Log** với đủ:

- UTC timestamp
- Mục tiêu
- Lệnh đã chạy
- File/path bị ảnh hưởng
- Năng lực mới có được
- Cách kiểm tra
- Cách rollback
- Trạng thái push GitHub

---

## 5) Change Log

### 2026-02-26 11:24 UTC — Khởi tạo danh tính agent
- Mục tiêu: hoàn tất bootstrap danh tính + lưu vào workspace.
- Thay đổi:
  - `IDENTITY.md`: Name=`Linh`, Creature=`Trợ lý AI cho gia đình`, Vibe an toàn/lịch sự/rõ ràng, Emoji=`🌿`
  - `USER.md`: gọi người dùng là `Boss`, trợ lý xưng `em`
  - `memory/2026-02-26.md`: ghi nhớ bootstrap
- Kiểm tra: file đã tồn tại và chứa đúng nội dung.
- Rollback: khôi phục từ git commit trước.

### 2026-02-26 11:24 UTC — Cấu hình Git identity
- Lệnh:
  - `git config --global user.name "tritruc"`
  - `git config --global user.email "vudinhcmm.py@gmail.com"`
- Năng lực: commit không còn lỗi `Author identity unknown`.
- Kiểm tra: `git config --global --get user.name/email`.
- Rollback: `git config --global --unset user.name` + `--unset user.email`.

### 2026-02-26 11:57 UTC — Pair Telegram user
- Lệnh: `openclaw pairing approve telegram CCDW24CJ`
- Kết quả: approve user id Telegram `6542038310`.
- Năng lực: user có thể chat bot qua DM Telegram.
- Kiểm tra: `openclaw status --deep` + test nhắn bot.
- Rollback: đổi `dmPolicy`/allowlist hoặc revoke theo policy pairing.

### 2026-02-26 11:59 UTC — Bật Telegram streaming preview
- Lệnh: `openclaw config set channels.telegram.streaming partial`
- Năng lực: trả lời dạng preview/chỉnh sửa tin nhắn theo tiến trình.
- Kiểm tra: `openclaw config get channels.telegram.streaming` trả `partial`.
- Rollback: set về `off`.

### 2026-02-26 12:09 UTC — Bật nhận diện voice tiếng Việt (Whisper local)
- Lệnh: cấu hình `tools.media.audio` dùng CLI `whisper` model `base`, language `Vietnamese`, timeout `120s`.
- Năng lực: nhận voice/audio từ Telegram, chuyển transcript để agent xử lý yêu cầu.
- Kiểm tra:
  - `openclaw config get tools.media.audio`
  - gửi 1 voice note test qua Telegram
- Rollback:
  - `openclaw config unset tools.media.audio` (hoặc set `enabled=false`)

### 2026-02-26 12:10 UTC — Thiết lập chính sách tài liệu hệ thống
- Thay đổi:
  - `AGENTS.md`: thêm rule bắt buộc cập nhật `CongCu.md` + push GitHub sau thay đổi hệ thống
  - `USER.md`: thêm ưu tiên accessibility cho người lớn tuổi mờ mắt
- Năng lực: chuẩn hóa tài liệu vận hành, dễ bàn giao cho agent khác.
- Kiểm tra: đọc lại `AGENTS.md`, `CongCu.md`, `USER.md`.
- Rollback: revert commit tương ứng.

---

## 6) Trạng thái GitHub sync

- Repo local đã có commit lịch sử.
- **Hiện chưa push được vì chưa cấu hình remote/auth GitHub trong máy này.**
- Cần làm để bật push tự động:
  1. `git remote add origin <GITHUB_REPO_URL>`
  2. `gh auth login` (hoặc dùng PAT)
  3. `git push -u origin <branch>`

Khi hoàn tất 3 bước trên, mọi thay đổi hệ thống tiếp theo sẽ được commit + push ngay theo rule.
