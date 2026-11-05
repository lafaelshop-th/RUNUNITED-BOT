# Discord Shop Bot + Web Dashboard

## Setup

1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill:
   - Discord Bot Token + Public Key (from Developer Portal)
   - PostgreSQL DATABASE_URL
   - SECRET_KEY (long random)
   - Generate password/PIN hashes with passlib for DEV_*
4. Create DB and run (tables auto-create on start)
5. `cd backend && python main.py` or `uvicorn backend.main:app --host 0.0.0.0 --port 8000`

## Discord Interactions Endpoint

- In Discord Developer Portal → General Information → Interactions Endpoint URL
- Set to `https://yourdomain.com/interactions`
- Save. Bot will respond to PING automatically.

## External APIs required

- **TrueMoney Wallet Angpao**: Unofficial API (search "truemoney voucher api" or similar community endpoints). Receiver phone in settings. Auto-verify amount + recipient + ref, prevent double-use. Fallback to admin approve if API fails.
- **PromptPay / Slip verification**: SlipOK, EasySlip, or bank API. Verify amount, receiver, transaction ID. Never trust QR detection alone. Store unique refs.
- **Discord**: Bot token, Public Key for signature verify (mandatory every interaction).
- **Optional**: Image upload storage (local or S3), Webhook for admin notifications.

## Core flows implemented / to expand

- User register/login (bcrypt, JWT cookie)
- Board create + verify message link → real Discord message update with Action Rows separate from embeds
- Products: categories (id_game / rental / code_file), stock, delivery data, image/GIF link or upload
- Buy: check credit + stock, deduct both atomically, log purchase, DM delivery, webhook admin
- Credit topup: TrueMoney / PromptPay + slip, admin approve path, webhook on approve
- Packages: custom days, trial 3d once per account (not IP-only), extend from current expiry, hard stop on expire
- Codes: create/edit/delete, expiry, reward types, single-use
- Status page: online/offline, remaining time, errors
- Developer: extra PIN/password layer, view/delete connections, manage users/credits/transactions
- Security: Discord signature on every interaction, rate limit, no secrets in frontend, ORM (no raw SQL), CSRF on forms, password hash

## Testing checklist (run before production)

- Add credit via admin → check-info board shows exact DB value
- Buy product → credit deducted, stock -1, purchase logged, DM sent
- Clear stock / delete product with confirms
- Connect board via endpoint → status shows online + ping
- Package expire → board stops responding
- Duplicate slip / code rejected
- Expired package blocks usage

## Deploy

- Use PM2 / systemd / Docker for continuous run
- Nginx reverse proxy + SSL
- PostgreSQL managed or self-hosted
- Environment variables only, never commit .env
- Monitor logs + webhook on errors

## Notes

Buttons are Action Row components, embeds separate. All data from DB, no mocks. Multi-shop by guild + verified message link. Web editor for title/desc/image/GIF/buttons with live preview that updates Discord message on confirm.

TrueMoney angpao API details: provide the endpoint + auth you want used and it will be wired in.
