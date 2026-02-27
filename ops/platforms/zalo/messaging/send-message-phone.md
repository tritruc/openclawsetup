# Zalo send-message flow (đã kiểm chứng)

## Mục tiêu
Tìm theo số điện thoại, nhập đúng ô chat, bấm gửi chắc chắn.

## Flow chuẩn
1. Activate cửa sổ `Zalo`.
2. Click ô tìm kiếm (top-left), `Ctrl+A`, nhập số điện thoại.
3. `Down` + `Enter` để mở đúng kết quả đầu tiên.
4. Click ô nhập tin nhắn (composer) ở đáy khung chat.
5. Dán nội dung Unicode bằng Clipboard (`Ctrl+V`) để tránh lỗi dấu tiếng Việt.
6. Chụp ảnh **trước gửi**.
7. Bấm nút Gửi (tọa độ nút gửi) + `Enter` dự phòng.
8. Chụp ảnh **sau gửi**.

## Script
- PowerShell: `scripts/windows/zalo_send_message.ps1`
- Wrapper WSL: `scripts/run_zalo_send.sh "<phone>" "<message>"`

## Ghi chú tọa độ (màn hiện tại)
- Search box: `(178, 52)`
- Composer: `(760, 744)`
- Send button: `(1185, 744)`

Nếu DPI/window thay đổi thì cập nhật tọa độ.
