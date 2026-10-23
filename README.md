# ACE BANK — Simulated Employee Portal

A Streamlit demo of a commercial-banking employee portal. **ACE BANK is fictional**; all 15 account holders, account numbers and transactions are synthetic and generated deterministically (same data every run).

## Features
- Employee login (demo credentials below)
- Search commercial account holders by 12-digit account number, or pick from the directory
- Account profile card + 30-day activity KPIs
- Statement for any date range (presets or custom, from 1 Apr 2025 to today)
- Download as **PDF** (branded, watermarked "SIMULATED") or **CSV**

## Demo logins
| Employee ID | Password |
|---|---|
| EMP1001 | Ace@2026 |
| EMP1002 | Ace@2026 |
| ADMIN | Admin@123 |

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy free on Streamlit Community Cloud
1. Create a GitHub repo and push this folder (`app.py`, `requirements.txt`, `.streamlit/config.toml`, `README.md`) to its root.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Pick the repo, branch `main`, main file path `app.py`. Optionally set a custom subdomain (e.g. `ace-bank-demo`).
5. Click **Deploy**. First build takes 2–3 minutes.

### Optional: change logins without editing code
In the app's **Settings → Secrets** on Streamlit Cloud, paste:
```toml
[employees.EMP2001]
password = "YourPassword"
name = "Your Name"
role = "Relationship Manager"
branch = "Mumbai – BKC"
```
If secrets are set, they replace the built-in demo logins.

## Customising
- Add/rename accounts: edit the `COMPANIES` list in `app.py`.
- Change history start date: `DATA_START` in `app.py`.
