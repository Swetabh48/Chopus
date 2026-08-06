import { Mode, SUPPORTED_CHAT_MODELS } from "@chopus/shared";
import { 
  AgentsDialogContent,
  DocsDialogContent,
  IngestDialogContent,
  ModelsDialogContent,
  SessionsDialogContent,
  ThemeDialogContent,
} from "../dialogs";
import type { Command } from "./types";

import { performLogin } from "../../lib/oauth";
import { clearAuth } from "../../lib/auth";
import { clearLocalDocuments } from "../../lib/local-ai";

import { openBillingPortal, openUpgradeCheckout } from "../../lib/upgrade";

export const COMMANDS: Command[] = [
  {
    name: "chat",
    description: "Open PrivateGPT (local docs Q&A, no coding tools)",
    value: "/chat",
    action: (ctx) => {
      ctx.setMode(Mode.CHAT);
      ctx.navigate("/chat");
    },
  },
  {
    name: "agent",
    description: "Open coding agent (Build/Plan tools)",
    value: "/agent",
    action: (ctx) => {
      ctx.setMode(Mode.BUILD);
      ctx.navigate("/");
    },
  },
  {
    name: "new",
    description: "Start a new conversation",
    value: "/new",
    action: (ctx) => {
      ctx.navigate(ctx.mode === Mode.CHAT ? "/chat" : "/");
    },
  },
  {
    name: "agents",
    description: "Switch agents",
    value: "/agents",
    action: (ctx) => {
      if (ctx.mode === Mode.CHAT) {
        ctx.toast.show({
          message: "PrivateGPT has no agents. Use /agent for Build/Plan.",
        });
        return;
      }
      ctx.dialog.open({
        title: "Select Agent",
        children: <AgentsDialogContent currentMode={ctx.mode} onSelectMode={ctx.setMode} />,
      })
    },
  },
  {
    name: "models",
    description: "Select AI model for generation",
    value: "/models",
    action: (ctx) => {
      ctx.dialog.open({
        title: "Select Model",
        children: (
          <ModelsDialogContent
            models={SUPPORTED_CHAT_MODELS.map((model) => model.id)}
            onSelectModel={ctx.setModel}
          />
        ),
      })
    },
  },
  {
    name: "sessions",
    description: "Browse past sessions",
    value: "/sessions",
    action: (ctx) => {
      ctx.dialog.open({
        title: "Sessions",
        children: <SessionsDialogContent />,
      })
    },
  },
  {
    name: "ingest",
    description: "Ingest local PDFs/Markdown/text into private RAG",
    value: "/ingest",
    action: (ctx) => {
      ctx.dialog.open({
        title: "Ingest Documents",
        children: <IngestDialogContent />,
      });
    },
  },
  {
    name: "docs",
    description: "List documents in the local knowledge base",
    value: "/docs",
    action: (ctx) => {
      ctx.dialog.open({
        title: "Local Documents",
        children: <DocsDialogContent />,
      });
    },
  },
  {
    name: "forget",
    description: "Clear the local RAG knowledge base",
    value: "/forget",
    action: async (ctx) => {
      ctx.toast.show({ message: "Clearing local documents..." });
      try {
        const result = await clearLocalDocuments();
        ctx.toast.show({
          variant: "success",
          message: `Cleared ${result.deleted_chunks} chunk(s)`,
        });
      } catch (error) {
        ctx.toast.show({
          variant: "error",
          message: error instanceof Error ? error.message : "Failed to clear documents",
        });
      }
    },
  },
  {
    name: "theme",
    description: "Change color theme",
    value: "/theme",
    action: (ctx) => {
      ctx.dialog.open({
        title: "Select Theme",
        children: <ThemeDialogContent />,
      })
    },
  },
  {
    name: "login",
    description: "Sign in with your browser",
    value: "/login",
    cloudOnly: true,
    action: async (ctx) => {
      ctx.toast.show({ message: "Opening browser to sign in..." });

      try {
        await performLogin();
        ctx.toast.show({ variant: "success", message: "Signed in" });
      } catch (error) {
        const message = error instanceof Error 
          ? error.message 
          : "Sign in failed or timed out";

        ctx.toast.show({ variant: "error", message });
      }
    },
  },
  {
    name: "logout",
    description: "Sign out of your account",
    value: "/logout",
    cloudOnly: true,
    action: (ctx) => {
      clearAuth();
      ctx.toast.show({ variant: "success", message: "Signed out" });
    },
  },
  {
    name: "upgrade",
    description: "Buy more credits",
    value: "/upgrade",
    cloudOnly: true,
    action: async (ctx) => {
      ctx.toast.show({ message: "Opening credits checkout..." });

      try {
        await openUpgradeCheckout();
        ctx.toast.show({
          variant: "success",
          message: "Checkout opened in browser",
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to open checkout";
        ctx.toast.show({ variant: "error", message });
      }
    },
  },
  {
    name: "usage",
    description: "Open billing portal in your browser",
    value: "/usage",
    cloudOnly: true,
    action: async (ctx) => {
      ctx.toast.show({ message: "Opening billing portal..." });

      try {
        await openBillingPortal();
        ctx.toast.show({
          variant: "success",
          message: "Billing portal opened in browser",
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to open billing portal";
        ctx.toast.show({ variant: "error", message });
      }
    },
  },
  {
    name: "exit",
    description: "Quit the application",
    value: "/exit",
    action: (ctx) => {
      ctx.exit();
    },
  },
];
