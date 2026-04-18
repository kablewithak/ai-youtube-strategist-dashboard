"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createRun } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();

  const [channelUrl, setChannelUrl] = useState("");
  const [channelNiche, setChannelNiche] = useState("");
  const [channelGoals, setChannelGoals] = useState("");
  const [audienceDemographicsText, setAudienceDemographicsText] = useState(
    '{\n  "age_range": "18-34",\n  "geography": "South Africa",\n  "interests": ["self-improvement", "career growth"]\n}'
  );
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const audienceDemographics = JSON.parse(audienceDemographicsText);

      const run = await createRun({
        channel_url: channelUrl,
        channel_niche: channelNiche,
        channel_goals: channelGoals,
        audience_demographics: audienceDemographics,
        notes,
      });

      router.push(`/runs/${run.id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong while creating the run."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-white px-6 py-12 text-black">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-semibold">AI YouTube Strategist Dashboard</h1>
        <p className="mt-2 text-sm text-neutral-600">
          Intake your channel context, draft assumptions, and prepare for strategist analysis.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div>
            <label className="mb-2 block text-sm font-medium">YouTube channel URL</label>
            <input
              value={channelUrl}
              onChange={(e) => setChannelUrl(e.target.value)}
              className="w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="https://www.youtube.com/@channelname"
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Channel niche</label>
            <input
              value={channelNiche}
              onChange={(e) => setChannelNiche(e.target.value)}
              className="w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="Career advice, finance, wellness, commentary"
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Channel goals</label>
            <textarea
              value={channelGoals}
              onChange={(e) => setChannelGoals(e.target.value)}
              className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="Grow audience, improve retention, find stronger video ideas"
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Audience demographics JSON</label>
            <textarea
              value={audienceDemographicsText}
              onChange={(e) => setAudienceDemographicsText(e.target.value)}
              className="min-h-40 w-full rounded-lg border border-neutral-300 px-4 py-3 font-mono text-sm"
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="min-h-36 w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="Creator notes, audience context, screenshot interpretation notes"
            />
          </div>

          {error ? (
            <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
          >
            {isSubmitting ? "Creating run..." : "Analyze Channel"}
          </button>
        </form>
      </div>
    </main>
  );
}