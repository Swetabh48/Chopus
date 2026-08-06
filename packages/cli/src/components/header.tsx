import { TextAttributes } from "@opentui/core";

type Props = {
  /** Defaults to coding-agent branding */
  variant?: "code" | "private";
};

export function Header({ variant = "code" }: Props) {
  if (variant === "private") {
    return (
      <box alignItems="center" justifyContent="center" flexDirection="column" gap={1}>
        <box flexDirection="row" justifyContent="center" alignItems="center" gap={0.5}>
          <ascii-font font="tiny" text="PRIVATE" color="gray" />
          <ascii-font font="tiny" text="GPT" />
        </box>
        <text attributes={TextAttributes.DIM}>
          Local Ollama + your docs — offline, no coding tools
        </text>
      </box>
    );
  }

  return (
    <box alignItems="center" justifyContent="center">
      <box flexDirection="row" justifyContent="center" alignItems="center" gap={0.5}>
        <ascii-font font="tiny" text="CHOPUS" color="gray" />
        <ascii-font font="tiny" text="Code"/>
      </box>
    </box>
  );
}
