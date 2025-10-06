"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/app/api/config";

const schema = z.object({
	email: z.string().email(),
	topic: z.string().min(2),
	num_questions: z.number().min(1).max(30),
});

type FormData = z.infer<typeof schema>;

export default function EnrollPage() {
	const router = useRouter();
	const [loading, setLoading] = useState(false);
	const [submitted, setSubmitted] = useState(false);
	const [emailQueued, setEmailQueued] = useState<boolean | null>(null);
	const [serverEmail, setServerEmail] = useState<string | null>(null);
	const [quizId, setQuizId] = useState<string | null>(null);
	const [resending, setResending] = useState(false);
	const [resendError, setResendError] = useState<string | null>(null);
	const {
		register,
		handleSubmit,
		formState: { errors },
	} = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { num_questions: 10 } });

	const onSubmit = async (data: FormData) => {
		try {
			setLoading(true);
			const res = await fetch(`${API_BASE}/generate_quiz`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					email: data.email,
					topic: data.topic,
					num_questions: data.num_questions,
				}),
			});
			if (!res.ok) throw new Error("Failed to generate quiz");
			const json = await res.json();
			// Do NOT navigate directly. Require email link flow.
			setSubmitted(true);
			setEmailQueued(json.email_queued === true ? true : null);
			setQuizId(json.quiz_id);
			setServerEmail(data.email);
			setResendError(null);
		} catch (e) {
			alert((e as Error).message);
		} finally {
			setLoading(false);
		}
	};

	const resend = async () => {
		if (!quizId || !serverEmail) return;
    try {
			setResending(true);
			setResendError(null);
			const res = await fetch(`${API_BASE}/resend_quiz_email`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ quiz_id: quizId, email: serverEmail }),
			});
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || "Failed to resend email");
      }
			const json = await res.json();
			if (!json?.ok) throw new Error("Resend returned not ok");
			if (json?.status?.error) {
				setResendError(String(json.status.error));
			} else {
				alert("Email resent. Please check your inbox/spam.");
			}
		} catch (e) {
			setResendError((e as Error).message);
		} finally {
			setResending(false);
		}
	};

	return (
		<div className="max-w-2xl mx-auto px-6 py-16">
			<h1 className="text-3xl font-semibold">Quiz Enrollment</h1>
			<p className="mt-2 text-white/70">Fill the details to generate your quiz.</p>

			{!submitted ? (
				<form onSubmit={handleSubmit(onSubmit)} className="mt-8 grid gap-6">
					<div>
						<label className="text-sm text-white/80">Email</label>
						<input
							className="mt-2 w-full px-4 py-2 rounded bg-white/5 border border-white/10 outline-none focus:ring-2 focus:ring-sky-500"
							placeholder="you@email.com"
							{...register("email")}
						/>
						{errors.email && <p className="text-sm text-red-400 mt-1">{errors.email.message}</p>}
					</div>
					<div>
						<label className="text-sm text-white/80">Select Topic</label>
						<input
							className="mt-2 w-full px-4 py-2 rounded bg-white/5 border border-white/10 outline-none focus:ring-2 focus:ring-sky-500"
							placeholder="e.g., Python, Generative AI, LLMs"
							{...register("topic")}
						/>
						{errors.topic && <p className="text-sm text-red-400 mt-1">{errors.topic.message}</p>}
					</div>
					<div>
						<label className="text-sm text-white/80">Number of MCQs</label>
						<input
							type="number"
							className="mt-2 w-full px-4 py-2 rounded bg-white/5 border border-white/10 outline-none focus:ring-2 focus:ring-sky-500"
							min={1}
							max={30}
							{...register("num_questions", { valueAsNumber: true })}
						/>
						{errors.num_questions && (
							<p className="text-sm text-red-400 mt-1">{errors.num_questions.message as string}</p>
						)}
					</div>
					<button
						type="submit"
						disabled={loading}
						className="px-5 py-3 rounded bg-sky-500 hover:bg-sky-400 disabled:opacity-60 font-medium"
					>
						{loading ? "Generating..." : "Generate Quiz"}
					</button>
				</form>
			) : (
				<div className="mt-8 p-6 rounded-xl border border-white/10 bg-white/5">
					<div className="text-lg font-medium">Check your email</div>
					<p className="mt-2 text-white/80">
						We&apos;ve sent your quiz link to {serverEmail || "your inbox"}. Please open the link to start the quiz.
					</p>
					<div className="mt-4">
						<button onClick={resend} disabled={resending || !quizId} className="px-4 py-2 rounded border border-white/20 hover:bg-white/10 disabled:opacity-50">
							{resending ? "Resending..." : "Resend email"}
						</button>
					</div>
					{resendError && (
						<p className="mt-3 text-red-400 text-sm">{resendError}</p>
					)}
					{emailQueued === false && (
						<p className="mt-3 text-amber-300">
							Email delivery is not configured yet. Please contact the admin to enable SMTP sending.
						</p>
					)}
				</div>
			)}
		</div>
	);
}


