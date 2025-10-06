"use client";
import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { API_BASE } from "@/app/api/config";

type Question = { id: string; text: string; options: string[] };

export default function QuizPage() {
  const { quizId } = useParams<{ quizId: string }>();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<number[]>([]);
  const [timeLeft, setTimeLeft] = useState(60 * 10); // 10 minutes
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (timeLeft > 0) {
      timer = setTimeout(() => setTimeLeft((t) => t - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [timeLeft]);

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch(`${API_BASE}/quiz/${quizId}`);
        if (!res.ok) throw new Error("Failed to load quiz");
        const json = await res.json();
        setQuestions(json.questions);
        setAnswers(new Array(json.questions.length).fill(-1));
      } catch (e) {
        alert((e as Error).message);
      } finally {
        setLoading(false);
      }
    };
    if (quizId) run();
  }, [quizId]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const onSelect = (qIdx: number, optIdx: number) => {
    setAnswers((prev) => {
      const next = [...prev];
      next[qIdx] = optIdx;
      return next;
    });
  };

  const allAnswered = useMemo(() => answers.every((a) => a >= 0), [answers]);

  const submit = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/submit_quiz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz_id: quizId, answers }),
      });
      if (!res.ok) throw new Error("Submit failed");
      router.push(`/result/${quizId}`);
    } catch (e) {
      alert((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="max-w-3xl mx-auto px-6 py-16">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Your Enrollment Quiz</h1>
        {mounted && (
          <div className="text-sm text-white/80">Time left: {Math.floor(timeLeft/60)}:{String(timeLeft%60).padStart(2, "0")}</div>
        )}
      </div>
      <div className="mt-8 grid gap-6">
        {questions.map((q, qi) => (
          <div key={q.id} className="p-6 rounded-xl border border-white/10 bg-white/5">
            <div className="font-medium">Q{qi + 1}. {q.text}</div>
            <div className="mt-4 grid gap-2">
              {q.options.map((opt, oi) => (
                <button
                  key={oi}
                  className={`text-left px-4 py-2 rounded border transition ${answers[qi]===oi ? "bg-sky-500/20 border-sky-400" : "bg-black/20 border-white/10 hover:bg-white/10"}`}
                  onClick={() => onSelect(qi, oi)}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-8 flex items-center justify-end gap-3">
        <button onClick={submit} disabled={!allAnswered} className="px-5 py-3 rounded bg-sky-500 hover:bg-sky-400 disabled:opacity-50 font-medium">Submit Quiz</button>
      </div>
    </div>
  );
}


