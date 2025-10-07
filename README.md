# AI Skill Bridge - Quiz Planner

[![Deployed on Vercel](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)](https://vercel.com)
[![Backend on Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?logo=railway)](https://railway.app)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)

> A modern, AI-powered quiz enrollment system for Pakistan's First Fully-Funded AI Bootcamp with automated quiz generation, video submission, and intelligent candidate evaluation.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

AI Skill Bridge Quiz Planner is a comprehensive enrollment system designed to streamline the candidate selection process for AI bootcamps. The platform features:

- **Personalized Quiz Generation**: AI-powered MCQ generation based on user-selected topics
- **Email Delivery**: Automated quiz link distribution via SMTP
- **Time-Bound Assessments**: 10-minute timed quizzes with real-time countdown
- **Video Evaluation**: Support for both file uploads and YouTube video submissions
- **AI-Powered Analysis**: Automated transcript generation and candidate evaluation using OpenAI Whisper and GPT models
- **Smart Selection**: Two-phase evaluation (70% quiz pass threshold + 70/100 video score)

## ✨ Features

### For Candidates
- 🎓 **Topic Selection**: Choose from various topics (Python, Generative AI, LLMs, etc.)
- 📧 **Email Link Flow**: Secure quiz access via personalized email links
- ⏱️ **Timed Quiz**: 10-minute countdown timer with automatic submission
- 🎥 **Flexible Video Submission**: Upload video files or submit YouTube links
- 📊 **Instant Results**: Immediate feedback with score breakdown
- 🔐 **Secure Tokens**: Signed JWT-style tokens for quiz persistence

### For Administrators
- 🤖 **AI Quiz Generation**: Google Gemini integration for intelligent question generation
- 📝 **Fallback System**: Template-based question generation when API is unavailable
- 🎙️ **Automated Transcription**: OpenAI Whisper for video-to-text conversion
- 💬 **AI Feedback**: GPT-powered candidate evaluation with numeric scoring
- 📈 **Analytics Ready**: Structured data storage for future analytics
- ☁️ **Cloud Storage**: Optional S3 integration for video uploads

## 🛠️ Tech Stack

### Frontend
- **Framework**: [Next.js 15.5.4](https://nextjs.org) with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Form Handling**: React Hook Form + Zod validation
- **Charts**: Chart.js with react-chartjs-2
- **Icons**: Lucide React
- **Deployment**: Vercel

### Backend
- **Framework**: [FastAPI 0.118.0](https://fastapi.tiangolo.com)
- **Language**: Python 3.11.9
- **Server**: Uvicorn with standard dependencies
- **AI Services**:
  - Google Generative AI (Gemini 1.5 Flash)
  - OpenAI GPT-4o-mini (for feedback & transcription)
- **Video Processing**:
  - OpenAI Whisper (transcription)
  - YouTube Transcript API
- **Storage**: 
  - In-memory storage (MVP)
  - Optional AWS S3 integration
- **Email**: SMTP with TLS/SSL support
- **Deployment**: Railway

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  - Landing Page                  - Quiz Interface            │
│  - Enrollment Form               - Result Dashboard          │
│  - Video Submission              - Final Results             │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Quiz Gen   │  │   Evaluate   │  │ Video Proc.  │      │
│  │   (Gemini)   │  │  (OpenAI)    │  │  (Whisper)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ In-Memory DB │  │  SMTP Email  │  │   S3 Store   │      │
│  │   (dicts)    │  │  Delivery    │  │  (Optional)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Enrollment**: User fills form → Backend generates quiz via Gemini → Email sent with secure link
2. **Quiz Taking**: User clicks link → Token validated → Questions loaded → Timed assessment
3. **Submission**: Answers submitted → Scored (70% pass threshold) → Results stored
4. **Video Phase**: Video uploaded/URL submitted → Whisper transcription → GPT evaluation
5. **Final Decision**: Combined score (quiz pass + video ≥70) → Selection result

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **API Keys** (optional for full functionality):
  - Google Gemini API Key
  - OpenAI API Key
  - SMTP credentials
  - AWS S3 (optional)

### Backend Setup

1. **Clone and navigate**:
   ```bash
   git clone <repository-url>
   cd quizplanner_02/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (create `.env` file):
   ```env
   # API Keys
   GEMINI_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key
   
   # SMTP Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=your-app-password
   SMTP_FROM=noreply@aiskillbridge.pk
   
   # Frontend URLs
   FRONTEND_ORIGIN=http://localhost:3000
   FRONTEND_BASE_URL=http://localhost:3000
   
   # Security
   SECRET_KEY=your-secret-key-change-in-production
   QUIZ_TOKEN_TTL_SECONDS=259200  # 3 days
   
   # Optional: S3 Storage
   AWS_S3_BUCKET=your-bucket-name
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   ```

5. **Run the server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   API will be available at `http://localhost:8000`
   Interactive docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (create `.env.local` file):
   ```env
   NEXT_PUBLIC_API_BASE=http://localhost:8000
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

   App will be available at `http://localhost:3000`

## 🔐 Environment Variables

### Backend (`.env`)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for quiz generation | No | Fallback templates |
| `GEMINI_MODEL` | Gemini model name | No | `gemini-1.5-flash` |
| `OPENAI_API_KEY` | OpenAI key for transcription & feedback | No | Fallback responses |
| `OPENAI_QUESTIONS_MODEL` | Model for questions (if used) | No | `gpt-4o-mini` |
| `OPENAI_FEEDBACK_MODEL` | Model for video feedback | No | `gpt-4o-mini` |
| `SMTP_HOST` | SMTP server hostname | No | Logs only |
| `SMTP_PORT` | SMTP port | No | `587` |
| `SMTP_SSL_PORT` | SSL fallback port | No | `465` |
| `SMTP_USER` | SMTP username | No | - |
| `SMTP_PASS` | SMTP password | No | - |
| `SMTP_FROM` | From email address | No | SMTP_USER |
| `FRONTEND_ORIGIN` | CORS origin | No | `http://localhost:3000` |
| `FRONTEND_BASE_URL` | Base URL for email links | No | `http://localhost:3000` |
| `SECRET_KEY` | Token signing secret | Yes | `dev-secret-change-me` |
| `QUIZ_TOKEN_TTL_SECONDS` | Token expiry time | No | `259200` (3 days) |
| `AWS_S3_BUCKET` | S3 bucket for videos | No | Local storage |
| `AWS_REGION` | AWS region | No | - |

### Frontend (`.env.local`)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_BASE` | Backend API URL | Yes | `http://localhost:8000` |

## 📡 API Documentation

### Core Endpoints

#### `POST /generate_quiz`
Generate a new quiz and send email with link.

**Request**:
```json
{
  "email": "candidate@example.com",
  "topic": "Generative AI",
  "num_questions": 10
}
```

**Response**:
```json
{
  "quiz_id": "quiz_1759557216680",
  "questions": [...],
  "expires_in_seconds": 3600,
  "quiz_url": "https://app.com/quiz/quiz_123?t=...",
  "email_queued": true
}
```

#### `GET /quiz/{quiz_id}?t={token}`
Retrieve quiz questions (supports token-based recovery).

#### `POST /submit_quiz`
Submit quiz answers for grading.

**Request**:
```json
{
  "quiz_id": "quiz_123",
  "answers": [0, 2, 1, 3, ...]
}
```

**Response**:
```json
{
  "quiz_id": "quiz_123",
  "score": 8,
  "total": 10,
  "passed": true,
  "suggestions": ["Great work! Prepare a concise project walkthrough..."]
}
```

#### `POST /submit_video`
Upload video file for analysis.

**Form Data**:
- `quiz_id`: string
- `file`: video file

#### `POST /submit_video_url`
Submit YouTube video URL for analysis.

**Request**:
```json
{
  "quiz_id": "quiz_123",
  "youtube_url": "https://youtube.com/watch?v=..."
}
```

#### `GET /final_result/{quiz_id}`
Get combined quiz + video evaluation result.

**Response**:
```json
{
  "quiz_id": "quiz_123",
  "passed_quiz": true,
  "selected": true,
  "feedback": "Strong fundamentals; consider deeper examples...",
  "video_score": 85
}
```

#### `POST /resend_quiz_email`
Resend quiz link to email.

**Request**:
```json
{
  "quiz_id": "quiz_123",
  "email": "candidate@example.com"
}
```

For full API documentation, visit `/docs` on your running backend instance.

## 📁 Project Structure

```
quizplanner_02/
├── backend/
│   ├── main.py                 # FastAPI application & all routes
│   ├── requirements.txt        # Python dependencies
│   ├── runtime.txt            # Python version for Railway
│   ├── Procfile               # Railway deployment config
│   ├── .env                   # Environment variables (not in git)
│   └── uploads/               # Local video storage
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx           # Landing page
│   │       ├── layout.tsx         # Root layout
│   │       ├── globals.css        # Global styles
│   │       ├── api/
│   │       │   └── config.ts      # API base URL config
│   │       ├── about/
│   │       │   └── page.tsx       # About page
│   │       ├── enroll/
│   │       │   └── page.tsx       # Quiz enrollment form
│   │       ├── quiz/
│   │       │   └── [quizId]/
│   │       │       └── page.tsx   # Quiz taking interface
│   │       ├── result/
│   │       │   └── [quizId]/
│   │       │       └── page.tsx   # Quiz results
│   │       ├── video/
│   │       │   └── [quizId]/
│   │       │       └── page.tsx   # Video submission
│   │       └── final/
│   │           └── [quizId]/
│   │               └── page.tsx   # Final selection result
│   ├── package.json           # npm dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── next.config.ts         # Next.js config
│   ├── tailwind.config.ts     # Tailwind CSS config
│   └── .env.local            # Frontend environment (not in git)
│
└── README.md                  # This file
```

## 🚢 Deployment

### Backend Deployment (Railway)

1. **Connect Repository**:
   - Sign in to [Railway](https://railway.app)
   - Create new project from GitHub repo
   - Select `backend` as root directory

2. **Configure Environment**:
   - Add all required environment variables from the [Environment Variables](#environment-variables) section
   - Railway auto-detects `Procfile` and `runtime.txt`

3. **Deploy**:
   - Railway automatically builds and deploys on push to main branch
   - Get your production URL (e.g., `https://quizplannerfr-production.up.railway.app`)

### Frontend Deployment (Vercel)

1. **Import Project**:
   - Sign in to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Select `frontend` as root directory

2. **Configure Build**:
   - Framework Preset: Next.js
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)

3. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE=https://your-backend-url.railway.app
   ```

4. **Deploy**:
   - Vercel auto-deploys on every push to main
   - Get your production URL (e.g., `https://quizplannerfr.vercel.app`)

### Post-Deployment Checklist

- [ ] Update `FRONTEND_BASE_URL` in backend environment
- [ ] Update `FRONTEND_ORIGIN` for CORS
- [ ] Test email delivery end-to-end
- [ ] Verify AI services (Gemini, OpenAI) are working
- [ ] Test video upload and transcription
- [ ] Enable S3 for production video storage
- [ ] Set strong `SECRET_KEY` for production
- [ ] Monitor logs and error tracking

## 📸 Screenshots

### 1. Email Notification
Candidates receive a personalized quiz link via email:

![Email with Quiz Link](docs/email-notification.png)

*Automated email delivery with secure, token-based quiz links*

---

### 2. Landing Page
Modern, responsive homepage with clear call-to-action:

![Homepage](C:\Users\baqir\OneDrive\Pictures\Screenshots\Screenshot 2025-10-07 181231.png)

*Dark-themed UI with hero section, features, and testimonials*

---

### 3. Quiz Enrollment
Simple form to generate personalized quizzes:

![Enrollment Form](docs/enrollment-form.png)

*Users enter email, select topic, and choose number of questions*

---

### 4. Deployment Dashboard
Production-ready infrastructure:

**Frontend (Vercel)**:
![Vercel Deployment](docs/vercel-deployment.png)

**Backend (Railway)**:
![Railway Deployment](docs/railway-deployment.png)

---

## 🎯 Key Features Explained

### Intelligent Quiz Generation

The system uses **Google Gemini AI** to generate contextually relevant MCQs based on the user's selected topic. The AI is instructed to:
- Create diverse, non-repetitive questions
- Ensure clear correct answers with plausible distractors
- Maintain topic relevance
- Format output as strict JSON for reliability

**Fallback System**: If Gemini API is unavailable, a sophisticated template-based generator creates varied questions using:
- Multiple question templates
- Randomized distractor pools
- Topic-contextualized options
- Balanced difficulty distribution

### Secure Token-Based Access

Quiz links include signed tokens (JWT-style HMAC-SHA256) that:
- Encode quiz metadata (ID, topic, questions count, email)
- Have configurable expiration (default: 3 days)
- Enable quiz recovery after server restarts
- Prevent unauthorized access

### Two-Phase Evaluation

**Phase 1 - Knowledge Assessment**:
- Multiple-choice questions (configurable 1-30)
- 70% passing threshold
- Immediate feedback with suggestions

**Phase 2 - Skills Demonstration**:
- Video submission (file or YouTube URL)
- Automatic transcription via OpenAI Whisper
- AI-powered evaluation (clarity, depth, relevance)
- Numeric score 0-100

**Final Selection**: `selected = (quiz_passed AND video_score >= 70)`

### Production-Ready Features

- **CORS Handling**: Full preflight request support
- **Error Recovery**: Graceful API fallbacks throughout
- **Responsive Design**: Mobile-first Tailwind CSS
- **Type Safety**: Full TypeScript + Pydantic validation
- **Cloud Storage**: S3 integration for scalable video storage
- **Email Resilience**: STARTTLS with SSL fallback

## 🔧 Development

### Running Tests

```bash
# Backend (add pytest to requirements.txt)
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Linting

```bash
# Frontend
npm run lint
```

### Building for Production

```bash
# Frontend
npm run build
npm start

# Backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AI Skill Bridge Team** - Project concept and requirements
- **Jarify** - UI/UX Design
- **Google Gemini** - AI-powered quiz generation
- **OpenAI** - Transcription and evaluation services
- **Vercel & Railway** - Hosting and deployment infrastructure

## 📞 Contact

For questions or support:
- **Email**: contact@aiskillbridge.pk
- **Website**: [https://aiskillbridge.pk](https://aiskillbridge.pk)
- **Repository**: [GitHub](https://github.com/your-username/quizplanner)

---

<div align="center">
  <strong>Built with ❤️ for Pakistan's First Fully-Funded AI Bootcamp</strong>
  <br>
  <sub>Empowering the next generation of AI engineers</sub>
</div>

