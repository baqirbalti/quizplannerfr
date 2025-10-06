"use client";
import { useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { API_BASE } from "@/app/api/config";

export default function VideoPage() {
  const { quizId } = useParams<{ quizId: string }>();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const submit = async () => {
    if (!file) return;
    try {
      setLoading(true);
      const fd = new FormData();
      fd.append("quiz_id", String(quizId));
      fd.append("file", file);
      const res = await fetch(`${API_BASE}/submit_video`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error("Upload failed");
      router.push(`/final/${quizId}`);
    } catch (e) {
      alert((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-semibold">Final Step: Show Your Skills</h1>
      <p className="mt-2 text-white/70">Upload a short video or screen recording explaining your project/skills.</p>

      <div className="mt-8 grid gap-4">
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="file:mr-4 file:rounded file:border-0 file:bg-sky-500 file:px-4 file:py-2 file:text-white file:hover:bg-sky-400 w-full text-sm text-white/80"
        />
        <button
          disabled={!file || loading}
          onClick={submit}
          className="px-5 py-3 rounded bg-sky-500 hover:bg-sky-400 disabled:opacity-50 font-medium"
        >
          {loading ? "Submitting..." : "Submit Video"}
        </button>
      </div>
    </div>
  );
}


