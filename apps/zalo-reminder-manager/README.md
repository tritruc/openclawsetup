# Zalo Reminder Manager

Web app quản lý nhắc hẹn Zalo (zalouser), có:

- CRUD nhắc hẹn (xem/sửa/xoá)
- Quản lý người nhận kèm số điện thoại
- Quản lý tài khoản gửi (account_id + zca profile)
- Nhắc mỗi ngày theo giờ cố định (mặc định 08:00 Asia/Ho_Chi_Minh)
- Nếu chưa xác nhận đúng cú pháp thì tự nhắc lại mỗi 30 phút
- Khi người nhận trả lời đúng cú pháp `<ngày> đã xong` (DD/MM/YYYY đã xong hoặc YYYY-MM-DD đã xong) thì dừng nhắc trong hôm đó
- Ưu tiên gửi qua luồng desktop automation (script `run_zalo_send.sh`) để thao tác như người dùng thật
- Nhật ký gửi/ack/lỗi

## Chạy app

```bash
cd ~/.openclaw/workspace
scripts/run_zalo_reminder_manager.sh
```

Mở: `http://127.0.0.1:8799`

## Chạy nền bằng systemd user service (đã áp dụng trên máy hiện tại)

```bash
systemctl --user status zalo-reminder-manager.service
systemctl --user restart zalo-reminder-manager.service
systemctl --user stop zalo-reminder-manager.service
```

Template service trong repo:

`scripts/systemd/zalo-reminder-manager.service`

Service file runtime:

`~/.config/systemd/user/zalo-reminder-manager.service`

## Bắt buộc trước khi gửi được tin

`zca-cli` hiện yêu cầu license và phiên đăng nhập:

1) Kích hoạt license

```bash
zca license support-code
zca license activate <key>
```

2) Đăng nhập ZaloUser profile mặc định

```bash
openclaw channels login --channel zalouser
```

(Quét QR bằng app Zalo trên điện thoại)

## Dữ liệu

SQLite DB: `apps/zalo-reminder-manager/reminders.db`
