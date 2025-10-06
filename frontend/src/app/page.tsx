import Link from "next/link";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 backdrop-blur bg-black/30 border-b border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-sky-500" />
            <span className="font-semibold">AI Skill Bridge</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-white/80">
            <Link href="/" className="hover:text-white">Home</Link>
            <Link href="/about" className="hover:text-white">About</Link>
            <Link href="/enroll" className="hover:text-white">Quiz</Link>
            <Link href="#contact" className="hover:text-white">Contact</Link>
          </nav>
          <Link href="/enroll" className="px-4 py-2 rounded bg-sky-500 hover:bg-sky-400 text-sm font-medium">Take Quiz</Link>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(50%_50%_at_50%_0%,rgba(14,165,233,0.25)_0%,rgba(11,18,32,0)_60%)]" />
          <div className="max-w-6xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-10 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold leading-tight">
                Become Top 1% in the AI-First World
              </h1>
              <p className="mt-4 text-white/80">
                Join Pakistan&apos;s First Fully-Funded, in-person AI Bootcamp. 100 seats available. No fees. Just your commitment.
              </p>
              <div className="mt-8 flex gap-4">
                <Link href="/enroll" className="px-5 py-3 rounded bg-sky-500 hover:bg-sky-400 font-medium">Take Quiz for Enrollment</Link>
                <a href="https://aiskillbridge.pk/" target="_blank" className="px-5 py-3 rounded border border-white/20 hover:bg-white/5">Learn More</a>
              </div>
            </div>
            <div className="relative aspect-video rounded-xl overflow-hidden border border-white/10">
              <Image src="/window.svg" alt="Hero" fill className="object-cover opacity-80" />
            </div>
          </div>
        </section>

        {/* About */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-semibold">About AI Skill Bridge</h2>
          <p className="mt-3 text-white/80 max-w-3xl">
            AI is transforming industries globally. By acquiring these skills now, you position yourself at the forefront of this revolution.
          </p>
        </section>

        {/* How It Works */}
        <section className="bg-white/5 border-y border-white/10">
          <div className="max-w-6xl mx-auto px-6 py-16">
            <h2 className="text-2xl font-semibold">How It Works</h2>
            <div className="mt-8 grid md:grid-cols-3 gap-6">
              {["Quiz","Video","Enrollment"].map((step, i) => (
                <div key={step} className="p-6 rounded-xl border border-white/10 bg-black/20">
                  <div className="text-sky-400 text-sm">Step {i+1}</div>
                  <div className="mt-2 text-lg font-medium">{step}</div>
                  <p className="mt-2 text-white/70">
                    {i===0 && "Take a quick topic-based MCQ quiz."}
                    {i===1 && "Submit a short video showcasing your skills."}
                    {i===2 && "Get your result and enrollment decision."}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-semibold">Testimonials</h2>
          <div className="mt-6 grid md:grid-cols-3 gap-6">
            {Array.from({length:3}).map((_,i)=> (
              <div key={i} className="p-6 rounded-xl border border-white/10 bg-white/5">
                <div className="text-white/80">“AI is the single most powerful force of our generation.”</div>
                <div className="mt-3 text-sm text-white/60">— Jensen Huang</div>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer id="contact" className="border-t border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-10 text-sm text-white/70 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>AI Skill Bridge © 2025. Designed by Jarify</div>
          <div className="flex gap-4">
            <a href="mailto:contact@example.com" className="hover:text-white">Contact</a>
            <a href="#" className="hover:text-white">Privacy</a>
            <a href="#" className="hover:text-white">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
