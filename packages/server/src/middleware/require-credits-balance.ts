import { createMiddleware } from "hono/factory";
import { isOllamaChatModel } from "@chopus/shared";
import type { AuthenticatedEnv } from "./require-auth";
import { getAvailableCreditsBalance, isPolarConfigured } from "../lib/polar";

export const requireCreditsBalance = createMiddleware<AuthenticatedEnv>(async (c, next) => {
  // Local PrivateGPT / Ollama: no Polar account required.
  if (!isPolarConfigured()) {
    await next();
    return;
  }

  // Peek at the body so local Ollama chats can skip Polar.
  // Hono caches JSON bodies, so later validators can still read it.
  let modelId: unknown;
  try {
    const body = await c.req.json();
    if (body && typeof body === "object" && "model" in body) {
      modelId = (body as { model?: unknown }).model;
    }
  } catch {
    // Invalid JSON is handled by route validators.
  }

  if (typeof modelId === "string" && isOllamaChatModel(modelId)) {
    await next();
    return;
  }

  try {
    const userId = c.get("userId");
    const creditsBalance = await getAvailableCreditsBalance(userId);

    // This is a simple launch-time gate: only start new work when the customer
    // still has credits left. It does not reserve the full eventual cost of the
    // request, so low-volume apps may tolerate small overspend on edge cases.
    if (creditsBalance <= 0) {
      return c.json({ error: "No credits remaining. Run /upgrade to buy more credits." }, 402);
    }

    await next();
  } catch {
    return c.json({ error: "Unable to verify credits balance right now." }, 503);
  }
});
