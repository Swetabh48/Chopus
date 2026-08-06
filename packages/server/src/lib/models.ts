import { createOpenAI } from "@ai-sdk/openai";
import {
  findSupportedChatModel,
  type SupportedChatModel,
  type SupportedChatModelId,
  type SupportedProvider,
} from "@chopus/shared";
import type { LanguageModel } from "ai";

type OllamaModelId = Extract<SupportedChatModel, { provider: "ollama" }>["id"];

export type ResolvedModel = {
  model: LanguageModel;
  provider: SupportedProvider;
  modelId: SupportedChatModelId;
};

function getLocalAiBaseUrl() {
  const base = process.env.LOCAL_AI_URL ?? "http://localhost:8000";
  return `${base.replace(/\/$/, "")}/v1`;
}

const localAi = createOpenAI({
  name: "ollama",
  baseURL: getLocalAiBaseUrl(),
  apiKey: process.env.LOCAL_AI_API_KEY ?? "local",
});

function resolveOllamaModel(modelId: OllamaModelId): ResolvedModel {
  return {
    // OpenAI chat-completions shape; services/ai proxies this to Ollama.
    model: localAi.chat(modelId),
    provider: "ollama",
    modelId,
  };
};

export function isSupportedChatModel(modelId: string): modelId is SupportedChatModelId {
  return findSupportedChatModel(modelId) != null;
};

export function resolveChatModel(modelId: string): ResolvedModel {
  const model = findSupportedChatModel(modelId);
  if (!model) {
    throw new Error(`Unsupported model: ${modelId}`);
  }

  return resolveOllamaModel(model.id);
};
