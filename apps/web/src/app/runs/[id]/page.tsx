"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getRun, updateAssumptions } from "@/lib/api";

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
};

export default function RunPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;

  const [run, setRun] = useState<RunData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pageError, setPageError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");

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
      <div className="mx-auto max-w-4xl space-y-8">
        <div>
          <h1 className="text-3xl font-semibold">Assumption Review</h1>
          <p className="mt-2 text-sm text-neutral-600">
            Review and edit provisional strategist assumptions before deeper analysis.
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

          <div className="mt-6 flex items-center gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="rounded-lg bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-60"
            >
              {saving ? "Saving..." : "Save assumptions"}
            </button>

            <span className="text-sm text-neutral-500">
              Current status: {run.status}
            </span>
          </div>
        </section>
      </div>
    </main>
  );
}