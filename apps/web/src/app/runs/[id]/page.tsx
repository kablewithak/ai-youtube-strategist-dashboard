"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  draftRecommendations,
  getRun,
  ingestYouTubeEvidence,
  synthesizeEvidence,
  updateAssumptions,
  uploadScreenshots,
} from "@/lib/api";

type RunData = {
  id: string;
  status: string;
  channel_url: string;
  channel_niche: string;
  channel_goals: string;
  notes: string;
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
  screenshots: Array<{
    id: string;
    original_filename: string;
    stored_filename: string;
    local_path: string;
    mime_type: string;
    size_bytes: number;
    uploaded_at: string;
  }>;
  synthesized_evidence: {
    channel_summary: string;
    audience_mood: string;
    praise_themes: string[];
    pain_points: string[];
    request_themes: string[];
    repeated_phrases: string[];
    evidence_strength_notes: string[];
  } | null;
};

type RecommendationDraft = {
  audience_analysis: {
    viewer_state_profile: {
      emotional_jobs: string[];
      hidden_tensions: string[];
      desired_identity: string[];
      emotional_drivers: string[];
      trust_mode: string;
      evidence_notes: string[];
    };
    confirmed_findings: string[];
    inferences: string[];
    weak_signals: string[];
    assumptions_used: string[];
  };
  candidates: Array<{
    id: string;
    topic: string;
    angle: string;
    target_viewer_state: string;
    emotional_driver: string;
    evidence_anchors: string[];
    trend_anchors: string[];
    channel_fit_score: number;
    audience_fit_score: number;
    trend_score: number;
  }>;
  final_recommendations: Array<{
    rank: number;
    idea: string;
    hook: string;
    title_options: string[];
    thumbnail_angle: string;
    structure: string[];
    cta_placement: string;
    cta_copy: string[];
    why_this_fits: string;
    evidence_notes: string[];
  }>;
};

function listTextToArray(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function arrayToListText(value: string[]) {
  return value.join("\n");
}

function BulletList({
  items,
  emptyText,
}: {
  items: string[];
  emptyText: string;
}) {
  if (!items.length) {
    return <li>{emptyText}</li>;
  }

  return (
    <>
      {items.map((item) => (
        <li key={item}>• {item}</li>
      ))}
    </>
  );
}

export default function RunPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;

  const [run, setRun] = useState<RunData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [synthesizing, setSynthesizing] = useState(false);
  const [draftingRecommendations, setDraftingRecommendations] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const [audienceInterestsText, setAudienceInterestsText] = useState("");
  const [likelyTopicPatternsText, setLikelyTopicPatternsText] = useState("");

  const [recommendationDraft, setRecommendationDraft] =
    useState<RecommendationDraft | null>(null);

  const [pageError, setPageError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [ingestMessage, setIngestMessage] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [synthesisMessage, setSynthesisMessage] = useState("");
  const [recommendationsMessage, setRecommendationsMessage] = useState("");

  useEffect(() => {
    async function loadRun() {
      setLoading(true);
      setPageError("");

      try {
        const data = await getRun(runId);
        setRun(data);
        setAudienceInterestsText(arrayToListText(data.assumptions.audience_interests));
        setLikelyTopicPatternsText(
          arrayToListText(data.assumptions.likely_topic_patterns)
        );
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

  function clearMessages() {
    setPageError("");
    setSaveMessage("");
    setIngestMessage("");
    setUploadMessage("");
    setSynthesisMessage("");
    setRecommendationsMessage("");
  }

  async function handleSave() {
    if (!run) return;

    setSaving(true);
    clearMessages();

    try {
      const updated = await updateAssumptions(runId, {
        audience_interests: listTextToArray(audienceInterestsText),
        likely_topic_patterns: listTextToArray(likelyTopicPatternsText),
        audience_intent: run.assumptions.audience_intent,
        screenshot_interpretation: run.assumptions.screenshot_interpretation,
        confidence_notes: run.assumptions.confidence_notes,
      });

      setRun(updated);
      setAudienceInterestsText(arrayToListText(updated.assumptions.audience_interests));
      setLikelyTopicPatternsText(
        arrayToListText(updated.assumptions.likely_topic_patterns)
      );
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
    clearMessages();

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

  function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const fileList = event.target.files;
    if (!fileList) return;
    setSelectedFiles(Array.from(fileList));
  }

  async function handleUploadScreenshots() {
    if (!run || selectedFiles.length === 0) return;

    setUploading(true);
    clearMessages();

    try {
      const updated = await uploadScreenshots(runId, selectedFiles);
      setRun(updated);
      setSelectedFiles([]);
      setUploadMessage("Screenshots uploaded successfully.");
    } catch (err) {
      setPageError(
        err instanceof Error ? err.message : "Failed to upload screenshots"
      );
    } finally {
      setUploading(false);
    }
  }

  async function handleSynthesize() {
    if (!run) return;

    setSynthesizing(true);
    clearMessages();

    try {
      const updated = await synthesizeEvidence(runId);
      setRun(updated);
      setSynthesisMessage("Evidence synthesized successfully.");
    } catch (err) {
      setPageError(
        err instanceof Error ? err.message : "Failed to synthesize evidence"
      );
    } finally {
      setSynthesizing(false);
    }
  }

  async function handleDraftRecommendations() {
    setDraftingRecommendations(true);
    clearMessages();

    try {
      const draft = await draftRecommendations(runId);
      setRecommendationDraft(draft);
      setRecommendationsMessage("Recommendation draft generated successfully.");
    } catch (err) {
      setPageError(
        err instanceof Error ? err.message : "Failed to draft recommendations"
      );
    } finally {
      setDraftingRecommendations(false);
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
      <div className="mx-auto max-w-6xl space-y-8">
        <div>
          <h1 className="text-3xl font-semibold">AI YouTube Strategist Dashboard</h1>
          <p className="mt-2 text-sm text-neutral-600">
            Review assumptions, ingest evidence, synthesize findings, and draft
            strategist recommendations.
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

        {uploadMessage ? (
          <div className="rounded-lg border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {uploadMessage}
          </div>
        ) : null}

        {synthesisMessage ? (
          <div className="rounded-lg border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {synthesisMessage}
          </div>
        ) : null}

        {recommendationsMessage ? (
          <div className="rounded-lg border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {recommendationsMessage}
          </div>
        ) : null}

        <section className="rounded-2xl border border-neutral-200 p-6">
          <h2 className="text-xl font-semibold">Run overview</h2>
          <div className="mt-4 grid gap-3 text-sm text-neutral-700 md:grid-cols-2">
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
          {run.notes ? (
            <p className="mt-4 text-sm text-neutral-700">
              <strong>Notes:</strong> {run.notes}
            </p>
          ) : null}
        </section>

        <section className="rounded-2xl border border-neutral-200 p-6">
          <h2 className="text-xl font-semibold">Assumptions</h2>

          <div className="mt-6 space-y-6">
            <div>
              <label className="mb-2 block text-sm font-medium">
                Audience interests
              </label>
              <textarea
                value={audienceInterestsText}
                onChange={(e) => setAudienceInterestsText(e.target.value)}
                className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
                placeholder="One audience interest per line"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Likely topic patterns
              </label>
              <textarea
                value={likelyTopicPatternsText}
                onChange={(e) => setLikelyTopicPatternsText(e.target.value)}
                className="min-h-28 w-full rounded-lg border border-neutral-300 px-4 py-3"
                placeholder="One topic pattern per line"
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

            <button
              onClick={handleDraftRecommendations}
              disabled={draftingRecommendations || !run.synthesized_evidence}
              className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
            >
              {draftingRecommendations
                ? "Drafting..."
                : "Draft Recommendations"}
            </button>

            <span className="text-sm text-neutral-500">
              Current status: {run.status}
            </span>
          </div>
        </section>

        <section className="rounded-2xl border border-neutral-200 p-6">
          <h2 className="text-xl font-semibold">Screenshot evidence</h2>

          <div className="mt-4 space-y-4">
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp,image/heic,image/heif"
              multiple
              onChange={handleFileSelection}
              className="block w-full text-sm"
            />

            {selectedFiles.length ? (
              <div className="rounded-lg border border-neutral-200 p-4 text-sm text-neutral-700">
                <p className="font-medium">Selected files</p>
                <ul className="mt-2 space-y-1">
                  {selectedFiles.map((file) => (
                    <li key={`${file.name}-${file.size}`}>• {file.name}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleUploadScreenshots}
                disabled={uploading || selectedFiles.length === 0}
                className="rounded-lg border border-black px-5 py-3 text-sm font-medium text-black disabled:opacity-60"
              >
                {uploading ? "Uploading..." : "Upload screenshots"}
              </button>

              <button
                onClick={handleSynthesize}
                disabled={synthesizing}
                className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
              >
                {synthesizing ? "Synthesizing..." : "Synthesize Evidence"}
              </button>
            </div>
          </div>

          {run.screenshots.length ? (
            <div className="mt-6 rounded-lg border border-neutral-200 p-4">
              <p className="text-sm font-medium">Uploaded screenshots</p>
              <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                {run.screenshots.map((shot) => (
                  <li key={shot.id}>• {shot.original_filename}</li>
                ))}
              </ul>
            </div>
          ) : null}
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
                  <BulletList
                    items={run.evidence_summary.top_video_titles}
                    emptyText="No video titles available yet."
                  />
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Repeated phrases</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  <BulletList
                    items={run.evidence_summary.repeated_phrases}
                    emptyText="No repeated phrases detected yet."
                  />
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Praise themes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  <BulletList
                    items={run.evidence_summary.praise_themes}
                    emptyText="No praise themes detected yet."
                  />
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Request themes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  <BulletList
                    items={run.evidence_summary.request_themes}
                    emptyText="No request themes detected yet."
                  />
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Pain points</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  <BulletList
                    items={run.evidence_summary.pain_points}
                    emptyText="No pain points detected yet."
                  />
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Evidence notes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  <BulletList
                    items={run.evidence_summary.evidence_notes}
                    emptyText="No evidence notes available yet."
                  />
                </ul>
              </div>
            </div>
          </section>
        ) : null}

        {run.synthesized_evidence ? (
          <section className="rounded-2xl border border-neutral-200 p-6">
            <h2 className="text-xl font-semibold">Synthesized strategist findings</h2>

            <div className="mt-6 space-y-6">
              <div>
                <h3 className="text-sm font-semibold">Channel summary</h3>
                <p className="mt-2 text-sm text-neutral-700">
                  {run.synthesized_evidence.channel_summary || "No channel summary yet."}
                </p>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Audience mood</h3>
                <p className="mt-2 text-sm text-neutral-700">
                  {run.synthesized_evidence.audience_mood || "No audience mood yet."}
                </p>
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                <div>
                  <h3 className="text-sm font-semibold">Praise themes</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={run.synthesized_evidence.praise_themes}
                      emptyText="No praise themes yet."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Pain points</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={run.synthesized_evidence.pain_points}
                      emptyText="No pain points yet."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Request themes</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={run.synthesized_evidence.request_themes}
                      emptyText="No request themes yet."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Repeated phrases</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={run.synthesized_evidence.repeated_phrases}
                      emptyText="No repeated phrases yet."
                    />
                  </ul>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold">Evidence strength notes</h3>
                <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                  <BulletList
                    items={run.synthesized_evidence.evidence_strength_notes}
                    emptyText="No evidence strength notes yet."
                  />
                </ul>
              </div>
            </div>
          </section>
        ) : null}

        {recommendationDraft ? (
          <>
            <section className="rounded-2xl border border-neutral-200 p-6">
              <h2 className="text-xl font-semibold">Audience psychology</h2>

              <div className="mt-6 grid gap-6 md:grid-cols-2">
                <div>
                  <h3 className="text-sm font-semibold">Emotional jobs</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={
                        recommendationDraft.audience_analysis.viewer_state_profile
                          .emotional_jobs
                      }
                      emptyText="No emotional jobs detected."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Hidden tensions</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={
                        recommendationDraft.audience_analysis.viewer_state_profile
                          .hidden_tensions
                      }
                      emptyText="No hidden tensions detected."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Desired identity</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={
                        recommendationDraft.audience_analysis.viewer_state_profile
                          .desired_identity
                      }
                      emptyText="No desired identity detected."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Emotional drivers</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={
                        recommendationDraft.audience_analysis.viewer_state_profile
                          .emotional_drivers
                      }
                      emptyText="No emotional drivers detected."
                    />
                  </ul>
                  <p className="mt-3 text-sm text-neutral-700">
                    <strong>Trust mode:</strong>{" "}
                    {
                      recommendationDraft.audience_analysis.viewer_state_profile
                        .trust_mode
                    }
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Confirmed findings</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={recommendationDraft.audience_analysis.confirmed_findings}
                      emptyText="No confirmed findings yet."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Inferences</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={recommendationDraft.audience_analysis.inferences}
                      emptyText="No inferences yet."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Weak signals</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={recommendationDraft.audience_analysis.weak_signals}
                      emptyText="No weak signals flagged."
                    />
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold">Assumptions used</h3>
                  <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                    <BulletList
                      items={recommendationDraft.audience_analysis.assumptions_used}
                      emptyText="No assumptions recorded."
                    />
                  </ul>
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-neutral-200 p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold">Top 10 ranked video ideas</h2>
                  <p className="mt-2 text-sm text-neutral-600">
                    Evidence-backed ideas with packaging and CTA logic.
                  </p>
                </div>
                <div className="rounded-lg border border-neutral-200 px-4 py-2 text-sm text-neutral-600">
                  Candidate pool: {recommendationDraft.candidates.length}
                </div>
              </div>

              <div className="mt-6 space-y-6">
                {recommendationDraft.final_recommendations.map((item) => (
                  <article
                    key={`${item.rank}-${item.idea}`}
                    className="rounded-2xl border border-neutral-200 p-5"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-neutral-500">
                          Rank #{item.rank}
                        </p>
                        <h3 className="mt-1 text-lg font-semibold">{item.idea}</h3>
                      </div>
                    </div>

                    <div className="mt-5 grid gap-6 md:grid-cols-2">
                      <div>
                        <h4 className="text-sm font-semibold">Hook</h4>
                        <p className="mt-2 text-sm text-neutral-700">{item.hook}</p>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold">Thumbnail angle</h4>
                        <p className="mt-2 text-sm text-neutral-700">
                          {item.thumbnail_angle}
                        </p>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold">Title options</h4>
                        <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                          <BulletList
                            items={item.title_options}
                            emptyText="No title options provided."
                          />
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold">CTA placement</h4>
                        <p className="mt-2 text-sm text-neutral-700">
                          {item.cta_placement}
                        </p>

                        <h4 className="mt-4 text-sm font-semibold">CTA copy</h4>
                        <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                          <BulletList
                            items={item.cta_copy}
                            emptyText="No CTA copy provided."
                          />
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold">Suggested structure</h4>
                        <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                          <BulletList
                            items={item.structure}
                            emptyText="No structure provided."
                          />
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold">Why this fits</h4>
                        <p className="mt-2 text-sm text-neutral-700">
                          {item.why_this_fits}
                        </p>

                        <h4 className="mt-4 text-sm font-semibold">Evidence notes</h4>
                        <ul className="mt-2 space-y-2 text-sm text-neutral-700">
                          <BulletList
                            items={item.evidence_notes}
                            emptyText="No evidence notes provided."
                          />
                        </ul>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}