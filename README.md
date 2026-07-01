# Senari.uz Bot

Telegram bot — tayyor ssenariylar katalogi, xarid, avtomatik yetkazib berish, premium, admin panel.

## Stack
aiogram 3.x · SQLAlchemy 2 (async) · PostgreSQL · Redis · FastAPI (Click webhook) · Docker · Nginx

## Ishga tushirish (lokal)
```bash
cp .env.example .env          # BOT_TOKEN, ADMIN_IDS to'ldiring
docker compose up -d db redis
docker compose run --rm bot alembic revision --autogenerate -m "init"
docker compose run --rm bot alembic upgrade head
docker compose run --rm bot python -m app.seed   # test ma'lumotlari
docker compose up -d bot web
```

## Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
# SSL (birinchi marta):
docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.uz
```

## Backup
`deploy/backup.sh` — kunlik pg_dump, 14 kun saqlaydi. Cron: `0 3 * * * /opt/senari/deploy/backup.sh`

## Imkoniyatlar
- ✅ Ro'yxatdan o'tish (kontakt orqali), uz/ru/en
- ✅ Katalog (16 kategoriya), paginatsiya, qidiruv
- ✅ To'lov: Telegram Stars + Click (FastAPI webhook, signature tekshiruvi)
- ✅ Avtomatik fayl yetkazish (file_id keshlash)
- ✅ Mening xaridlarim (qayta yuklash)
- ✅ Premium (1/3/6/12 oy), referal, promo kod, sevimlilar, reyting
- ✅ Admin panel (/admin): ssenariy qo'shish, fayl/rasm yuklash, statistika
- ✅ Audit log, backup, CI/CD

## Struktura
```
app/
  handlers/    start, catalog, payment, purchases, premium, admin
  services/    delivery, click, audit
  repositories/ user, catalog, purchase, stats, premium
  keyboards/   common, catalog
  models/      ORM (User, Scenario, Payment, Premium, Promo, Review, Favorite, AuditLog...)
  web.py       FastAPI webhooks
  main.py      bot entry
deploy/        nginx.conf, backup.sh, certbot
.github/       CI/CD
```
