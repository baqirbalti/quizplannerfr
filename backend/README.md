# AI Skill Bridge - Quiz Planner

[![Deployed on Vercel](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)](https://vercel.com)
[![Backend on Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?logo=railway)](https://railway.app)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)

> A modern, AI-powered quiz enrollment system for Pakistan's First Fully-Funded AI Bootcamp featuring automated quiz generation, video evaluation, and intelligent selection.

---

## 📘 Overview

**AI Skill Bridge Quiz Planner** streamlines candidate enrollment and evaluation for AI bootcamps through automation and intelligent analysis.

**Core Highlights:**

* Personalized AI-generated quizzes
* Secure email delivery with tokenized links
* Time-bound quiz sessions
* Automated video transcription and feedback
* AI-driven candidate scoring and selection

---

## ✨ Features

### Candidate Experience

* 🎓 Choose topics (Python, Generative AI, LLMs, etc.)
* 📧 Receive quiz links securely via email
* ⏱️ Take a timed 10-minute quiz
* 🎥 Upload or submit YouTube videos
* 📊 Get instant score feedback

### Admin Tools

* 🤖 AI quiz generation via Google Gemini
* 📝 Backup question templates
* 🎙️ Automatic transcription using Whisper
* 💬 AI-based video evaluation via GPT
* ☁️ Optional AWS S3 integration for videos

---

## 🧰 Tech Stack

### Frontend

* **Next.js 15.5.4 (React 19)**
* **Tailwind CSS v4**
* **TypeScript**, **React Hook Form**, **Chart.js**
* **Deployed on Vercel**

### Backend

* **FastAPI 0.118.0 (Python 3.11)**
* **Gemini 1.5 Flash** & **GPT-4o-mini** integration
* **OpenAI Whisper** for transcription
* **SMTP Email Delivery**, optional **S3 Storage**
* **Deployed on Railway**

---

## 🏗️ Architecture Diagram

```
Frontend (Next.js)
│
├── Enrollment, Quiz, Results, Video Submission
│
▼
Backend (FastAPI)
├── Quiz Generation (Gemini)
├── Evaluation (OpenAI)
├── Video Processing (Whisper)
├── Email Delivery (SMTP)
└── Storage (Local / AWS S3)
```

**Data Flow Summary:**

1. User enrolls → Quiz generated → Email sent
2. User takes quiz → Answers scored (≥70% pass)
3. User submits video → Whisper + GPT evaluation
4. Final selection (quiz + video ≥70)

---

## 🚀 Getting Started

### Requirements

* Node.js ≥20
* Python ≥3.11
* API keys for Gemini, OpenAI, SMTP (optional)

### Backend Setup

```bash
git clone <repo>
cd quizplanner_02/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

Visit: `http://localhost:3000`

---

## 🔐 Environment Variables

| Key                    | Description           | Default                                        |
| ---------------------- | --------------------- | ---------------------------------------------- |
| GEMINI_API_KEY         | Google Gemini API key | -                                              |
| OPENAI_API_KEY         | OpenAI API key        | -                                              |
| SMTP_HOST              | SMTP server           | smtp.gmail.com                                 |
| SMTP_USER / SMTP_PASS  | Email credentials     | -                                              |
| FRONTEND_ORIGIN        | CORS origin           | [http://localhost:3000](http://localhost:3000) |
| SECRET_KEY             | Security token        | change-me                                      |
| QUIZ_TOKEN_TTL_SECONDS | Token expiry (s)      | 259200                                         |
| AWS_S3_BUCKET          | Optional S3 storage   | -                                              |

Frontend `.env.local`:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

---

## 📡 API Overview

**POST /generate_quiz** → Generates and emails quiz
**POST /submit_quiz** → Grades answers
**POST /submit_video / submit_video_url** → Analyzes candidate videos
**GET /final_result/{quiz_id}** → Returns combined score
**POST /resend_quiz_email** → Re-sends quiz link

---

## 📁 Folder Structure

```
quizplanner_02/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Procfile
│   └── uploads/
├── frontend/
│   ├── src/app/
│   │   ├── enroll/, quiz/, result/, video/, final/
│   ├── package.json
│   └── next.config.ts
└── README.md
```

---

## 🌍 Deployment

### Backend (Railway)

1. Connect repo → select `backend` folder
2. Add environment variables
3. Deploy automatically

### Frontend (Vercel)

1. Import repo → select `frontend`
2. Add `NEXT_PUBLIC_API_BASE=https://your-backend-url`
3. Deploy automatically

**Checklist:**

* Update CORS + base URLs
* Test email + AI services
* Enable S3 in production
* Use strong secret key

---

## 🧠 AI Evaluation Pipeline

**Step 1:** Quiz generated using Gemini → 70% threshold

**Step 2:** Video evaluated via Whisper (transcription) + GPT (scoring)

**Step 3:** Combined score determines selection.

---

## 🧩 Development Commands

```bash
# Tests
pytest  # backend
npm test  # frontend

# Linting
npm run lint

# Build production
npm run build && npm start
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Commit & push
4. Open Pull Request

---

## 📄 License

MIT License © AI Skill Bridge Team

---

### 💬 Contact

* Email: [contact@aiskillbridge.pk](mailto:contact@aiskillbridge.pk)
* Website: [https://aiskillbridge.pk](https://aiskillbridge.pk)
* GitHub: [AI Skill Bridge](https://github.com/your-username/quizplanner)

---

<div align="center">
<strong>Built with ❤️ for Pakistan's First Fully-Funded AI Bootcamp</strong><br>
<sub>Empowering the next generation of AI engineers</sub>
</div>
