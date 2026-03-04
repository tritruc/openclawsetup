# BMAD + ProxyPal role map (local)

## Proxy endpoint
- Base URL: `http://127.0.0.1:8317/v1`
- API Key: `proxypal-local`

## Suggested role mapping
- **Planner/Analyst** (brief/spec/research): model mạnh phân tích (Claude/GPT)
- **Coder** (implement/fix): model tối ưu coding (Codex/Copilot bridge)
- **Reviewer/QA** (review/test/refactor): model khác coder để phản biện chéo

## Important
- ProxyPal đã cài + chạy local, nhưng hiện chưa có model nào vì cần đăng nhập subscription trong app ProxyPal.
- Sau khi login provider trong app, test nhanh:
  ```bash
  curl -H 'Authorization: Bearer proxypal-local' http://127.0.0.1:8317/v1/models
  ```

## OpenAI-compatible clients
Dùng cùng một cấu hình:
- `OPENAI_BASE_URL=http://127.0.0.1:8317/v1`
- `OPENAI_API_KEY=proxypal-local`
