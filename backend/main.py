import os
import json
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
try:
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
except Exception:  # pragma: no cover
    YouTubeTranscriptApi = None

try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None
try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None

# Simple in-file storage for MVP; replace with DB via SQLAlchemy
QUIZZES: dict[str, dict] = {}
QUESTIONS: dict[str, list[dict]] = {}
SUBMISSIONS: dict[str, dict] = {}
VIDEO_ANALYSIS: dict[str, dict] = {}


class GenerateQuizRequest(BaseModel):
    email: str
    topic: str
    num_questions: int = Field(ge=1, le=30)


class OptionedQuestion(BaseModel):
    id: str
    text: str
    options: List[str]


class GenerateQuizResponse(BaseModel):
    quiz_id: str
    questions: List[OptionedQuestion]
    expires_in_seconds: int = 60 * 60
    quiz_url: str
    email_queued: bool = False


class SubmitQuizRequest(BaseModel):
    quiz_id: str
    answers: List[int]


class SubmitQuizResponse(BaseModel):
    quiz_id: str
    score: int
    total: int
    passed: bool
    suggestions: List[str]


class FinalResultResponse(BaseModel):
    quiz_id: str
    passed_quiz: bool
    selected: Optional[bool]
    feedback: Optional[str]
    video_score: Optional[int] = None


class SubmitVideoURLRequest(BaseModel):
    quiz_id: str
    youtube_url: str


load_dotenv()

app = FastAPI(title="AI Skill Bridge Backend", version="0.2.0")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

# For local development, allow all origins to avoid CORS/preflight issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/{path:path}")
async def cors_preflight(path: str, request: Request):
    origin = request.headers.get("origin", "*")
    req_method = request.headers.get("access-control-request-method", "*")
    req_headers = request.headers.get("access-control-request-headers", "*")
    resp = Response(status_code=204)
    resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = req_method
    resp.headers["Access-Control-Allow-Headers"] = req_headers or "*"
    resp.headers["Access-Control-Max-Age"] = "600"
    return resp


def _fallback_generate_questions(topic: str, num: int) -> list[dict]:
    """Generate varied placeholder questions without external APIs.

    These are template-based and diversified to avoid repetition when offline.
    """
    question_templates = [
        "Which of the following best describes {topic}?",
        "Which scenario is a common use case for {topic}?",
        "Which statement about {topic} is most accurate?",
        "Which choice is NOT typically related to {topic}?",
        "What is a key benefit of using {topic}?",
        "Which practice aligns with best use of {topic}?",
        "Which pitfall should be avoided when working with {topic}?",
        "Which component is most closely associated with {topic}?",
        "Which metric is most relevant when evaluating {topic}?",
        "Which tool complements {topic} in production?",
    ]

    generic_distractors = [
        "A static website template",
        "A relational database engine",
        "A low-level memory allocator",
        "A general-purpose web framework",
        "A spreadsheet formatting feature",
        "A container orchestration plugin",
        "A graphics rendering filter",
    ]

    benefits = [
        "Improved efficiency and automation",
        "Better scalability under variable loads",
        "Faster prototyping and iteration",
        "Enhanced developer productivity",
        "More consistent outcomes at scale",
    ]

    use_cases = [
        "Summarizing long documents",
        "Automating repetitive workflows",
        "Building intelligent assistants",
        "Retrieving domain knowledge with RAG",
        "Generating structured outputs from prompts",
    ]

    best_practices = [
        "Add guardrails and validations",
        "Use retrieval to ground responses",
        "Evaluate with real-world test sets",
        "Version prompts and track metrics",
        "Cache responses for repeat queries",
    ]

    questions: list[dict] = []
    for i in range(num):
        qid = f"q{i+1}"
        template = random.choice(question_templates)
        text = template.format(topic=topic)

        # Build a diverse option set for each question draw
        bucket = random.choice(["benefit", "use_case", "best_practice", "mixed"])
        if bucket == "benefit":
            correct = random.choice(benefits)
            wrongs = random.sample(generic_distractors, k=3)
        elif bucket == "use_case":
            correct = random.choice(use_cases)
            wrongs = random.sample(generic_distractors, k=3)
        elif bucket == "best_practice":
            correct = random.choice(best_practices)
            wrongs = random.sample(generic_distractors, k=3)
        else:
            # Mixed pool for more variety
            pool = benefits + use_cases + best_practices
            correct = random.choice(pool)
            wrongs = random.sample([x for x in pool + generic_distractors if x != correct], k=3)

        # Insert topic context into one or more wrongs to feel "on-topic"
        wrongs = [w if random.random() > 0.5 else f"{w} (not {topic})" for w in wrongs]

        options = wrongs + [f"{correct} (in context of {topic})"]
        random.shuffle(options)
        correct_index = options.index(next(opt for opt in options if opt.endswith(f"(in context of {topic})")))

        questions.append(
            {
                "id": qid,
                "text": text,
                "options": options,
                "correct_index": correct_index,
            }
        )

    return questions


def _build_quiz_url(quiz_id: str) -> str:
    return f"{frontend_base_url.rstrip('/')}/quiz/{quiz_id}"


def _send_quiz_email_sync(to_email: str, quiz_id: str) -> None:
    """Send the quiz link via SMTP.

    Configure via env: SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASS, SMTP_FROM.
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", user or "no-reply@example.com")

    # If SMTP is not configured, skip silently
    if not host or not user or not password:
        print("[email] SMTP not configured; skipping send")
        if quiz_id in QUIZZES:
            QUIZZES[quiz_id]["email_status"] = {"queued": False, "sent": False, "error": "not_configured"}
        return

    quiz_url = _build_quiz_url(quiz_id)
    msg = EmailMessage()
    msg["Subject"] = "Your AI Skill Bridge Quiz Link"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"Your quiz is ready. Click the link to start: {quiz_url}\n\n"
        "This link opens your personalized enrollment quiz. Good luck!"
    )

    try:
        try:
            with smtplib.SMTP(host, port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user, password)
                server.send_message(msg)
        except Exception as e_starttls:
            # Fallback to SSL (port 465) if STARTTLS path fails
            ssl_port = int(os.getenv("SMTP_SSL_PORT", "465"))
            with smtplib.SMTP_SSL(host, ssl_port, timeout=20) as server_ssl:
                server_ssl.login(user, password)
                server_ssl.send_message(msg)
        print(f"[email] sent quiz link to {to_email} for {quiz_id}")
        if quiz_id in QUIZZES:
            QUIZZES[quiz_id]["email_status"] = {"queued": True, "sent": True, "error": None}
    except Exception as e:
        # Avoid crashing the request path if email fails
        print(f"[email] failed to send: {e}")
        if quiz_id in QUIZZES:
            QUIZZES[quiz_id]["email_status"] = {"queued": True, "sent": False, "error": str(e)}


def _send_quiz_email_status(to_email: str, quiz_id: str) -> dict:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", user or "no-reply@example.com")

    if not host or not user or not password:
        print("[email] SMTP not configured; skipping send")
        return {"queued": False, "sent": False, "error": "not_configured"}

    quiz_url = _build_quiz_url(quiz_id)
    msg = EmailMessage()
    msg["Subject"] = "Your AI Skill Bridge Quiz Link"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"Your quiz is ready. Click the link to start: {quiz_url}\n\n"
        "This link opens your personalized enrollment quiz. Good luck!"
    )

    try:
        try:
            with smtplib.SMTP(host, port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user, password)
                server.send_message(msg)
        except Exception as e_starttls:
            ssl_port = int(os.getenv("SMTP_SSL_PORT", "465"))
            with smtplib.SMTP_SSL(host, ssl_port, timeout=20) as server_ssl:
                server_ssl.login(user, password)
                server_ssl.send_message(msg)
        print(f"[email] sent quiz link to {to_email} for {quiz_id}")
        return {"queued": True, "sent": True, "error": None}
    except Exception as e:
        print(f"[email] failed to send: {e}")
        return {"queued": True, "sent": False, "error": str(e)}


def _generate_questions_with_gemini(topic: str, num: int) -> list[dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    if not api_key or genai is None:
        return _fallback_generate_questions(topic, num)

    genai.configure(api_key=api_key)
    prompt = (
        "Return ONLY valid JSON (no markdown). Schema: {\n"
        "  \"questions\": [ { \"id\": string, \"text\": string, \"options\": [string,string,string,string], \"correct_index\": number } ]\n"
        "}. Topic: "
        f"{topic}. questions length: {num}. Keep options concise and distinct."
    )
    try:
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(prompt)
        text = resp.text or ""
        # Try object with 'questions'
        try:
            obj = json.loads(text)
            arr = obj.get("questions") if isinstance(obj, dict) else None
            if isinstance(arr, list) and arr:
                out: list[dict] = []
                for i, q in enumerate(arr):
                    out.append(
                        {
                            "id": str(q.get("id") or f"q{i+1}"),
                            "text": str(q.get("text") or f"Question about {topic} {i+1}"),
                            "options": list(q.get("options") or ["A", "B", "C", "D"]),
                            "correct_index": int(q.get("correct_index", 0)),
                        }
                    )
                return out
        except Exception:
            pass
        # Fallback: attempt to extract first JSON array in the text
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                arr = json.loads(text[start : end + 1])
                out: list[dict] = []
                for i, q in enumerate(arr):
                    out.append(
                        {
                            "id": str(q.get("id") or f"q{i+1}"),
                            "text": str(q.get("text") or f"Question about {topic} {i+1}"),
                            "options": list(q.get("options") or ["A", "B", "C", "D"]),
                            "correct_index": int(q.get("correct_index", 0)),
                        }
                    )
                return out
            except Exception:
                pass
    except Exception:
        pass
    return _fallback_generate_questions(topic, num)


def _generate_questions_with_openai(topic: str, num: int) -> list[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return _fallback_generate_questions(topic, num)

    try:
        client = OpenAI()
        model = os.getenv("OPENAI_QUESTIONS_MODEL", "gpt-4o-mini")
        prompt = (
            "Return ONLY valid JSON (no markdown). Schema: {\n"
            "  \"questions\": [ { \"id\": string, \"text\": string, \"options\": [string,string,string,string], \"correct_index\": number } ]\n"
            "}. Topic: "
            f"{topic}. questions length: {num}. Keep options concise and distinct."
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = resp.choices[0].message.content or ""
        obj = json.loads(content)
        arr = obj.get("questions") if isinstance(obj, dict) else None
        if isinstance(arr, list) and arr:
            out: list[dict] = []
            for i, q in enumerate(arr):
                out.append(
                    {
                        "id": str(q.get("id") or f"q{i+1}"),
                        "text": str(q.get("text") or f"Question about {topic} {i+1}"),
                        "options": list(q.get("options") or ["A", "B", "C", "D"]),
                        "correct_index": int(q.get("correct_index", 0)),
                    }
                )
            return out
    except Exception:
        pass
    return _fallback_generate_questions(topic, num)


def _extract_youtube_id(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
        if parsed.netloc in {"youtu.be"}:
            return parsed.path.lstrip("/") or None
        if "youtube.com" in parsed.netloc:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]
            # also support /shorts/<id> or /embed/<id>
            parts = [p for p in parsed.path.split("/") if p]
            if parts and parts[0] in {"shorts", "embed"} and len(parts) > 1:
                return parts[1]
        return None
    except Exception:
        return None


@app.post("/generate_quiz", response_model=GenerateQuizResponse)
async def generate_quiz(payload: GenerateQuizRequest, background_tasks: BackgroundTasks):
    quiz_id = f"quiz_{int(datetime.utcnow().timestamp()*1000)}"

    # Enforce role: Gemini only for quiz generation; fallback to local templates if missing
    questions = _generate_questions_with_gemini(payload.topic, payload.num_questions)
    if not questions:
        questions = _fallback_generate_questions(payload.topic, payload.num_questions)

    QUIZZES[quiz_id] = {
        "email": payload.email,
        "topic": payload.topic,
        "num_questions": payload.num_questions,
        "created_at": datetime.utcnow().isoformat(),
    }
    QUESTIONS[quiz_id] = questions

    quiz_url = _build_quiz_url(quiz_id)

    # Queue email only if SMTP config is present
    smtp_configured = bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASS"))
    if smtp_configured:
        background_tasks.add_task(_send_quiz_email_sync, payload.email, quiz_id)
        print(f"[email] queued quiz link to {payload.email}: {quiz_url}")
    else:
        print(f"[email] SMTP not configured; quiz link for {payload.email}: {quiz_url}")

    return GenerateQuizResponse(
        quiz_id=quiz_id,
        questions=[
            OptionedQuestion(id=q["id"], text=q["text"], options=q["options"]) for q in questions
        ],
        quiz_url=quiz_url,
        email_queued=smtp_configured,
    )


class ResendEmailRequest(BaseModel):
    quiz_id: str
    email: str


@app.post("/resend_quiz_email")
async def resend_quiz_email(payload: ResendEmailRequest):
    # Proceed even if in-memory quiz is missing (dev reload clears memory)
    status = _send_quiz_email_status(payload.email, payload.quiz_id)
    if payload.quiz_id in QUIZZES:
        QUIZZES[payload.quiz_id]["email"] = payload.email
        QUIZZES[payload.quiz_id]["email_status"] = status
    return {"ok": True, "status": status}


# Accept trailing slash as well (some clients may append it)
@app.post("/resend_quiz_email/")
async def resend_quiz_email_trailing(payload: ResendEmailRequest):
    status = _send_quiz_email_status(payload.email, payload.quiz_id)
    if payload.quiz_id in QUIZZES:
        QUIZZES[payload.quiz_id]["email"] = payload.email
        QUIZZES[payload.quiz_id]["email_status"] = status
    return {"ok": True, "status": status}


# Optional GET for debugging/manual testing: /resend_quiz_email?quiz_id=...&email=...
@app.get("/resend_quiz_email")
async def resend_quiz_email_get(quiz_id: str, email: str):
    status = _send_quiz_email_status(email, quiz_id)
    if quiz_id in QUIZZES:
        QUIZZES[quiz_id]["email"] = email
        QUIZZES[quiz_id]["email_status"] = status
    return {"ok": True, "status": status}


@app.get("/quiz/{quiz_id}", response_model=GenerateQuizResponse)
async def get_quiz(quiz_id: str):
    if quiz_id not in QUIZZES or quiz_id not in QUESTIONS:
        raise HTTPException(status_code=404, detail="Quiz not found")
    questions = QUESTIONS[quiz_id]
    # Build quiz_url and indicate if email queueing is configured (for info only)
    quiz_url = _build_quiz_url(quiz_id)
    smtp_configured = bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASS"))
    return GenerateQuizResponse(
        quiz_id=quiz_id,
        questions=[
            OptionedQuestion(id=q["id"], text=q["text"], options=q["options"]) for q in questions
        ],
        quiz_url=quiz_url,
        email_queued=smtp_configured,
    )


@app.post("/submit_quiz", response_model=SubmitQuizResponse)
async def submit_quiz(payload: SubmitQuizRequest):
    if payload.quiz_id not in QUESTIONS:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = QUESTIONS[payload.quiz_id]
    if len(payload.answers) != len(questions):
        raise HTTPException(status_code=400, detail="Answers length mismatch")

    score = 0
    for i, q in enumerate(questions):
        if payload.answers[i] == q.get("correct_index", -1):
            score += 1

    total = len(questions)
    passed = score >= max(1, int(0.7 * total))  # 70% threshold

    suggestions = []
    if not passed:
        suggestions.append("Review foundational concepts and practice with targeted exercises.")
    else:
        suggestions.append("Great work! Prepare a concise project walkthrough for the video.")

    SUBMISSIONS[payload.quiz_id] = {
        "answers": payload.answers,
        "score": score,
        "total": total,
        "passed": passed,
    }

    return SubmitQuizResponse(
        quiz_id=payload.quiz_id, score=score, total=total, passed=passed, suggestions=suggestions
    )


@app.get("/quiz_result/{quiz_id}", response_model=SubmitQuizResponse)
async def quiz_result(quiz_id: str):
    if quiz_id not in SUBMISSIONS:
        raise HTTPException(status_code=404, detail="Result not found")
    sub = SUBMISSIONS[quiz_id]
    # Provide generic suggestion based on pass/fail for consistency
    suggestions = (
        ["Great work! Prepare a concise project walkthrough for the video."]
        if sub.get("passed")
        else ["Review foundational concepts and practice with targeted exercises."]
    )
    return SubmitQuizResponse(
        quiz_id=quiz_id,
        score=sub.get("score", 0),
        total=sub.get("total", 0),
        passed=bool(sub.get("passed")),
        suggestions=suggestions,
    )


@app.post("/submit_video")
async def submit_video(
    quiz_id: str = Form(...),
    file: UploadFile = File(...),
):
    if quiz_id not in QUIZZES:
        raise HTTPException(status_code=404, detail="Quiz not found")

    raw = await file.read()

    # Optional S3 upload
    dest_path = None
    bucket = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_REGION")
    if bucket and boto3 is not None:
        try:
            key = f"uploads/{quiz_id}_{file.filename}"
            s3 = boto3.client("s3", region_name=region)
            s3.put_object(Bucket=bucket, Key=key, Body=raw, ContentType=file.content_type or "application/octet-stream")
            dest_path = f"s3://{bucket}/{key}"
        except Exception:
            # Fallback to local save
            pass

    if dest_path is None:
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        local_path = os.path.join(uploads_dir, f"{quiz_id}_{file.filename}")
        with open(local_path, "wb") as f:
            f.write(raw)
        dest_path = local_path

    # Transcribe using OpenAI Whisper if available
    transcript = ""
    if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
        try:
            client = OpenAI()
            # Note: whisper-1 accepts various audio/video formats including mp4
            from io import BytesIO

            stream = BytesIO(raw)
            stream.name = file.filename  # Some clients use name for MIME hints
            tr = client.audio.transcriptions.create(model="whisper-1", file=stream)  # type: ignore
            transcript = getattr(tr, "text", "") or ""
        except Exception:
            transcript = ""

    if not transcript:
        transcript = "Candidate presented a solid understanding of basics and project overview."

    # OpenAI-only analysis: produce feedback + numeric score 0-100
    feedback = "Strong fundamentals; consider deeper examples of real-world integrations."
    video_score: int = 60
    try:
        if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
            client = OpenAI()
            analysis_prompt = (
                "You are an admissions reviewer. Read the transcript and return STRICT JSON with this schema:\n"
                "{\n  \"score\": number (0-100 integer),\n  \"feedback\": string (1-2 sentences)\n}\n\n"
                "Evaluate clarity, technical depth, relevance to topic, and communication.\n"
                "Transcript:\n" + transcript
            )
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_FEEDBACK_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.2,
            )
            content = resp.choices[0].message.content or ""
            try:
                obj = json.loads(content)
                s = int(obj.get("score", video_score))
                if s < 0:
                    s = 0
                if s > 100:
                    s = 100
                video_score = s
                feedback = str(obj.get("feedback") or feedback)
            except Exception:
                # fallback: try to extract first integer in content
                import re

                m = re.search(r"(\d{1,3})", content)
                if m:
                    video_score = max(0, min(100, int(m.group(1))))
                if content.strip():
                    feedback = content.strip()
    except Exception:
        pass

    # Selection: must have passed quiz and achieve score >= 70
    passed_quiz = SUBMISSIONS.get(quiz_id, {}).get("passed", False)
    selected = bool(passed_quiz and video_score >= 70)

    VIDEO_ANALYSIS[quiz_id] = {
        "path": dest_path,
        "transcript": transcript,
        "feedback": feedback,
        "selected": selected,
        "video_score": video_score,
    }

    return {
        "quiz_id": quiz_id,
        "status": "processing_complete",
        "transcript_preview": transcript[:120],
        "selected": selected,
        "video_score": video_score,
    }


@app.post("/submit_video_url")
async def submit_video_url(payload: SubmitVideoURLRequest):
    if payload.quiz_id not in QUIZZES:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if YouTubeTranscriptApi is None:
        raise HTTPException(status_code=500, detail="YouTube transcript dependency not available")

    video_id = _extract_youtube_id(payload.youtube_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # Try transcript in preferred languages
    transcript_text = ""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
        transcript_text = " ".join([seg.get("text", "") for seg in transcript_list])
    except Exception:
        # Try generated
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            tr = transcript_list.find_transcript(["en"]).fetch()
            transcript_text = " ".join([seg.get("text", "") for seg in tr])
        except Exception:
            transcript_text = ""

    if not transcript_text:
        transcript_text = "Transcript unavailable; evaluate based on overall content quality heuristics."

    # OpenAI-only feedback + score
    feedback = "Strong fundamentals; consider deeper examples of real-world integrations."
    video_score: int = 60
    try:
        if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
            client = OpenAI()
            analysis_prompt = (
                "You are an admissions reviewer. Read the transcript and return STRICT JSON with this schema:\n"
                "{\n  \"score\": number (0-100 integer),\n  \"feedback\": string (1-2 sentences)\n}\n\n"
                "Evaluate clarity, technical depth, relevance to topic, and communication.\n"
                "Transcript:\n" + transcript_text
            )
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_FEEDBACK_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.2,
            )
            content = resp.choices[0].message.content or ""
            try:
                obj = json.loads(content)
                s = int(obj.get("score", video_score))
                if s < 0:
                    s = 0
                if s > 100:
                    s = 100
                video_score = s
                feedback = str(obj.get("feedback") or feedback)
            except Exception:
                import re
                m = re.search(r"(\d{1,3})", content)
                if m:
                    video_score = max(0, min(100, int(m.group(1))))
                if content.strip():
                    feedback = content.strip()
    except Exception:
        pass

    passed_quiz = SUBMISSIONS.get(payload.quiz_id, {}).get("passed", False)
    selected = bool(passed_quiz and video_score >= 70)

    VIDEO_ANALYSIS[payload.quiz_id] = {
        "path": f"youtube:{video_id}",
        "transcript": transcript_text,
        "feedback": feedback,
        "selected": selected,
        "video_score": video_score,
    }

    return {
        "quiz_id": payload.quiz_id,
        "status": "processing_complete",
        "transcript_preview": transcript_text[:120],
        "selected": selected,
        "video_score": video_score,
    }


@app.get("/final_result/{quiz_id}", response_model=FinalResultResponse)
async def final_result(quiz_id: str):
    passed_quiz = SUBMISSIONS.get(quiz_id, {}).get("passed")
    analysis = VIDEO_ANALYSIS.get(quiz_id)
    return FinalResultResponse(
        quiz_id=quiz_id,
        passed_quiz=bool(passed_quiz),
        selected=analysis.get("selected") if analysis else None,
        feedback=analysis.get("feedback") if analysis else None,
        video_score=analysis.get("video_score") if analysis else None,
    )


@app.get("/")
async def root():
    return {"status": "ok", "service": "ai-skill-bridge-backend"}


