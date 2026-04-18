"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getRun, ingestYouTubeEvidence, updateAssumptions } from "@/lib/api";

type RunData = {
  id: string;
  status: string;
  channel_url: string;
  channel_niche: string;
  channel_goals: string;
  assumptions: {
    audience_interests: string[];
    likely_topic_patterns: string[];
    audience_intent: string;
    screenshot_interpretation: string;
    confidence_notes: string;
  };
  youtube_channel: {
    channel_id: string;
    title: string;
    description: string;
    custom_url: string;
    published_at: string;
    uploads_playlist_id: string;
    subscriber_count: number | null;
    video_count: number | null;
    view_count: number | null;
    thumbnails: Record<string, string>;
  } | null;
  videos: Array<{
    video_id: string;
    channel_id: string;
    channel_title: string;
    title: string;
    description: string;
    published_at: string;
    url: string;
    view_count: number | null;
    like_count: number | null;
    comment_count: number | null;
  }>;
  comment_samples: Array<{
    comment_id: string;
    video_id: string;
    author_display_name: string;
    text_display: string;
    like_count: number | null;
    published_at: string;
    updated_at: string;
  }>;
  evidence_summary: {
    total_videos_fetched: number;
    total_comments_fetched: number;
    top_video_titles: string[];
    repeated_phrases: string[];
    praise_themes: string[];
    request_themes: string[];
    pain_points: string[];
    evidence_notes: string[];
  } | null;
};

export default function RunPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;

  const [run, setRun] = useState<RunData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [pageError, setPageError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [ingestMessage, setIngestMessage] = useState("");

  useEffect(() => {
    async function loadRun() {
      setLoading(true);
      setPageError("");

      try {
        const data = await getRun(runId);
        setRun(data);
      } catch (err) {
        setPageError(err instanceof Error ? err.message : "Failed to load run");
      } finally {
        setLoading(false);
      }
    }

    if (runId) {
      void loadRun();
    }
  }, [runId]);

  async function handleSave() {
    if (!run) return;

    setSaving(true);
    setPageError("");
    setSaveMessage("");
    setIngestMessage("");

    try {
      const updated = await updateAssumptions(runId, run.assumptions);
      setRun(updated);
      setSaveMessage("Assumptions saved successfully.");
    } catch (err) {
      setPageError(
        err instanceof Error ? err.message : "Failed to save assumptions"
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleIngest() {
    if (!run) return;

    setIngesting(true);
    setPageError("");
    setSaveMessage("");
    setIngestMessage("");

    try {
      const updated = await ingestYouTubeEvidence(runId);
      setRun(updated);
      setIngestMessage("YouTube evidence ingested successfully.");
    } catch (err) {
      setPageError(
        err instanceof Error ? err.message : "Failed to ingest YouTube evidence"
      );
    } finally {
      setIngesting(false);
    }
  }

  if (loading) {
    return <main className="p-8">Loading run...</main>;
  }

  if (!run) {
    return (
      <main className="p-8">
        <div className="mx-auto max-w-3xl rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-red-700">
          {pageError || "Run not found."}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white px-6 py-12 text-black">
      <div className="mx-auto max-w-5xl space-y-8">
        <div>
          <h1 className="text-3xl font-semibold">Assumption Review</h1>
          <p className="mt-2 text-sm text-neutral-600">
            Review and edit provisional strategist assumptions, then ingest YouTube
            evidence for this run.
          </p>
        </div>

        {pageError ? (
          <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
            {pageError}
          </div>
        ) : null}

        {saveMessage ? (
          <div className="rounded-lg border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {saveMessage}
          </div>
        ) : null}

        {ingestMessage ? (
          <div className="rounded-lg border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {ingestMessage}
          </div>
        ) : null}

        <section className="rounded-2xl border border-neutral-200 p-6">
          <h2 className="text-xl font-semibold">Run overview</h2>
          <div className="mt-4 space-y-2 text-sm text-neutral-700">
            <p>
              <strong>Status:</strong> {run.status}
            </p>
            <p>
              <strong>Channel URL:</strong> {run.channel_url}
            </p>
            <p>
              <strong>Niche:</strong> {run.channel_niche}
            </p>
            <p>
              <strong>Goals:</strong> {run.channel_goals}
            </p>
          </div>
        </section>

        <section className="rounded-2xl border border-neutral-200 p-6">
          <h2 className="text-xl font-semibold">Assumptions</h2>

          <div className="mt-6 space-y-6">
            <div>
              <label className="mb-2 block text-sm font-medium">
                Audience interests
              </label>
              <textarea
                value={run.assumptions.audience_interests.join("\n")}
                onChange={(e) =>
                  setRun({
                    ...run,
                    assumptions: {
                      ...run.assumptions,
                      audience_interests: e.target.value
                        .split("\n")
                        .map((item) => item.trim())
                        .filter(Boolean),
                    },
                  })
                }
                className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Likely topic patterns
              </label>
              <textarea
                value={run.assumptions.likely_topic_patterns.join("\n")}
                onChange={(e) =>
                  setRun({
                    ...run,
                    assumptions: {
                      ...run.assumptions,
                      likely_topic_patterns: e.target.value
                        .split("\n")
                        .map((item) => item.trim())
                        .filter(Boolean),
                    },
                  })
                }
                className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Audience intent
              </label>
              <textarea
                value={run.assumptions.audience_intent}
                onChange={(e) =>
                  setRun({
                    ...run,
                    assumptions: {
                      ...run.assumptions,
                      audience_intent: e.target.value,
                    },
                  })
                }
                className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Screenshot interpretation
              </label>
              <textarea
                value={run.assumptions.screenshot_interpretation}
                onChange={(e) =>
                  setRun({
                    ...run,
                    assumptions: {
                      ...run.assumptions,
                      screenshot_interpretation: e.target.value,
                    },
                  })
                }
                className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Confidence notes
              </label>
              <textarea
                value={run.assumptions.confidence_notes}
                onChange={(e) =>
                  setRun({
                    ...run,
                    assumptions: {
                      ...run.assumptions,
                      confidence_notes: e.target.value,
                    },
                  })
                }
                className="min-h-24 w-full rounded-lg border border-neutral-300 px-4 py-3"
              />
            </div>
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
            >
              {saving ? "Saving..." : "Save assumptions"}
            </button>

            <button
              onClick={handleIngest}
              disabled={ingesting}
              className="rounded-lg border border-black px-5 py-3 text-sm font-medium text-black disabled:opacity-60"
            >
              {ingesting ? "Ingesting..." : "Ingest YouTube Evidence"}
            </button>

            <span className="text-sm text-neutral-500">
              Current status: {run.status}
            </span>
          </div>
        </section>

        {run.youtube_channel ? (
          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">YouTube channel</h2>
            <div className="mt-4 space-y-2 text-sm text-neutral-700">
              <p>
                <strong>Title:</strong> {run.youtube_channel.title}
              </p>
              <p>
                <strong>Channel ID:</strong> {run.youtube_channel.channel_id}
              </p>
              <p>
                <strong>Subscribers:</strong>{" "}
                {run.youtube_channel.subscriber_count ?? "N/A"}
              </p>
              <p>
                <strong>Videos:</strong> {run.youtube_channel.video_count ?? "N/A"}
              </p>
              <p>
                <strong>Views:</strong> {run.youtube_channel.view_count ?? "N/A"}
              </p>
              {run.youtube_channel.description ? (
                <p>
                  <strong>Description:</strong> {run.youtube_channel.description}
                </p>
              ) : null}
            </div>
          </section>
        ) : null}

        {run.evidence_summary ? (
          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Evidence summary</h2>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-neutral-200 p-4">
                <p className="text-sm font-medium text-neutral-500">
                  Videos fetched
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {run.evidence_summary.total_videos_fetched}
                </p>
              </div>

              <div className="rounded-xl border border-neutral-200 p-4">
                <p className="text-sm font-medium text-neutral-500">
                  Comments fetched
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {run.evidence_summary.total_comments_fetched}
                </p>
              </div>
            </div>

            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <div>
                <h3 className="text-sm font-semibold">Top video titles</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  {run.evidence_summary.top_video_titles.length ? (
                    run.evidence_summary.top_video_titles.map((title) => (
                      <li key={title}>• {title}</li>
                    ))
                  ) : (
                    <li>No video titles available yet.</li>
                  )}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Repeated phrases</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  {run.evidence_summary.repeated_phrases.length ? (
                    run.evidence_summary.repeated_phrases.map((phrase) => (
                      <li key={phrase}>• {phrase}</li>
                    ))
                  ) : (
                    <li>No repeated phrases detected yet.</li>
                  )}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Praise themes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  {run.evidence_summary.praise_themes.length ? (
                    run.evidence_summary.praise_themes.map((theme) => (
                      <li key={theme}>• {theme}</li>
                    ))
                  ) : (
                    <li>No praise themes detected yet.</li>
                  )}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Request themes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  {run.evidence_summary.request_themes.length ? (
                    run.evidence_summary.request_themes.map((theme) => (
                      <li key={theme}>• {theme}</li>
                    ))
                  ) : (
                    <li>No request themes detected yet.</li>
                  )}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Pain points</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  {run.evidence_summary.pain_points.length ? (
                    run.evidence_summary.pain_points.map((theme) => (
                      <li key={theme}>• {theme}</li>
                    ))
                  ) : (
                    <li>No pain points detected yet.</li>
                  )}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Evidence notes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  {run.evidence_summary.evidence_notes.length ? (
                    run.evidence_summary.evidence_notes.map((note) => (
                      <li key={note}>• {note}</li>
                    ))
                  ) : (
                    <li>No evidence notes available yet.</li>
                  )}
                </ul>
              </div>
            </div>
          </section>
        ) : null}

        {run.videos.length ? (
          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Recent videos</h2>
            <div className="mt-4 space-y-4">
              {run.videos.map((video) => (
                <div
                  key={video.video_id}
                  className="rounded-xl border border-neutral-200 p-4"
                >
                  <p className="font-medium">{video.title}</p>
                  <p className="mt-1 text-sm text-neutral-600">{video.url}</p>
                  {video.description ? (
                    <p className="mt-2 text-sm text-neutral-700 line-clamp-3">
                      {video.description}
                    </p>
                  ) : null}
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {run.comment_samples.length ? (
          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Comment samples</h2>
            <div className="mt-4 space-y-4">
              {run.comment_samples.slice(0, 12).map((comment) => (
                <div
                  key={comment.comment_id}
                  className="rounded-xl border border-neutral-200 p-4"
                >
                  <p className="text-sm font-medium">{comment.author_display_name}</p>
                  <p className="mt-2 text-sm text-neutral-700">
                    {comment.text_display}
                  </p>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </main>
  );
}