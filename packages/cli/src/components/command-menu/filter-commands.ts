import { COMMANDS } from "./commands";
import type { Command } from "./types";
import { isLocalMode } from "../../lib/local-mode";

function getAvailableCommands(): Command[] {
  if (!isLocalMode()) {
    return COMMANDS;
  }
  return COMMANDS.filter((cmd) => !cmd.cloudOnly);
}

export function getFilteredCommands(query: string): Command[] {
  const available = getAvailableCommands();
  if (query.length === 0) {
    return available;
  }
  return available.filter((cmd) =>
    cmd.name.toLowerCase().startsWith(query.toLowerCase()),
  );
}
