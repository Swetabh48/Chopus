import { useEffect, useState } from "react";
import { TextAttributes } from "@opentui/core";
import { useTheme } from "../../providers/theme";
import { listLocalDocuments } from "../../lib/local-ai";

type DocRow = { source: string; chunks: number };

export function DocsDialogContent() {
  const { colors } = useTheme();
  const [docs, setDocs] = useState<DocRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    void (async () => {
      try {
        const result = await listLocalDocuments();
        if (!ignore) setDocs(result.documents);
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Failed to load documents");
        }
      }
    })();
    return () => {
      ignore = true;
    };
  }, []);

  if (error) {
    return (
      <box padding={1}>
        <text fg={colors.error}>{error}</text>
      </box>
    );
  }

  if (!docs) {
    return (
      <box padding={1}>
        <text>Loading local documents...</text>
      </box>
    );
  }

  if (docs.length === 0) {
    return (
      <box padding={1} flexDirection="column" gap={1}>
        <text>No documents ingested yet.</text>
        <text attributes={TextAttributes.DIM}>Use /ingest on a ./docs folder or file path.</text>
      </box>
    );
  }

  return (
    <box padding={1} flexDirection="column" gap={1} width="100%">
      <text fg={colors.primary}>{docs.length} source(s) in local knowledge base</text>
      {docs.map((doc) => (
        <text key={doc.source} attributes={TextAttributes.DIM}>
          {doc.chunks} chunk(s) · {doc.source}
        </text>
      ))}
    </box>
  );
}
