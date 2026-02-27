# Zalo Reminder Manager

Web app quản lý nhắc hẹn Zalo (zalouser), có:

- CRUD nhắc hẹn (xem/sửa/xoá)
- Quản lý người nhận kèm số điện thoại
- Quản lý tài khoản gửi (account_id + zca profile)
- Nhắc mỗi ngày theo giờ cố định (mặc định 08:00 Asia/Ho_Chi_Minh)
- Nếu chưa xác nhận đúng ngày thì tự nhắc lại mỗi 30 phút
- Khi người nhận trả lời đúng ngày (DD/MM/YYYY hoặc YYYY-MM-DD) thì dừng nhắc trong hôm đó
- Nhật ký gửi/ack/lỗi

## Chạy app

```bash
cd ~/.openclaw/workspace
scripts/run_zalo_reminder_manager.sh
```

Mở: `http://127.0.0.1:8799`

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
