"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { API_BASE } from "@/app/api/config";

export default function FinalPage() {
  const { quizId } = useParams<{ quizId: string }>();
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<boolean | null>(null);
  const [passedQuiz, setPassedQuiz] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch(`${API_BASE}/final_result/${quizId}`);
        if (!res.ok) throw new Error("Failed to load final result");
        const json = await res.json();
        setSelected(json.selected);
        setPassedQuiz(json.passed_quiz);
        setFeedback(json.feedback);
      } catch (e) {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    if (quizId) run();
  }, [quizId]);

  if (loading) return <div className="max-w-3xl mx-auto px-6 py-16">Evaluating...</div>;

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      {selected ? (
        <div className="p-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10">
          <div className="text-2xl font-semibold">✅ Congratulations!</div>
          <p className="mt-2 text-white/80">You have been selected. Download your certificate soon.</p>
        </div>
      ) : (
        <div className="p-6 rounded-xl border border-white/10 bg-white/5">
          <div className="text-2xl font-semibold">❌ Thank You</div>
          <p className="mt-2 text-white/80">You were not selected this time. Keep improving and try again!</p>
        </div>
      )}
      {feedback && (
        <div className="mt-6 p-4 rounded-lg border border-white/10 bg-black/30">
          <div className="font-medium">Feedback</div>
          <p className="mt-2 text-white/80">{feedback}</p>
        </div>
      )}
    </div>
  );
}


