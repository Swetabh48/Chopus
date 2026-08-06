import { useCallback, useState } from "react";
import { TextAttributes } from "@opentui/core";
import { useKeyboard } from "@opentui/react";
import { useDialog } from "../../providers/dialog";
import { useToast } from "../../providers/toast";
import { useTheme } from "../../providers/theme";
import { defaultDocsPath, ingestLocalDocs } from "../../lib/local-ai";

type Props = {
  initialPath?: string;
};

export function IngestDialogContent({ initialPath }: Props) {
  const dialog = useDialog();
  const toast = useToast();
  const { colors } = useTheme();
  const [path, setPath] = useState(initialPath ?? defaultDocsPath());
  const [busy, setBusy] = useState(false);

  const submit = useCallback(async () => {
    if (busy) return;
    const trimmed = path.trim();
    if (!trimmed) {
      toast.show({ variant: "error", message: "Enter a file or folder path" });
      return;
    }

    setBusy(true);
    toast.show({ message: `Ingesting ${trimmed}...` });

    try {
      const result = await ingestLocalDocs(trimmed);
      toast.show({
        variant: "success",
        message: `Ingested ${result.files} file(s), ${result.chunks} chunk(s)`,
      });
      dialog.close();
    } catch (error) {
      toast.show({
        variant: "error",
        message: error instanceof Error ? error.message : "Ingest failed",
      });
    } finally {
      setBusy(false);
    }
  }, [busy, dialog, path, toast]);

  useKeyboard((key) => {
    if (key.name === "return" || key.name === "enter") {
      key.preventDefault();
      void submit();
    }
  });

  return (
    <box flexDirection="column" width="100%" gap={1} padding={1}>
      <text fg={colors.primary}>Path to file or folder (.pdf, .md, .txt)</text>
      <text attributes={TextAttributes.DIM}>Default: ./docs in the current project</text>
      <input
        focused
        value={path}
        onInput={(value: string) => setPath(value)}
        placeholder={defaultDocsPath()}
        width="100%"
      />
      <text>{busy ? "Working..." : "Enter to ingest · Esc to cancel"}</text>
    </box>
  );
}
