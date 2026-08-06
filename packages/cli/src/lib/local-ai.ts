import { join } from "node:path";

function getLocalAiBaseUrl() {
  return (process.env.LOCAL_AI_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

async function readError(response: Response) {
  try {
    const data = (await response.json()) as { detail?: string | { msg?: string }[] };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg!;
  } catch {
    // fall through
  }
  return response.statusText || `Request failed (${response.status})`;
}

export function defaultDocsPath() {
  return join(process.cwd(), "docs");
}

export async function ingestLocalDocs(path: string) {
  const response = await fetch(`${getLocalAiBaseUrl()}/v1/rag/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return (await response.json()) as {
    path: string;
    files: number;
    chunks: number;
    documents: { source: string; chunks: number }[];
  };
}

export async function listLocalDocuments() {
  const response = await fetch(`${getLocalAiBaseUrl()}/v1/rag/documents`);
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as {
    documents: { source: string; chunks: number }[];
  };
}

export async function clearLocalDocuments() {
  const response = await fetch(`${getLocalAiBaseUrl()}/v1/rag/documents`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as { deleted_chunks: number };
}

export async function getLocalRagStatus() {
  const response = await fetch(`${getLocalAiBaseUrl()}/v1/rag/status`);
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as {
    chunks: number;
    sources: { source: string; chunks: number }[];
  };
}
