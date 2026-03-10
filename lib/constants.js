import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const PROJECT_ROOT = path.resolve(__dirname, "..");
export const REGISTRY_ROOT = path.join(PROJECT_ROOT, "registry");
export const REGISTRY_SKILLS_ROOT = path.join(REGISTRY_ROOT, "skills");
export const REGISTRY_INDEX_PATH = path.join(REGISTRY_ROOT, "index.json");

const HOME = os.homedir();

export const SOURCE_ROOTS = {
  codex: path.join(HOME, ".codex", "skills"),
  agents: path.join(HOME, ".agents", "skills"),
  claudecode: path.join(HOME, ".claude", "skills"),
  cursor: path.join(HOME, ".cursor", "skills"),
  "cursor-rules": path.join(HOME, ".cursor", "skills-cursor"),
  antigravity: path.join(HOME, ".antigravity", "skills"),
  openclaw: path.join(HOME, ".openclaw", "skills")
};

export const SOURCE_PRIORITY = [
  "codex",
  "cursor",
  "claudecode",
  "agents",
  "cursor-rules",
  "antigravity",
  "openclaw"
];

export const TARGETS = {
  codex: {
    root: SOURCE_ROOTS.codex,
    preferredVariants: ["codex", "cursor", "claudecode", "agents"]
  },
  claudecode: {
    root: SOURCE_ROOTS.claudecode,
    preferredVariants: ["claudecode", "codex", "cursor", "agents"]
  },
  cursor: {
    root: SOURCE_ROOTS.cursor,
    preferredVariants: ["cursor", "codex", "claudecode", "agents"]
  },
  "cursor-rules": {
    root: SOURCE_ROOTS["cursor-rules"],
    preferredVariants: ["cursor-rules", "cursor", "codex"]
  },
  antigravity: {
    root: SOURCE_ROOTS.antigravity,
    preferredVariants: ["antigravity", "cursor", "codex", "claudecode"]
  },
  openclaw: {
    root: SOURCE_ROOTS.openclaw,
    preferredVariants: ["openclaw", "codex", "cursor", "claudecode"]
  }
};

export const SYSTEM_SKILL_NAMES = new Set([".system"]);
