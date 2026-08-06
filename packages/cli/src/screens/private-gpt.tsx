import { useCallback, useEffect } from "react";
import { useNavigate } from "react-router";
import { TextAttributes } from "@opentui/core";
import { Mode } from "@chopus/shared";
import { Header } from "../components/header";
import { InputBar } from "../components/input-bar";
import { usePromptConfig } from "../providers/prompt-config";

/** Separate PrivateGPT surface — no agent tools. */
export function PrivateGptHome() {
  const navigate = useNavigate();
  const { model, setMode } = usePromptConfig();

  useEffect(() => {
    setMode(Mode.CHAT);
  }, [setMode]);

  const handleSubmit = useCallback(
    (text: string) => {
      navigate("/sessions/new", {
        state: { message: text, mode: Mode.CHAT, model },
      });
    },
    [navigate, model],
  );

  return (
    <box
      alignItems="center"
      justifyContent="center"
      flexGrow={1}
      gap={2}
      position="relative"
      width="100%"
      height="100%"
    >
      <Header variant="private" />
      <box width="100%" maxWidth={78} paddingX={2} flexDirection="column" gap={1}>
        <InputBar onSubmit={handleSubmit} />
        <box flexDirection="row" gap={1} flexShrink={0} marginLeft="auto">
          <text attributes={TextAttributes.DIM}>/ingest</text>
          <text attributes={TextAttributes.DIM}>docs</text>
          <text attributes={TextAttributes.DIM}>·</text>
          <text attributes={TextAttributes.DIM}>/agent</text>
          <text attributes={TextAttributes.DIM}>coding mode</text>
        </box>
      </box>
    </box>
  );
}
