# จดโดเมน + ชี้มาที่เซิร์ฟเวอร์

## 1. จดโดเมน
- ไปที่ registrar ไทย: https://www.thnic.co.th หรือ Namecheap / Cloudflare Registrar / GoDaddy
- ค้นหาโดเมนที่ต้องการ (เช่น shopboard.th หรือ .com)
- จ่ายเงิน จด 1 ปี
- เปิดบัญชี Cloudflare (ฟรี) แล้วเพิ่มโดเมน → เปลี่ยน nameserver ตามที่ Cloudflare ให้

## 2. ชี้โดเมนมาที่เซิร์ฟเวอร์
- ใน Cloudflare DNS เพิ่ม A record:
  - Name: @ หรือ www
  - IPv4: IP ของเซิร์ฟเวอร์จริง (ไม่ใช่ sandbox นี้)
  - Proxy: เปิด (orange cloud) หรือปิดตามต้องการ
- รอ propagate 5-30 นาที

## 3. SSL
- Cloudflare เปิด SSL/TLS mode = Full (strict) หรือ Flexible
- หรือใช้ Certbot บนเซิร์ฟเวอร์: `certbot --nginx`

## 4. รันเซิร์ฟเวอร์ถาวร
บนเครื่องจริง (VPS):
```bash
# ติดตั้ง postgres + สร้าง db
sudo apt install postgresql
sudo -u postgres createdb discord_shop
# ตั้ง DATABASE_URL ใน .env เป็น postgresql://...
# รันด้วย systemd หรือ pm2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name shopbot
```

## 5. Discord Interactions Endpoint
ใน Discord Developer Portal → General Information
ใส่: https://yourdomain.com/interactions
กด Save → บอทจะตอบ PING อัตโนมัติ

## หมายเหตุ
Sandbox นี้รันได้แค่ชั่วคราวบน SQLite. ต้องย้ายไป VPS จริงเพื่อใช้ PostgreSQL และโดเมนสาธารณะ.
TrueMoney / PromptPay API ยังรอ endpoint จาก Sam.
