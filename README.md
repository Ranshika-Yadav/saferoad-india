# SafeRoad India — Enhanced Demo

## Local setup

Requires Python 3.10+; no pip dependencies.

```bash
export ADMIN_TOKEN="replace-with-a-long-random-secret"
python server.py
```

Open http://localhost:8000 and http://localhost:8000/admin.html. Never commit the token.

## Render deployment

Create a **Web Service** using Python.
- Build command: `echo "No dependencies"`
- Start command: `python server.py`
- Environment: `ADMIN_TOKEN` = a strong random secret (Render dashboard only).
- For SQLite persistence: attach a paid persistent disk and set `SAFEROAD_DB=/var/data/saferoad.db`. Without a persistent disk, Render's local database may disappear on redeploy/restart. For production, migrate to managed PostgreSQL.
- Python standard library only; no requirements.txt required.

## Included features

Responsive homepage, guides, five-question quiz, Hindi toggle for key headings, road hazard submissions, campaign interest forms, volunteer and contact forms, pledge saving and printable certificate, downloadable text resources, admin token login, submission management, CSV export, privacy notice.

## Important limitations before public launch

This is a **demonstration**, not an emergency reporting service or official road authority. No email notifications or real scheduled campaigns are configured. Hindi translation covers key headings only. No public map/geocoding or photo uploads. Add a complete legal privacy policy, organization identity, retention policy, admin contact, accessible Hindi translation, stronger anti-abuse protections, HTTPS, backups and a production database before collecting real personal data. Admin token is a single shared secret; use proper user authentication for a public production service. The certificate is an acknowledgement, not an official credential.
