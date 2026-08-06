import "opentui-spinner/react";
import { Mode, type ModeType } from "@chopus/shared";
import { useTheme } from "../providers/theme";

type Props = {
  mode?: ModeType;
};

export function Spinner({ mode = Mode.BUILD }: Props) {
  const { colors } = useTheme();
  const activeColor =
    mode === Mode.CHAT
      ? colors.success
      : mode === Mode.PLAN
        ? colors.planMode
        : colors.primary;

  return <spinner name="aesthetic" color={activeColor} />;
};
