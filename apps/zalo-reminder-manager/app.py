#!/usr/bin/env python3
import json
import os
import re
import sqlite3
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

APP_TZ = "Asia/Ho_Chi_Minh"
DEFAULT_RETRY_MIN = 30
DEFAULT_DAILY_TIME = "08:00"
DEFAULT_ACK_TEXT = "ok đã xong"
DB_PATH = Path(os.environ.get("ZALO_REMINDER_DB", Path(__file__).with_name("reminders.db")))
OPENCLAW_BIN = os.environ.get("OPENCLAW_BIN", "/home/manduong/.nvm/versions/node/v24.13.1/bin/openclaw")
ZCA_BIN = os.environ.get("ZCA_BIN", "zca")
ZALO_SEND_SH = os.environ.get("ZALO_SEND_SH", "/home/manduong/.openclaw/workspace/scripts/run_zalo_send.sh")
ZALO_CHECK_ACK_SH = os.environ.get("ZALO_CHECK_ACK_SH", "/home/manduong/.openclaw/workspace/scripts/run_zalo_check_ack.sh")
HOST = os.environ.get("ZALO_REMINDER_HOST", "127.0.0.1")
PORT = int(os.environ.get("ZALO_REMINDER_PORT", "8799"))


INDEX_HTML = r"""
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Zalo Reminder Manager</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 16px; background: #f6f7fb; color: #111; }
    h1 { margin: 0 0 8px; }
    .muted { color: #666; font-size: 14px; }
    .grid { display: grid; gap: 14px; }
    .card { background: #fff; border-radius: 12px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .row { display: flex; gap: 8px; flex-wrap: wrap; }
    input, select, textarea, button { font: inherit; padding: 8px; border-radius: 8px; border: 1px solid #ccc; }
    textarea { min-height: 70px; width: 100%; }
    button { cursor: pointer; border: none; background: #1f6feb; color: #fff; }
    button.secondary { background: #5b6578; }
    button.warn { background: #d73a49; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { border-bottom: 1px solid #eee; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #fafafa; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .pill { padding: 3px 8px; border-radius: 20px; font-size: 12px; background: #e7f0ff; color: #114; }
    .right { margin-left: auto; }
    .ok { color: #0a7d2a; font-weight: 600; }
    .bad { color: #b42318; font-weight: 600; }
  </style>
</head>
<body>
  <h1>🌿 Zalo Reminder Manager</h1>
  <div class="muted">Quản lý nhắc hẹn theo ngày + yêu cầu xác nhận đúng cú pháp: DD/MM/YYYY đã xong (hoặc YYYY-MM-DD đã xong).</div>

  <div class="grid" style="margin-top:12px">
    <section class="card">
      <div class="row">
        <div><b>System</b></div>
        <button class="secondary" onclick="refreshAll()">Làm mới</button>
        <button class="secondary" onclick="openAuthGuide()">Hướng dẫn đăng nhập ZaloUser</button>
        <div class="right" id="sysStatus"></div>
      </div>
      <div id="sysMeta" class="muted" style="margin-top:6px"></div>
    </section>

    <section class="card">
      <h3>1) Tài khoản gửi (Accounts)</h3>
      <div class="row">
        <input id="accId" placeholder="account_id (vd: default)"/>
        <input id="accName" placeholder="Tên hiển thị"/>
        <input id="accProfile" placeholder="ZCA profile (vd: default)"/>
        <label><input id="accEnabled" type="checkbox" checked/> Enabled</label>
        <button onclick="saveAccount()">Lưu tài khoản</button>
      </div>
      <table id="accountsTbl"></table>
    </section>

    <section class="card">
      <h3>2) Người nhận (kèm số điện thoại)</h3>
      <div class="row">
        <input id="tName" placeholder="Tên người nhận"/>
        <input id="tPhone" placeholder="Số điện thoại"/>
        <input id="tThread" placeholder="threadId Zalo (bắt buộc để gửi)" style="min-width:260px"/>
        <select id="tAccount"></select>
        <label><input id="tGroup" type="checkbox"/> Group</label>
        <label><input id="tActive" type="checkbox" checked/> Active</label>
        <button onclick="saveTarget()">Lưu người nhận</button>
      </div>
      <table id="targetsTbl"></table>
    </section>

    <section class="card">
      <h3>3) Nhắc hẹn hằng ngày</h3>
      <div class="row">
        <input id="rTitle" placeholder="Tên nhắc hẹn" style="min-width:220px"/>
        <select id="rTarget"></select>
        <input id="rTime" type="time" value="08:00"/>
        <input id="rTz" value="Asia/Ho_Chi_Minh"/>
        <input id="rRetry" type="number" min="5" value="30" style="width:90px"/>
        <input id="rAck" value="ok đã xong" placeholder="Reply để dừng (mặc định: ok đã xong)" style="min-width:220px"/>
        <label><input id="rNeedAck" type="checkbox" checked/> Cần xác nhận</label>
        <label><input id="rActive" type="checkbox" checked/> Active</label>
      </div>
      <textarea id="rMsg" placeholder="Nội dung nhắc (có thể để trống để dùng mẫu mặc định)"></textarea>
      <div class="row">
        <button onclick="saveReminder()">Lưu nhắc hẹn</button>
      </div>
      <table id="remindersTbl"></table>
    </section>

    <section class="card">
      <h3>4) Nhật ký</h3>
      <div class="row">
        <button class="secondary" onclick="loadLogs()">Làm mới log</button>
      </div>
      <table id="logsTbl"></table>
    </section>
  </div>

<script>
let edit = { accountId:null, targetId:null, reminderId:null };

async function api(path, opts={}) {
  const r = await fetch(path, { headers:{'Content-Type':'application/json'}, ...opts });
  const t = await r.text();
  let j; try { j = JSON.parse(t); } catch { j = {raw:t}; }
  if (!r.ok) throw new Error(j.error || t || ('HTTP '+r.status));
  return j;
}

function esc(s){ return (s??'').toString().replace(/[&<>\"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c])); }

async function refreshSystem(){
  const s = await api('/api/system/status');
  document.getElementById('sysStatus').innerHTML = `${s.licenseOk ? '<span class=ok>License OK</span>' : '<span class=bad>License thiếu</span>'} · ${s.authenticated ? '<span class=ok>Đã login</span>' : '<span class=bad>Chưa login</span>'}`;
  document.getElementById('sysMeta').innerText = `openclaw: ${s.openclawBin} | zca: ${s.zcaBin} | profile: ${s.defaultProfile}`;
}

function openAuthGuide(){
  alert('Bước bắt buộc 1 lần:\n1) Mở terminal\n2) zca license support-code -> nhận code\n3) zca license activate <key>\n4) openclaw channels login --channel zalouser\n5) quét QR bằng Zalo trên điện thoại');
}

async function loadAccounts(){
  const rows = await api('/api/accounts');
  const sel = document.getElementById('tAccount');
  sel.innerHTML = rows.map(r=>`<option value="${esc(r.account_id)}">${esc(r.account_id)} (${esc(r.zca_profile)})</option>`).join('');

  let html = '<tr><th>Account</th><th>Tên</th><th>Profile</th><th>Self ID</th><th>Enabled</th><th></th></tr>';
  for(const r of rows){
    html += `<tr>
      <td class='mono'>${esc(r.account_id)}</td>
      <td>${esc(r.name||'')}</td>
      <td class='mono'>${esc(r.zca_profile)}</td>
      <td class='mono'>${esc(r.self_id||'')}</td>
      <td>${r.enabled? '✅':'❌'}</td>
      <td>
        <button class='secondary' onclick='pickAccount(${JSON.stringify(r.account_id)})'>Sửa</button>
        <button class='secondary' onclick='refreshSelfId(${JSON.stringify(r.account_id)})'>Lấy selfId</button>
        <button class='warn' onclick='delAccount(${JSON.stringify(r.account_id)})'>Xoá</button>
      </td>
    </tr>`;
  }
  document.getElementById('accountsTbl').innerHTML = html;
}

async function pickAccount(id){
  const rows = await api('/api/accounts');
  const r = rows.find(x=>x.account_id===id); if(!r) return;
  edit.accountId = id;
  accId.value = r.account_id; accName.value = r.name||''; accProfile.value = r.zca_profile||'default'; accEnabled.checked = !!r.enabled;
}

async function saveAccount(){
  const body = { account_id: accId.value.trim(), name: accName.value.trim(), zca_profile: accProfile.value.trim()||'default', enabled: accEnabled.checked?1:0 };
  if(!body.account_id) return alert('Thiếu account_id');
  await api('/api/accounts', { method:'POST', body: JSON.stringify(body) });
  edit.accountId = null; accId.value=''; accName.value=''; accProfile.value='default'; accEnabled.checked=true;
  await refreshAll();
}

async function delAccount(id){ if(!confirm('Xoá account '+id+'?')) return; await api('/api/accounts/'+encodeURIComponent(id), {method:'DELETE'}); await refreshAll(); }
async function refreshSelfId(id){ await api('/api/accounts/'+encodeURIComponent(id)+'/refresh-self-id', {method:'POST'}); await refreshAll(); }

async function loadTargets(){
  const rows = await api('/api/targets');
  const tSel = document.getElementById('rTarget');
  tSel.innerHTML = rows.map(r=>`<option value='${r.id}'>${esc(r.name)} (${esc(r.phone||'no-phone')})</option>`).join('');

  let html = '<tr><th>ID</th><th>Tên</th><th>Phone</th><th>Thread ID</th><th>Account</th><th>Trạng thái</th><th></th></tr>';
  for(const r of rows){
    html += `<tr>
      <td>${r.id}</td><td>${esc(r.name)}</td><td>${esc(r.phone||'')}</td>
      <td class='mono'>${esc(r.thread_id)}</td><td>${esc(r.account_id)}</td>
      <td>${r.active? '✅':'❌'} ${r.is_group? '<span class="pill">Group</span>':''}</td>
      <td>
        <button class='secondary' onclick='pickTarget(${r.id})'>Sửa</button>
        <button class='warn' onclick='delTarget(${r.id})'>Xoá</button>
      </td>
    </tr>`;
  }
  document.getElementById('targetsTbl').innerHTML = html;
}

async function pickTarget(id){
  const rows = await api('/api/targets');
  const r = rows.find(x=>x.id===id); if(!r) return;
  edit.targetId = id;
  tName.value=r.name||''; tPhone.value=r.phone||''; tThread.value=r.thread_id||''; tAccount.value=r.account_id||'default'; tGroup.checked=!!r.is_group; tActive.checked=!!r.active;
}

async function saveTarget(){
  const body = { id: edit.targetId, name: tName.value.trim(), phone: tPhone.value.trim(), thread_id: tThread.value.trim(), account_id: tAccount.value, is_group: tGroup.checked?1:0, active: tActive.checked?1:0 };
  if(!body.name || !body.thread_id) return alert('Thiếu tên hoặc threadId');
  await api('/api/targets', { method:'POST', body: JSON.stringify(body)});
  edit.targetId=null; tName.value=''; tPhone.value=''; tThread.value=''; tGroup.checked=false; tActive.checked=true;
  await refreshAll();
}

async function delTarget(id){ if(!confirm('Xoá người nhận #'+id+'?')) return; await api('/api/targets/'+id,{method:'DELETE'}); await refreshAll(); }

async function loadReminders(){
  const rows = await api('/api/reminders');
  let html = '<tr><th>ID</th><th>Tên</th><th>Người nhận</th><th>Lịch</th><th>Nội dung</th><th>Trạng thái</th><th></th></tr>';
  for(const r of rows){
    html += `<tr>
      <td>${r.id}</td>
      <td>${esc(r.title)}</td>
      <td>${esc(r.target_name||'')}<br><span class='muted'>${esc(r.phone||'')}</span></td>
      <td>${esc(r.daily_time)}<br><span class='muted'>${esc(r.timezone)} · ${r.retry_interval_min}p</span></td>
      <td>${esc((r.message_template||'').slice(0,120))}<br><span class='muted'>Ack: ${esc(r.ack_text||'ok đã xong')}</span></td>
      <td>${r.active? '✅':'❌'} ${r.require_date_ack? '<span class="pill">cần xác nhận</span>':''}</td>
      <td>
        <button class='secondary' onclick='pickReminder(${r.id})'>Sửa</button>
        <button class='secondary' onclick='sendNow(${r.id})'>Gửi ngay</button>
        <button class='secondary' onclick='ackToday(${r.id})'>Ack hôm nay</button>
        <button class='warn' onclick='delReminder(${r.id})'>Xoá</button>
      </td>
    </tr>`;
  }
  document.getElementById('remindersTbl').innerHTML = html;
}

async function pickReminder(id){
  const rows = await api('/api/reminders');
  const r = rows.find(x=>x.id===id); if(!r) return;
  edit.reminderId=id;
  rTitle.value=r.title||''; rTarget.value=r.target_id; rTime.value=r.daily_time||'08:00'; rTz.value=r.timezone||'Asia/Ho_Chi_Minh'; rRetry.value=r.retry_interval_min||30;
  rAck.value=r.ack_text||'ok đã xong'; rNeedAck.checked=!!r.require_date_ack; rActive.checked=!!r.active; rMsg.value=r.message_template||'';
}

async function saveReminder(){
  const body = {
    id: edit.reminderId,
    title: rTitle.value.trim(),
    target_id: Number(rTarget.value),
    daily_time: rTime.value || '08:00',
    timezone: rTz.value.trim() || 'Asia/Ho_Chi_Minh',
    retry_interval_min: Number(rRetry.value||30),
    require_date_ack: rNeedAck.checked?1:0,
    ack_text: (rAck.value||'').trim() || 'ok',
    active: rActive.checked?1:0,
    message_template: rMsg.value.trim()
  };
  if(!body.title || !body.target_id) return alert('Thiếu tên nhắc hẹn hoặc người nhận');
  await api('/api/reminders', {method:'POST', body: JSON.stringify(body)});
  edit.reminderId=null; rTitle.value=''; rMsg.value=''; rTime.value='08:00'; rTz.value='Asia/Ho_Chi_Minh'; rRetry.value=30; rAck.value='ok đã xong'; rNeedAck.checked=true; rActive.checked=true;
  await refreshAll();
}

async function delReminder(id){ if(!confirm('Xoá nhắc hẹn #'+id+'?')) return; await api('/api/reminders/'+id,{method:'DELETE'}); await refreshAll(); }
async function sendNow(id){ await api('/api/reminders/'+id+'/send-now',{method:'POST'}); await loadLogs(); alert('Đã chạy gửi thử. Xem log phía dưới.'); }
async function ackToday(id){ await api('/api/reminders/'+id+'/ack-today',{method:'POST'}); await loadLogs(); alert('Đã xác nhận hôm nay.'); }

async function loadLogs(){
  const rows = await api('/api/logs?limit=200');
  let html = '<tr><th>Thời gian</th><th>Loại</th><th>Reminder</th><th>Người nhận</th><th>Nội dung/Lỗi</th></tr>';
  for(const r of rows){
    html += `<tr>
      <td class='mono'>${esc(r.created_at)}</td>
      <td>${esc(r.event_type)}</td>
      <td>${esc(r.reminder_title||'')}</td>
      <td>${esc(r.target_name||'')}</td>
      <td>${esc((r.message_text||r.error_text||'').slice(0,200))}</td>
    </tr>`;
  }
  document.getElementById('logsTbl').innerHTML = html;
}

async function refreshAll(){
  try {
    await refreshSystem();
    await loadAccounts();
    await loadTargets();
    await loadReminders();
    await loadLogs();
  } catch(e){ alert(e.message); }
}

refreshAll();
setInterval(()=>{ loadLogs().catch(()=>{}); refreshSystem().catch(()=>{}); }, 30000);
</script>
</body>
</html>
"""


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS accounts (
                  account_id TEXT PRIMARY KEY,
                  name TEXT,
                  zca_profile TEXT NOT NULL DEFAULT 'default',
                  self_id TEXT,
                  enabled INTEGER NOT NULL DEFAULT 1,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS targets (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  phone TEXT,
                  thread_id TEXT NOT NULL UNIQUE,
                  account_id TEXT NOT NULL DEFAULT 'default',
                  is_group INTEGER NOT NULL DEFAULT 0,
                  active INTEGER NOT NULL DEFAULT 1,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  FOREIGN KEY(account_id) REFERENCES accounts(account_id)
                );

                CREATE TABLE IF NOT EXISTS reminders (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  target_id INTEGER NOT NULL,
                  message_template TEXT,
                  daily_time TEXT NOT NULL DEFAULT '08:00',
                  timezone TEXT NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
                  retry_interval_min INTEGER NOT NULL DEFAULT 30,
                  require_date_ack INTEGER NOT NULL DEFAULT 1,
                  ack_text TEXT NOT NULL DEFAULT 'ok',
                  start_date TEXT,
                  active INTEGER NOT NULL DEFAULT 1,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  FOREIGN KEY(target_id) REFERENCES targets(id)
                );

                CREATE TABLE IF NOT EXISTS daily_acks (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  reminder_id INTEGER NOT NULL,
                  ack_date TEXT NOT NULL,
                  source_text TEXT,
                  created_at TEXT NOT NULL,
                  UNIQUE(reminder_id, ack_date)
                );

                CREATE TABLE IF NOT EXISTS logs (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  created_at TEXT NOT NULL,
                  event_type TEXT NOT NULL,
                  account_id TEXT,
                  reminder_id INTEGER,
                  target_id INTEGER,
                  local_date TEXT,
                  message_text TEXT,
                  error_text TEXT,
                  raw_json TEXT
                );

                CREATE TABLE IF NOT EXISTS ack_baselines (
                  reminder_id INTEGER NOT NULL,
                  local_date TEXT NOT NULL,
                  user_ok_count INTEGER NOT NULL DEFAULT 0,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  PRIMARY KEY(reminder_id, local_date)
                );
                """
            )
            now = utc_now_iso()
            row = c.execute("SELECT account_id FROM accounts WHERE account_id='default'").fetchone()
            if not row:
                c.execute(
                    "INSERT INTO accounts(account_id,name,zca_profile,enabled,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                    ("default", "Default", "default", 1, now, now),
                )

            # lightweight migration for old DBs
            cols = [r["name"] for r in c.execute("PRAGMA table_info(reminders)").fetchall()]
            if "ack_text" not in cols:
                c.execute("ALTER TABLE reminders ADD COLUMN ack_text TEXT NOT NULL DEFAULT 'ok'")
                c.execute("UPDATE reminders SET ack_text='ok' WHERE ack_text IS NULL OR TRIM(ack_text)='' ")
            if "start_date" not in cols:
                c.execute("ALTER TABLE reminders ADD COLUMN start_date TEXT")

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.lock, self._conn() as c:
            cur = c.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    def execute(self, sql: str, params: tuple = ()):
        with self.lock, self._conn() as c:
            c.execute(sql, params)
            c.commit()

    def upsert_account(self, payload: Dict[str, Any]):
        now = utc_now_iso()
        with self.lock, self._conn() as c:
            c.execute(
                """
                INSERT INTO accounts(account_id,name,zca_profile,enabled,created_at,updated_at)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(account_id) DO UPDATE SET
                  name=excluded.name,
                  zca_profile=excluded.zca_profile,
                  enabled=excluded.enabled,
                  updated_at=excluded.updated_at
                """,
                (
                    payload["account_id"],
                    payload.get("name", ""),
                    payload.get("zca_profile", "default") or "default",
                    int(payload.get("enabled", 1)),
                    now,
                    now,
                ),
            )
            c.commit()

    def set_account_self_id(self, account_id: str, self_id: str):
        self.execute("UPDATE accounts SET self_id=?, updated_at=? WHERE account_id=?", (self_id, utc_now_iso(), account_id))

    def delete_account(self, account_id: str):
        if account_id == "default":
            raise ValueError("Không xoá account default")
        in_use = self.query("SELECT 1 FROM targets WHERE account_id=? LIMIT 1", (account_id,))
        if in_use:
            raise ValueError("Account đang được dùng bởi người nhận")
        self.execute("DELETE FROM accounts WHERE account_id=?", (account_id,))

    def upsert_target(self, payload: Dict[str, Any]):
        now = utc_now_iso()
        with self.lock, self._conn() as c:
            if payload.get("id"):
                c.execute(
                    """
                    UPDATE targets SET name=?, phone=?, thread_id=?, account_id=?, is_group=?, active=?, updated_at=? WHERE id=?
                    """,
                    (
                        payload["name"],
                        payload.get("phone", ""),
                        payload["thread_id"],
                        payload.get("account_id", "default"),
                        int(payload.get("is_group", 0)),
                        int(payload.get("active", 1)),
                        now,
                        int(payload["id"]),
                    ),
                )
            else:
                c.execute(
                    """
                    INSERT INTO targets(name,phone,thread_id,account_id,is_group,active,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        payload["name"],
                        payload.get("phone", ""),
                        payload["thread_id"],
                        payload.get("account_id", "default"),
                        int(payload.get("is_group", 0)),
                        int(payload.get("active", 1)),
                        now,
                        now,
                    ),
                )
            c.commit()

    def delete_target(self, target_id: int):
        in_use = self.query("SELECT 1 FROM reminders WHERE target_id=? LIMIT 1", (target_id,))
        if in_use:
            raise ValueError("Người nhận đang gắn với reminder")
        self.execute("DELETE FROM targets WHERE id=?", (target_id,))

    def upsert_reminder(self, payload: Dict[str, Any]):
        now = utc_now_iso()
        tz_name = payload.get("timezone", APP_TZ) or APP_TZ
        daily_time = payload.get("daily_time", DEFAULT_DAILY_TIME) or DEFAULT_DAILY_TIME
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo(APP_TZ)
        now_local = datetime.now(timezone.utc).astimezone(tz)
        h, m = parse_hhmm(daily_time)
        trigger_today = now_local.replace(hour=h, minute=m, second=0, microsecond=0)
        # If schedule time already passed at save-time, first run starts next day.
        start_date = (now_local.date() + timedelta(days=1) if now_local > trigger_today else now_local.date()).isoformat()

        with self.lock, self._conn() as c:
            if payload.get("id"):
                c.execute(
                    """
                    UPDATE reminders SET title=?, target_id=?, message_template=?, daily_time=?, timezone=?, retry_interval_min=?, require_date_ack=?, ack_text=?, start_date=?, active=?, updated_at=?
                    WHERE id=?
                    """,
                    (
                        payload["title"],
                        int(payload["target_id"]),
                        payload.get("message_template", ""),
                        daily_time,
                        tz_name,
                        int(payload.get("retry_interval_min", DEFAULT_RETRY_MIN)),
                        int(payload.get("require_date_ack", 1)),
                        (payload.get("ack_text") or DEFAULT_ACK_TEXT).strip() or DEFAULT_ACK_TEXT,
                        start_date,
                        int(payload.get("active", 1)),
                        now,
                        int(payload["id"]),
                    ),
                )
            else:
                c.execute(
                    """
                    INSERT INTO reminders(title,target_id,message_template,daily_time,timezone,retry_interval_min,require_date_ack,ack_text,start_date,active,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        payload["title"],
                        int(payload["target_id"]),
                        payload.get("message_template", ""),
                        daily_time,
                        tz_name,
                        int(payload.get("retry_interval_min", DEFAULT_RETRY_MIN)),
                        int(payload.get("require_date_ack", 1)),
                        (payload.get("ack_text") or DEFAULT_ACK_TEXT).strip() or DEFAULT_ACK_TEXT,
                        start_date,
                        int(payload.get("active", 1)),
                        now,
                        now,
                    ),
                )
            c.commit()

    def delete_reminder(self, reminder_id: int):
        self.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))

    def get_accounts(self):
        return self.query("SELECT * FROM accounts ORDER BY account_id")

    def get_targets(self):
        return self.query("SELECT * FROM targets ORDER BY id DESC")

    def get_reminders(self):
        return self.query(
            """
            SELECT r.*, t.name as target_name, t.phone as phone, t.thread_id as thread_id, t.account_id as account_id, t.is_group as is_group
            FROM reminders r
            JOIN targets t ON t.id=r.target_id
            ORDER BY r.id DESC
            """
        )

    def get_active_reminders(self):
        return self.query(
            """
            SELECT r.*, t.name as target_name, t.phone as phone, t.thread_id as thread_id, t.account_id as account_id, t.is_group as is_group
            FROM reminders r
            JOIN targets t ON t.id=r.target_id
            WHERE r.active=1 AND t.active=1
            """
        )

    def get_reminder_by_id(self, reminder_id: int):
        rows = self.query(
            """
            SELECT r.*, t.name as target_name, t.phone as phone, t.thread_id as thread_id, t.account_id as account_id, t.is_group as is_group
            FROM reminders r JOIN targets t ON t.id=r.target_id WHERE r.id=?
            """,
            (reminder_id,),
        )
        return rows[0] if rows else None

    def add_log(
        self,
        event_type: str,
        account_id: Optional[str] = None,
        reminder_id: Optional[int] = None,
        target_id: Optional[int] = None,
        local_date: Optional[str] = None,
        message_text: Optional[str] = None,
        error_text: Optional[str] = None,
        raw_json: Optional[Dict[str, Any]] = None,
    ):
        self.execute(
            "INSERT INTO logs(created_at,event_type,account_id,reminder_id,target_id,local_date,message_text,error_text,raw_json) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                utc_now_iso(),
                event_type,
                account_id,
                reminder_id,
                target_id,
                local_date,
                message_text,
                error_text,
                json.dumps(raw_json, ensure_ascii=False) if raw_json is not None else None,
            ),
        )

    def list_logs(self, limit: int = 200):
        return self.query(
            """
            SELECT l.*, r.title as reminder_title, t.name as target_name
            FROM logs l
            LEFT JOIN reminders r ON r.id=l.reminder_id
            LEFT JOIN targets t ON t.id=l.target_id
            ORDER BY l.id DESC LIMIT ?
            """,
            (limit,),
        )

    def is_acked(self, reminder_id: int, local_date: str) -> bool:
        rows = self.query("SELECT 1 FROM daily_acks WHERE reminder_id=? AND ack_date=? LIMIT 1", (reminder_id, local_date))
        return bool(rows)

    def ack(self, reminder_id: int, local_date: str, source_text: str = ""):
        with self.lock, self._conn() as c:
            c.execute(
                "INSERT OR IGNORE INTO daily_acks(reminder_id,ack_date,source_text,created_at) VALUES (?,?,?,?)",
                (reminder_id, local_date, source_text, utc_now_iso()),
            )
            c.commit()

    def last_send_at(self, reminder_id: int, local_date: str, event_type: str = "send") -> Optional[datetime]:
        rows = self.query(
            "SELECT created_at FROM logs WHERE reminder_id=? AND event_type=? AND local_date=? ORDER BY id DESC LIMIT 1",
            (reminder_id, event_type, local_date),
        )
        if not rows:
            return None
        try:
            return parse_iso(rows[0]["created_at"])
        except Exception:
            return None

    def get_ack_baseline(self, reminder_id: int, local_date: str) -> Optional[int]:
        rows = self.query("SELECT user_ok_count FROM ack_baselines WHERE reminder_id=? AND local_date=?", (reminder_id, local_date))
        return int(rows[0]["user_ok_count"]) if rows else None

    def set_ack_baseline(self, reminder_id: int, local_date: str, user_ok_count: int):
        now = utc_now_iso()
        self.execute(
            """
            INSERT INTO ack_baselines(reminder_id,local_date,user_ok_count,created_at,updated_at)
            VALUES (?,?,?,?,?)
            ON CONFLICT(reminder_id,local_date) DO UPDATE SET
              user_ok_count=excluded.user_ok_count,
              updated_at=excluded.updated_at
            """,
            (reminder_id, local_date, int(user_ok_count), now, now),
        )

    def was_ack_confirmed_today(self, reminder_id: int, local_date: str) -> bool:
        rows = self.query(
            "SELECT 1 FROM logs WHERE reminder_id=? AND event_type='ack_confirm_send' AND local_date=? LIMIT 1",
            (reminder_id, local_date),
        )
        return bool(rows)


@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    code: int


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _parse_date_token(token: str) -> Optional[datetime.date]:
    token = (token or "").strip()
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", token)
    if m:
        d, mo, y = map(int, m.groups())
        try:
            return datetime(y, mo, d).date()
        except ValueError:
            return None

    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", token)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            return datetime(y, mo, d).date()
        except ValueError:
            return None

    return None


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def ack_matches(text: str, ack_text: str, today_local: datetime.date) -> bool:
    t = normalize_text(text)
    if not t:
        return False

    token = (ack_text or DEFAULT_ACK_TEXT).strip()
    if not token:
        token = DEFAULT_ACK_TEXT

    token_norm = normalize_text(token)
    token_today = normalize_text(token.replace("{date}", today_local.strftime("%d/%m/%Y")))
    token_today_iso = normalize_text(token.replace("{date}", today_local.isoformat()))

    if t in {token_norm, token_today, token_today_iso}:
        return True

    # backward compatibility: accept "<date> đã xong"
    m = re.fullmatch(r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\s+(đã xong|da xong)", t)
    if not m:
        return False
    d = _parse_date_token(m.group(1))
    return d == today_local


def parse_hhmm(value: str):
    try:
        h, m = value.split(":")
        return int(h), int(m)
    except Exception:
        return 8, 0


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)


def run_cmd(cmd: List[str], timeout: int = 35, env: Optional[Dict[str, str]] = None) -> RunResult:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=merged)
        return RunResult(ok=(p.returncode == 0), stdout=(p.stdout or "").strip(), stderr=(p.stderr or "").strip(), code=p.returncode)
    except subprocess.TimeoutExpired as e:
        return RunResult(ok=False, stdout=_to_text(e.stdout).strip(), stderr=(_to_text(e.stderr).strip() or "Timeout"), code=124)


class ReminderEngine:
    def __init__(self, store: Store):
        self.store = store
        self.stop_event = threading.Event()
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.listener_threads: Dict[str, threading.Thread] = {}
        self.listener_stops: Dict[str, threading.Event] = {}

    def start(self):
        self.scheduler_thread.start()
        self.reload_listeners()

    def stop(self):
        self.stop_event.set()
        for ev in self.listener_stops.values():
            ev.set()

    def reload_listeners(self):
        accounts = [a for a in self.store.get_accounts() if int(a.get("enabled", 1)) == 1]
        wanted = {a["account_id"]: a for a in accounts}

        for acc_id in list(self.listener_stops.keys()):
            if acc_id not in wanted:
                self.listener_stops[acc_id].set()
                del self.listener_stops[acc_id]
                self.listener_threads.pop(acc_id, None)

        for acc in accounts:
            acc_id = acc["account_id"]
            if acc_id in self.listener_threads and self.listener_threads[acc_id].is_alive():
                continue
            ev = threading.Event()
            t = threading.Thread(target=self.listener_loop, args=(acc_id, acc["zca_profile"], ev), daemon=True)
            self.listener_stops[acc_id] = ev
            self.listener_threads[acc_id] = t
            t.start()

    def refresh_self_id(self, account_id: str):
        acc_rows = [a for a in self.store.get_accounts() if a["account_id"] == account_id]
        if not acc_rows:
            raise ValueError("Account không tồn tại")
        profile = acc_rows[0]["zca_profile"]
        res = run_cmd([ZCA_BIN, "--profile", profile, "me", "id"], timeout=15)
        if not res.ok:
            raise RuntimeError(res.stderr or res.stdout or "Không lấy được self id")
        self_id = (res.stdout or "").strip().splitlines()[-1].strip()
        if not self_id:
            raise RuntimeError("Self id rỗng")
        self.store.set_account_self_id(account_id, self_id)

    def system_status(self) -> Dict[str, Any]:
        license_res = run_cmd([ZCA_BIN, "license", "status"], timeout=15)
        license_ok = license_res.ok and ("active" in (license_res.stdout or "").lower() or "valid" in (license_res.stdout or "").lower())

        auth_res = run_cmd([ZCA_BIN, "auth", "status"], timeout=8)
        # zca auth status currently can hang in some versions; timeout still indicates we got text.
        auth_text = f"{auth_res.stdout}\n{auth_res.stderr}".lower()
        authenticated = "logged in" in auth_text and "not logged in" not in auth_text

        return {
            "licenseOk": bool(license_ok),
            "authenticated": bool(authenticated),
            "licenseRaw": (license_res.stdout or license_res.stderr)[:500],
            "authRaw": (auth_res.stdout or auth_res.stderr)[:500],
            "openclawBin": OPENCLAW_BIN,
            "zcaBin": ZCA_BIN,
            "defaultProfile": "default",
        }

    def listener_loop(self, account_id: str, profile: str, stop: threading.Event):
        backoff_sec = 15
        while not stop.is_set() and not self.stop_event.is_set():
            env = os.environ.copy()
            env["ZCA_PROFILE"] = profile
            try:
                proc = subprocess.Popen(
                    [ZCA_BIN, "--profile", profile, "listen", "-r", "-k", "--events", "message"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    bufsize=1,
                )
            except Exception as e:
                self.store.add_log("listener_error", account_id=account_id, error_text=str(e))
                time.sleep(backoff_sec)
                backoff_sec = min(300, backoff_sec * 2)
                continue

            err_thread = threading.Thread(target=self._drain_stderr, args=(proc, account_id), daemon=True)
            err_thread.start()

            had_event = False
            try:
                while not stop.is_set() and proc.poll() is None:
                    line = proc.stdout.readline() if proc.stdout else ""
                    if not line:
                        time.sleep(0.1)
                        continue
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except Exception:
                        continue
                    had_event = True
                    self.handle_inbound(account_id, payload)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except Exception:
                        proc.kill()

            if had_event:
                backoff_sec = 15

            if not stop.is_set() and not self.stop_event.is_set():
                self.store.add_log("listener_restart", account_id=account_id, error_text=f"Listener restarted in {backoff_sec}s")
                time.sleep(backoff_sec)
                backoff_sec = min(300, backoff_sec * 2)

    def _drain_stderr(self, proc: subprocess.Popen, account_id: str):
        if not proc.stderr:
            return
        for line in proc.stderr:
            txt = (line or "").strip()
            if txt:
                self.store.add_log("listener_stderr", account_id=account_id, error_text=txt[:1000])

    def handle_inbound(self, account_id: str, payload: Dict[str, Any]):
        thread_id = str(payload.get("threadId") or payload.get("thread_id") or "").strip()
        content = str(payload.get("content") or payload.get("message") or "").strip()
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        from_id = str(metadata.get("fromId") or payload.get("fromId") or "").strip()

        self.store.add_log("inbound", account_id=account_id, message_text=content[:500], raw_json=payload)

        if not thread_id or not content:
            return

        accounts = {a["account_id"]: a for a in self.store.get_accounts()}
        self_id = (accounts.get(account_id) or {}).get("self_id")
        if self_id and from_id and from_id == self_id:
            return

        reminders = self.store.query(
            """
            SELECT r.*, t.thread_id, t.phone, t.account_id, t.id as target_id
            FROM reminders r JOIN targets t ON t.id=r.target_id
            WHERE r.active=1 AND t.active=1 AND t.thread_id=? AND t.account_id=? AND r.require_date_ack=1
            """,
            (thread_id, account_id),
        )

        for r in reminders:
            tz_name = r.get("timezone") or APP_TZ
            try:
                now_local = datetime.now(timezone.utc).astimezone(ZoneInfo(tz_name))
            except Exception:
                now_local = datetime.now(timezone.utc).astimezone(ZoneInfo(APP_TZ))
            today_local = now_local.date()

            if ack_matches(content, str(r.get("ack_text") or DEFAULT_ACK_TEXT), today_local):
                local_date = today_local.isoformat()
                self.store.ack(int(r["id"]), local_date, content)
                self.store.add_log(
                    "ack",
                    account_id=account_id,
                    reminder_id=int(r["id"]),
                    target_id=int(r["target_id"]),
                    local_date=local_date,
                    message_text=content[:500],
                    raw_json=payload,
                )
                self.send_ack_confirmation(r, local_date)

    def send_ack_confirmation(self, reminder: Dict[str, Any], local_date: str):
        reminder_id = int(reminder["id"])
        if self.store.was_ack_confirmed_today(reminder_id, local_date):
            return
        target_id = int(reminder["target_id"])
        account_id = reminder.get("account_id") or "default"
        thread_id = str(reminder.get("thread_id") or "")
        phone = (reminder.get("phone") or "").strip()
        is_group = int(reminder.get("is_group", 0)) == 1

        body = f"✅ Đã nhận xác nhận. Em sẽ dừng nhắc trong hôm nay ({local_date})."

        result: RunResult
        if phone and Path(ZALO_SEND_SH).exists():
            result = run_cmd(["bash", ZALO_SEND_SH, phone, body], timeout=90)
        else:
            profile = "default"
            acc = [a for a in self.store.get_accounts() if a["account_id"] == account_id]
            if acc:
                profile = acc[0].get("zca_profile") or "default"

            cmd = [ZCA_BIN, "--profile", profile, "msg", "send", str(thread_id), body]
            if is_group:
                cmd.insert(-2, "--group")
            result = run_cmd(cmd, timeout=45)

            if not result.ok:
                fallback_cmd = [OPENCLAW_BIN, "message", "send", "--channel", "zalouser", "--target", str(thread_id), "--message", body, "--account", account_id]
                result = run_cmd(fallback_cmd, timeout=45)

        if result.ok:
            self.store.add_log(
                "ack_confirm_send",
                account_id=account_id,
                reminder_id=reminder_id,
                target_id=target_id,
                local_date=local_date,
                message_text=body,
                raw_json={"stdout": result.stdout[:1000]},
            )
        else:
            self.store.add_log(
                "ack_confirm_error",
                account_id=account_id,
                reminder_id=reminder_id,
                target_id=target_id,
                local_date=local_date,
                message_text=body,
                error_text=(result.stderr or result.stdout or "Send failed")[:1000],
            )

    def check_desktop_ack(self, reminder: Dict[str, Any], local_date: str) -> tuple[bool, int]:
        phone = (reminder.get("phone") or "").strip()
        if not phone or not Path(ZALO_CHECK_ACK_SH).exists():
            return (False, 0)
        ack_text = (str(reminder.get("ack_text") or DEFAULT_ACK_TEXT).strip() or DEFAULT_ACK_TEXT)
        rr = run_cmd(["bash", ZALO_CHECK_ACK_SH, phone, ack_text], timeout=90)
        out = f"{rr.stdout}\n{rr.stderr}".lower()
        found = rr.ok and ("ack_found=1" in out)
        user_ok_count = 0
        m = re.search(r"user_ok_count=(\d+)", out)
        if m:
            user_ok_count = int(m.group(1))
        self.store.add_log(
            "ack_probe",
            account_id=reminder.get("account_id") or "default",
            reminder_id=int(reminder["id"]),
            target_id=int(reminder["target_id"]),
            local_date=local_date,
            message_text=(rr.stdout or "")[:500],
            error_text=(rr.stderr or "")[:500],
        )
        return (found, user_ok_count)

    def scheduler_loop(self):
        while not self.stop_event.is_set():
            try:
                self.run_scheduler_tick()
            except Exception as e:
                self.store.add_log("scheduler_error", error_text=str(e))
            time.sleep(20)

    def run_scheduler_tick(self):
        reminders = self.store.get_active_reminders()
        for r in reminders:
            reminder_id = int(r["id"])
            tz_name = r.get("timezone") or APP_TZ
            try:
                tz = ZoneInfo(tz_name)
            except Exception:
                tz = ZoneInfo(APP_TZ)
            now_local = datetime.now(timezone.utc).astimezone(tz)
            local_date = now_local.date().isoformat()

            h, m = parse_hhmm(r.get("daily_time") or DEFAULT_DAILY_TIME)
            trigger = now_local.replace(hour=h, minute=m, second=0, microsecond=0)
            start_date = (r.get("start_date") or "").strip()
            if start_date and local_date < start_date:
                continue
            if now_local < trigger:
                continue

            if int(r.get("require_date_ack", 1)) == 1 and self.store.is_acked(reminder_id, local_date):
                continue

            retry_min = max(1, int(r.get("retry_interval_min", DEFAULT_RETRY_MIN)))
            last_scheduled = self.store.last_send_at(reminder_id, local_date, event_type="send")

            if last_scheduled is None or last_scheduled.astimezone(tz) < trigger:
                # First scheduled send of the current window: send first, then set baseline OK-count.
                self.send_reminder(r, reason="scheduled")
                if int(r.get("require_date_ack", 1)) == 1:
                    _, ok_count = self.check_desktop_ack(r, local_date)
                    self.store.set_ack_baseline(reminder_id, local_date, ok_count)
                continue

            # Desktop-only ACK detection path with baseline guard (avoid matching old "ok").
            if int(r.get("require_date_ack", 1)) == 1:
                found, ok_count = self.check_desktop_ack(r, local_date)
                baseline = self.store.get_ack_baseline(reminder_id, local_date)
                if baseline is None:
                    self.store.set_ack_baseline(reminder_id, local_date, ok_count)
                    baseline = ok_count

                if found and ok_count > baseline:
                    self.store.ack(reminder_id, local_date, "desktop-ack-detected")
                    self.store.add_log(
                        "ack",
                        account_id=r.get("account_id") or "default",
                        reminder_id=reminder_id,
                        target_id=int(r["target_id"]),
                        local_date=local_date,
                        message_text=f"desktop-ack-detected (ok_count={ok_count}, baseline={baseline})",
                    )
                    self.send_ack_confirmation(r, local_date)
                    continue

            delta = datetime.now(timezone.utc) - last_scheduled.astimezone(timezone.utc)
            if delta >= timedelta(minutes=retry_min):
                self.send_reminder(r, reason="scheduled")

    def send_reminder(self, reminder: Dict[str, Any], reason: str = "manual") -> RunResult:
        reminder_id = int(reminder["id"])
        target_id = int(reminder["target_id"])
        account_id = reminder.get("account_id") or "default"
        thread_id = reminder.get("thread_id")
        is_group = int(reminder.get("is_group", 0)) == 1

        if not thread_id:
            rr = RunResult(False, "", "Thiếu thread_id", 1)
            self.store.add_log("error", account_id=account_id, reminder_id=reminder_id, target_id=target_id, error_text=rr.stderr)
            return rr

        tz_name = reminder.get("timezone") or APP_TZ
        try:
            now_local = datetime.now(timezone.utc).astimezone(ZoneInfo(tz_name))
        except Exception:
            now_local = datetime.now(timezone.utc).astimezone(ZoneInfo(APP_TZ))
        local_date = now_local.date().isoformat()
        date_text = now_local.strftime("%d/%m/%Y")

        ack_text = (str(reminder.get("ack_text") or DEFAULT_ACK_TEXT).strip() or DEFAULT_ACK_TEXT)
        ack_hint = ack_text.replace("{date}", date_text)
        default_msg = (
            f"[{reminder.get('title','Nhắc hẹn')}]\n"
            f"Hôm nay ({date_text}) nhớ thực hiện việc đã hẹn.\n"
            f"Vui lòng phản hồi để em dừng nhắc trong hôm nay."
        )
        body = (reminder.get("message_template") or "").strip() or default_msg
        if "xác nhận hôm nay" not in body.lower() and "xac nhan hom nay" not in body.lower():
            body += "\n\nXác nhận hôm nay: (reply theo cú pháp đã thống nhất)"

        # Prefer local desktop Zalo send flow (human-like UI automation) when phone is available.
        phone = (reminder.get("phone") or "").strip()
        result: RunResult
        if phone and Path(ZALO_SEND_SH).exists():
            result = run_cmd(["bash", ZALO_SEND_SH, phone, body], timeout=90)
        else:
            # Fallback to zca / channel transport
            profile = "default"
            acc = [a for a in self.store.get_accounts() if a["account_id"] == account_id]
            if acc:
                profile = acc[0].get("zca_profile") or "default"

            cmd = [ZCA_BIN, "--profile", profile, "msg", "send", str(thread_id), body]
            if is_group:
                cmd.insert(-2, "--group")
            result = run_cmd(cmd, timeout=45)

            if not result.ok:
                fallback_cmd = [OPENCLAW_BIN, "message", "send", "--channel", "zalouser", "--target", str(thread_id), "--message", body, "--account", account_id]
                result = run_cmd(fallback_cmd, timeout=45)

        if result.ok:
            event_type = "send" if reason == "scheduled" else "send_manual"
            self.store.add_log(
                event_type,
                account_id=account_id,
                reminder_id=reminder_id,
                target_id=target_id,
                local_date=local_date,
                message_text=body,
                raw_json={"reason": reason, "stdout": result.stdout[:1000]},
            )
        else:
            self.store.add_log(
                "error",
                account_id=account_id,
                reminder_id=reminder_id,
                target_id=target_id,
                local_date=local_date,
                message_text=body,
                error_text=(result.stderr or result.stdout or "Send failed")[:1000],
                raw_json={"reason": reason},
            )
        return result


class Handler(BaseHTTPRequestHandler):
    engine: ReminderEngine = None  # type: ignore
    store: Store = None  # type: ignore

    def _send_json(self, data: Any, code: int = 200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str, code: int = 200):
        raw = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> Dict[str, Any]:
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n <= 0:
            return {}
        raw = self.rfile.read(n)
        return json.loads(raw.decode("utf-8")) if raw else {}

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path
        qs = parse_qs(p.query)
        try:
            if path == "/":
                return self._send_html(INDEX_HTML)
            if path == "/api/health":
                return self._send_json({"ok": True, "time": utc_now_iso()})
            if path == "/api/system/status":
                return self._send_json(self.engine.system_status())
            if path == "/api/accounts":
                return self._send_json(self.store.get_accounts())
            if path == "/api/targets":
                return self._send_json(self.store.get_targets())
            if path == "/api/reminders":
                return self._send_json(self.store.get_reminders())
            if path == "/api/logs":
                limit = int((qs.get("limit") or ["200"])[0])
                return self._send_json(self.store.list_logs(max(1, min(1000, limit))))
            return self._send_json({"error": "Not found"}, 404)
        except Exception as e:
            return self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        p = urlparse(self.path)
        path = p.path
        try:
            if path == "/api/accounts":
                body = self._read_json()
                if not body.get("account_id"):
                    return self._send_json({"error": "Thiếu account_id"}, 400)
                self.store.upsert_account(body)
                self.engine.reload_listeners()
                return self._send_json({"ok": True})

            if path.startswith("/api/accounts/") and path.endswith("/refresh-self-id"):
                account_id = path.split("/")[3]
                self.engine.refresh_self_id(account_id)
                return self._send_json({"ok": True})

            if path == "/api/targets":
                body = self._read_json()
                if not body.get("name") or not body.get("thread_id"):
                    return self._send_json({"error": "Thiếu name hoặc thread_id"}, 400)
                self.store.upsert_target(body)
                return self._send_json({"ok": True})

            if path == "/api/reminders":
                body = self._read_json()
                if not body.get("title") or not body.get("target_id"):
                    return self._send_json({"error": "Thiếu title hoặc target_id"}, 400)
                self.store.upsert_reminder(body)
                return self._send_json({"ok": True})

            if path.startswith("/api/reminders/") and path.endswith("/send-now"):
                reminder_id = int(path.split("/")[3])
                r = self.store.get_reminder_by_id(reminder_id)
                if not r:
                    return self._send_json({"error": "Reminder không tồn tại"}, 404)
                rr = self.engine.send_reminder(r, reason="manual")
                return self._send_json({"ok": rr.ok, "stdout": rr.stdout, "stderr": rr.stderr, "code": rr.code})

            if path.startswith("/api/reminders/") and path.endswith("/ack-today"):
                reminder_id = int(path.split("/")[3])
                r = self.store.get_reminder_by_id(reminder_id)
                if not r:
                    return self._send_json({"error": "Reminder không tồn tại"}, 404)
                tz_name = r.get("timezone") or APP_TZ
                try:
                    now_local = datetime.now(timezone.utc).astimezone(ZoneInfo(tz_name))
                except Exception:
                    now_local = datetime.now(timezone.utc).astimezone(ZoneInfo(APP_TZ))
                self.store.ack(reminder_id, now_local.date().isoformat(), "manual-ack")
                self.store.add_log("ack", account_id=r.get("account_id"), reminder_id=reminder_id, target_id=int(r["target_id"]), local_date=now_local.date().isoformat(), message_text="manual-ack")
                return self._send_json({"ok": True})

            return self._send_json({"error": "Not found"}, 404)
        except Exception as e:
            return self._send_json({"error": str(e)}, 500)

    def do_DELETE(self):
        p = urlparse(self.path)
        path = p.path
        try:
            if path.startswith("/api/accounts/"):
                account_id = path.split("/")[3]
                self.store.delete_account(account_id)
                self.engine.reload_listeners()
                return self._send_json({"ok": True})
            if path.startswith("/api/targets/"):
                target_id = int(path.split("/")[3])
                self.store.delete_target(target_id)
                return self._send_json({"ok": True})
            if path.startswith("/api/reminders/"):
                reminder_id = int(path.split("/")[3])
                self.store.delete_reminder(reminder_id)
                return self._send_json({"ok": True})
            return self._send_json({"error": "Not found"}, 404)
        except Exception as e:
            return self._send_json({"error": str(e)}, 500)


def main():
    store = Store(DB_PATH)
    engine = ReminderEngine(store)
    engine.start()

    Handler.engine = engine
    Handler.store = store
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Zalo Reminder Manager chạy tại http://{HOST}:{PORT}")
    print(f"DB: {DB_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()
        server.server_close()


if __name__ == "__main__":
    main()
