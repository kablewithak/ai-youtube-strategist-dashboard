"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createRun } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();

  const [channelUrl, setChannelUrl] = useState("");
  const [channelNiche, setChannelNiche] = useState("");
  const [channelGoals, setChannelGoals] = useState("");

  const [ageRange, setAgeRange] = useState("18-34");
  const [primaryGeography, setPrimaryGeography] = useState("South Africa");
  const [primaryLanguage, setPrimaryLanguage] = useState("English");
  const [viewerLifeStage, setViewerLifeStage] = useState("");
  const [topInterestsText, setTopInterestsText] = useState(
    "career growth, self-improvement"
  );
  const [demographicNotes, setDemographicNotes] = useState("");

  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const audienceDemographics = {
        age_range: ageRange,
        geography: primaryGeography,
        language: primaryLanguage,
        viewer_life_stage: viewerLifeStage,
        interests: topInterestsText
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        notes: demographicNotes,
      };

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
        err instanceof Error
          ? err.message
          : "Something went wrong while creating the run."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-white px-6 py-12 text-black">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-semibold">AI YouTube Strategist Dashboard</h1>
        <p className="mt-2 text-sm text-neutral-600">
          Add your channel context, audience details, and notes to start the
          strategist workflow.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-8">
          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Channel intake</h2>

            <div className="mt-6 space-y-6">
              <div>
                <label className="mb-2 block text-sm font-medium">
                  YouTube channel URL
                </label>
                <input
                  value={channelUrl}
                  onChange={(e) => setChannelUrl(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="https://www.youtube.com/@channelname"
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Channel niche
                </label>
                <input
                  value={channelNiche}
                  onChange={(e) => setChannelNiche(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="Business, career advice, finance, wellness, commentary"
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Channel goals
                </label>
                <textarea
                  value={channelGoals}
                  onChange={(e) => setChannelGoals(e.target.value)}
                  className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="Grow audience, improve retention, find stronger video ideas, improve packaging"
                  required
                />
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Audience demographics</h2>
            <p className="mt-2 text-sm text-neutral-600">
              Fill this in normally. No JSON needed.
            </p>

            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium">Age range</label>
                <input
                  value={ageRange}
                  onChange={(e) => setAgeRange(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="18-24, 25-34, 18-34"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Primary geography
                </label>
                <input
                  value={primaryGeography}
                  onChange={(e) => setPrimaryGeography(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="South Africa"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Primary language
                </label>
                <input
                  value={primaryLanguage}
                  onChange={(e) => setPrimaryLanguage(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="English"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Viewer life stage
                </label>
                <input
                  value={viewerLifeStage}
                  onChange={(e) => setViewerLifeStage(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="Students, early-career professionals, founders, working adults"
                />
              </div>

              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-medium">
                  Top interests
                </label>
                <input
                  value={topInterestsText}
                  onChange={(e) => setTopInterestsText(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="career growth, money, self-improvement, entrepreneurship"
                />
                <p className="mt-2 text-xs text-neutral-500">
                  Separate interests with commas.
                </p>
              </div>

              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-medium">
                  Demographic notes
                </label>
                <textarea
                  value={demographicNotes}
                  onChange={(e) => setDemographicNotes(e.target.value)}
                  className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
                  placeholder="Anything useful about audience context, worldview, local market relevance, spending power, or content preferences"
                />
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Additional notes</h2>

            <div className="mt-6">
              <label className="mb-2 block text-sm font-medium">Run notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="min-h-36 w-full rounded-lg border border-neutral-300 px-4 py-3"
                placeholder="Creator notes, audience context, screenshot interpretation notes, channel observations"
              />
            </div>
          </section>

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