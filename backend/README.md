# AI Skill Bridge Backend

Run locally:

```bash
.\.venv\Scripts\python -m uvicorn main:app --reload --port 8000
```

Environment variables:

- FRONTEND_ORIGIN: CORS origin (default http://localhost:3000)

Endpoints:

- POST `/generate_quiz`
- GET `/quiz/{quiz_id}`
- POST `/submit_quiz`
- GET `/quiz_result/{quiz_id}`
- POST `/submit_video`
- GET `/final_result/{quiz_id}`

## Email (SMTP) Setup

The backend can email the quiz link to the user after quiz generation. Configure SMTP via environment variables.

Required env vars:

- SMTP_HOST (e.g., `smtp.gmail.com`)
- SMTP_PORT (default `587`)
- SMTP_USER (your email)
- SMTP_PASS (password or app password)
- SMTP_FROM (optional display from, defaults to `SMTP_USER`)
- FRONTEND_BASE_URL (e.g., `http://localhost:3000`)

### Gmail (Recommended via App Password)
1. Enable 2‑Step Verification on your Google Account.
2. Create an App Password: Google Account → Security → App passwords → Select “Mail” and “Windows Computer”.
3. Use the generated 16‑character app password as `SMTP_PASS`.

Example configuration (Windows PowerShell):

```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="your_gmail@gmail.com"
$env:SMTP_PASS="your_app_password_here"
$env:SMTP_FROM="AI Skill Bridge <your_gmail@gmail.com>"
$env:FRONTEND_BASE_URL="http://localhost:3000"
```

Then start the server in the same shell so it can read these env vars:

```powershell
.\.venv\Scripts\python -m uvicorn main:app --reload --port 8000
```

Notes:
- If SMTP is not configured, the API still works but will not send emails. The response indicates `email_queued: false` and logs the quiz URL for debugging.
- Some providers block username/password SMTP; App Passwords or a provider like SendGrid/Resend is recommended for production.


