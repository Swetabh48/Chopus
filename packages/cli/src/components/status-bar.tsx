import { TextAttributes } from "@opentui/core";
import { useTheme } from "../providers/theme";
import { usePromptConfig } from "../providers/prompt-config";
import { Mode } from "@chopus/shared";

function modeLabel(mode: string) {
  if (mode === Mode.CHAT) return "PrivateGPT";
  if (mode === Mode.PLAN) return "Plan";
  return "Build";
}

export function StatusBar() {
  const { mode, model } = usePromptConfig();
  const { colors } = useTheme();

  const fg =
    mode === Mode.CHAT
      ? colors.success
      : mode === Mode.PLAN
        ? colors.planMode
        : colors.primary;

  return (
    <box flexDirection="row" gap={1}>
      <text fg={fg}>{modeLabel(mode)}</text>
      <text attributes={TextAttributes.DIM} fg={colors.dimSeparator}>
        ›
      </text>
      <text>{model}</text>
    </box>
  );
}
