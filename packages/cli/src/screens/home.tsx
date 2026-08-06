import { useCallback, useEffect } from "react";
import { useNavigate } from "react-router";
import { TextAttributes } from "@opentui/core";
import { Mode } from "@chopus/shared";
import { Header } from "../components/header";
import { InputBar } from "../components/input-bar";
import { usePromptConfig } from "../providers/prompt-config";

export function Home() {
  const navigate = useNavigate();
  const { mode, model, setMode } = usePromptConfig();

  useEffect(() => {
    if (mode === Mode.CHAT) {
      setMode(Mode.BUILD);
    }
  }, [mode, setMode]);

  const handleSubmit = useCallback(
    (text: string) => {
      navigate("/sessions/new", {
        state: {
          message: text,
          mode: mode === Mode.CHAT ? Mode.BUILD : mode,
          model,
        },
      });
    },
    [navigate, mode, model],
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
      <Header />
      <box width="100%" maxWidth={78} paddingX={2} flexDirection="column" gap={1}>
        <InputBar onSubmit={handleSubmit} />
        <box flexDirection="row" gap={1} flexShrink={0} marginLeft="auto">
          <text>tab</text>
          <text attributes={TextAttributes.DIM}>agents</text>
          <text attributes={TextAttributes.DIM}>·</text>
          <text attributes={TextAttributes.DIM}>/chat</text>
          <text attributes={TextAttributes.DIM}>PrivateGPT</text>
        </box>
      </box>
    </box>
  );
}
