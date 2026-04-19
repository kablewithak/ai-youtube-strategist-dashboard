export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type Assumptions = {
  audience_interests: string[];
  likely_topic_patterns: string[];
  audience_intent: string;
  screenshot_interpretation: string;
  confidence_notes: string;
};

async function parseResponse(response: Response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return text;
}

function getErrorMessage(status: number, body: unknown) {
  if (typeof body === "string" && body.trim()) {
    return `Request failed (${status}): ${body}`;
  }

  if (body && typeof body === "object") {
    const maybeDetail =
      "detail" in body && typeof (body as { detail?: unknown }).detail === "string"
        ? (body as { detail: string }).detail
        : null;

    if (maybeDetail) {
      return `Request failed (${status}): ${maybeDetail}`;
    }
  }

  return `Request failed with status ${status}`;
}

export async function createRun(payload: {
  channel_url: string;
  channel_niche: string;
  channel_goals: string;
  audience_demographics: Record<string, unknown>;
  notes: string;
}) {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error(
      "Could not reach the API. Make sure the backend is running on http://localhost:8000."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}

export async function getRun(runId: string) {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs/${runId}`, {
      cache: "no-store",
    });
  } catch {
    throw new Error(
      "Could not reach the API. Make sure the backend is running on http://localhost:8000."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}

export async function updateAssumptions(runId: string, assumptions: Assumptions) {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs/${runId}/assumptions`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ assumptions }),
    });
  } catch {
    throw new Error(
      "Could not reach the API while saving assumptions. Make sure the backend is still running."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}

export async function ingestYouTubeEvidence(runId: string) {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs/${runId}/ingest-youtube`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch {
    throw new Error(
      "Could not reach the API while ingesting YouTube evidence. Make sure the backend is still running."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}

export async function uploadScreenshots(runId: string, files: File[]) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs/${runId}/screenshots`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      "Could not reach the API while uploading screenshots. Make sure the backend is still running."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}

export async function synthesizeEvidence(runId: string) {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs/${runId}/synthesize-evidence`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch {
    throw new Error(
      "Could not reach the API while synthesizing evidence. Make sure the backend is still running."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}

export async function draftRecommendations(runId: string) {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/runs/${runId}/recommendations/draft`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch {
    throw new Error(
      "Could not reach the API while drafting recommendations. Make sure the backend is still running."
    );
  }

  const body = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(response.status, body));
  }

  return body;
}