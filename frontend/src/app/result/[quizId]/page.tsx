"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { API_BASE } from "@/app/api/config";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
ChartJS.register(ArcElement, Tooltip, Legend);
const Pie = dynamic(() => import("react-chartjs-2").then(m => m.Pie), { ssr: false });

export default function ResultPage() {
  const { quizId } = useParams<{ quizId: string }>();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [score, setScore] = useState(0);
  const [total, setTotal] = useState(0);
  const [passed, setPassed] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    setMounted(true);
    const run = async () => {
      try {
        const res = await fetch(`${API_BASE}/quiz_result/${quizId}`);
        if (!res.ok) throw new Error("Failed to load result");
        const json = await res.json();
        setScore(json.score);
        setTotal(json.total);
        setPassed(json.passed);
        setSuggestions(json.suggestions || []);
      } catch (e) {
        alert((e as Error).message);
      } finally {
        setLoading(false);
      }
    };
    if (quizId) run();
  }, [quizId]);

  if (loading) return <div className="max-w-3xl mx-auto px-6 py-16">Loading...</div>;

  const correct = score;
  const wrong = Math.max(0, total - score);
  const data = {
    labels: ["Correct", "Wrong"],
    datasets: [
      {
        data: [correct, wrong],
        backgroundColor: ["#22c55e", "#ef4444"],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold">Your Result</h1>
      <div className="mt-6 p-6 rounded-xl border border-white/10 bg-white/5">
        <div className="text-lg">Score: {score}/{total}</div>
        {mounted && (
          <div className="mt-4 w-64">
            <Pie data={data} />
          </div>
        )}
        <div className="mt-6">
          <div className="font-medium">AI Suggestions</div>
          <ul className="list-disc list-inside text-white/80 mt-2">
            {suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
        {passed ? (
          <div className="mt-6 flex gap-3">
            <button onClick={() => router.push(`/video/${quizId}`)} className="px-5 py-3 rounded bg-sky-500 hover:bg-sky-400 font-medium">Proceed to Video Submission</button>
          </div>
        ) : (
          <div className="mt-6">
            <div className="text-white/80">Don&apos;t give up—retry when ready!</div>
            <div className="mt-3 flex gap-3">
              <button onClick={() => router.push("/enroll")} className="px-5 py-3 rounded border border-white/20 hover:bg-white/10">Retry Quiz</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


