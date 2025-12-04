#  QUICK START GUIDE - BSport System

##  CÁC CÁCH CHẠY HỆ THỐNG

Có 3 cách chạy hệ thống, tùy thuộc bạn có dùng Ngrok hay không:

---

##  OPTION 1: CHẠY VỚI STATIC NGROK DOMAIN (KHUYẾN NGHỊ)

> **Lợi ích**: Domain không đổi, chỉ config 1 lần duy nhất

### Lần đầu tiên (Setup):

```bash
# 1. Claim static domain tại: https://dashboard.ngrok.com/cloud-edge/domains
# Ví dụ: bsport-app.ngrok-free.dev

# 2. Config authtoken (lấy từ https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken YOUR_AUTHTOKEN

# 3. Update domain trong script
nano start_with_static_ngrok.sh
# Sửa dòng: STATIC_NGROK_DOMAIN="bsport-app.ngrok-free.dev"

# 4. Update config hệ thống (CHỈ 1 LẦN)
./update_ngrok_url.sh https://bsport-app.ngrok-free.dev
./rebuild_fixed_services.sh
```

### Mỗi lần chạy (sau khi tắt máy):

```bash
# CHỈ CẦN 1 COMMAND:
./start_with_static_ngrok.sh

# Script sẽ tự động:
# ✓ Start Docker Compose
# ✓ Verify config
# ✓ Start Ngrok với static domain
# ✓ Không cần update config lại!
```

**Access**: `https://bsport-app.ngrok-free.dev/ui/Homepage/homepage.html`

---

##  OPTION 2: CHẠY VỚI RANDOM NGROK DOMAIN (Auto Update)

> **Lưu ý**: Domain thay đổi mỗi lần restart, nhưng script tự động update

### Mỗi lần chạy:

```bash
# CHỈ CẦN 1 COMMAND:
./start_with_random_ngrok.sh

# Script sẽ tự động:
# ✓ Start Docker Compose
# ✓ Start Ngrok (random domain)
# ✓ Detect ngrok URL
# ✓ Update config files
# ✓ Rebuild services

# Ngrok URL sẽ được hiển thị sau khi xong
```

**Access**: URL sẽ được hiển thị trong console output

---

##  OPTION 3: CHẠY LOCALHOST (KHÔNG NGROK)

> **Lưu ý**: Payment callback từ SePay sẽ KHÔNG hoạt động

```bash
# Start Docker Compose
docker-compose up -d

# Access local
open http://localhost/ui/Homepage/homepage.html
```

**Access**: `http://localhost/ui/Homepage/homepage.html`

---

##  CHI TIẾT CÁC FILE CONFIG

### File cần config Ngrok domain:

1. **`Billing/core/.env`** (Backend):
   ```env
   BACKEND_PUBLIC_URL=https://your-domain.ngrok-free.dev
   FRONTEND_URL=https://your-domain.ngrok-free.dev/ui
   ```

2. **`UI/Homepage/homepage.html`** (Frontend):
   ```javascript
   window.CONFIG = {
       BACKEND_PUBLIC_URL: 'https://your-domain.ngrok-free.dev',
       ...
   }
   ```

---

##  SAU KHI TẮT MÁY VÀ MỞ LẠI

### Với Static Domain:
```bash
# Chỉ cần chạy:
./start_with_static_ngrok.sh

#  Config không đổi, không cần update!
```

### Với Random Domain:
```bash
# Chỉ cần chạy:
./start_with_random_ngrok.sh

#  Script tự động detect & update config!
```

### Localhost only:
```bash
docker-compose up -d
```

---

##  TROUBLESHOOTING

###  Domain ngrok đổi nhưng config chưa update:
```bash
# Update manual:
./update_ngrok_url.sh https://new-domain.ngrok-free.dev
./rebuild_fixed_services.sh
```

###  Services không apply config mới:
```bash
# Restart services:
docker-compose restart billing_api nginx

# Hoặc rebuild:
./rebuild_fixed_services.sh
```

###  Frontend vẫn gọi localhost:
```bash
# Clear browser cache: Ctrl+Shift+R
# Hoặc dùng Incognito mode
```

###  Payment callback không về:
```bash
# Check config:
cat Billing/core/.env | grep BACKEND_PUBLIC_URL

# Rebuild billing:
docker-compose up -d --build billing_api
```

---

##  VERIFY HỆ THỐNG

```bash
# 1. Check Docker services
docker-compose ps

# 2. Check ngrok
curl https://your-domain.ngrok-free.dev/health \
  -H "ngrok-skip-browser-warning: true"

# 3. View ngrok traffic
open http://localhost:4040

# 4. Check logs
docker-compose logs -f billing_api
```

---

##  CHECKLIST

- [ ] Docker đã start: `docker info`
- [ ] Ngrok đã install: `ngrok version`
- [ ] Config đã update: `cat Billing/core/.env | grep BACKEND`
- [ ] Services đã rebuild: `docker-compose ps`
- [ ] Health check OK: `curl https://your-domain.ngrok-free.dev/health`
- [ ] Frontend load được: Mở browser test

---

##  TÀI LIỆU CHI TIẾT

- **Ngrok Setup**: `NGROK_SETUP_GUIDE.md`
- **API Documentation**: `YEU_CAU_3_DANH_SACH_API.md`
- **System README**: `README.txt`

---

##  KHUYẾN NGHỊ

1.  **Dùng Static Domain** cho development lâu dài
2.  **Dùng Auto Script** (`start_with_static_ngrok.sh`) để tiết kiệm thời gian
3.  **Monitor logs** khi test payment: `docker-compose logs -f billing_api`
4.  **Dùng ngrok inspector** (http://localhost:4040) để debug requests
5.  **KHÔNG share** ngrok URL publicly (có thể access toàn bộ localhost)

---

**Last Updated**: 27/11/2025  
**Version**: 1.0
