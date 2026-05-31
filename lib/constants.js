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
const SIBLING_HERMES_AGENT_ROOT = path.resolve(PROJECT_ROOT, "..", "hermes-agent");

function envPath(name, fallbackPath) {
  return process.env[name] ? path.resolve(process.env[name]) : fallbackPath;
}

export const SOURCE_ROOTS = {
  codex: path.join(HOME, ".codex", "skills"),
  agents: path.join(HOME, ".agents", "skills"),
  claudecode: path.join(HOME, ".claude", "skills"),
  cursor: path.join(HOME, ".cursor", "skills"),
  "cursor-staging": path.join(HOME, ".cursor", "skills-staging"),
  "cursor-rules": path.join(HOME, ".cursor", "skills-cursor"),
  "cursor-rules-staging": path.join(HOME, ".cursor", "rules-staging"),
  "hermes-agent": envPath(
    "HERMES_AGENT_SKILLS_ROOT",
    path.join(SIBLING_HERMES_AGENT_ROOT, "skills")
  ),
  "hermes-agent-optional": envPath(
    "HERMES_AGENT_OPTIONAL_SKILLS_ROOT",
    path.join(SIBLING_HERMES_AGENT_ROOT, "optional-skills")
  ),
  "hermes-agent-plugins": envPath(
    "HERMES_AGENT_PLUGINS_ROOT",
    path.join(SIBLING_HERMES_AGENT_ROOT, "plugins")
  ),
  "hermes-agent-vendor": envPath(
    "HERMES_AGENT_VENDOR_SKILLS_ROOT",
    path.join(
      SIBLING_HERMES_AGENT_ROOT,
      "vendor",
      "openclaw-mirror",
      "extensions",
      "hypura-harness",
      "skills"
    )
  ),
  antigravity: path.join(HOME, ".antigravity", "skills"),
  openclaw: path.join(HOME, ".openclaw", "skills")
};

export const SOURCE_PRIORITY = [
  "codex",
  "cursor",
  "cursor-staging",
  "claudecode",
  "agents",
  "cursor-rules",
  "cursor-rules-staging",
  "hermes-agent",
  "hermes-agent-optional",
  "hermes-agent-plugins",
  "hermes-agent-vendor",
  "antigravity",
  "openclaw"
];

const PORTABLE_SKILL_VARIANTS = [
  "hermes-agent",
  "hermes-agent-optional",
  "hermes-agent-plugins",
  "hermes-agent-vendor"
];

export const TARGETS = {
  codex: {
    root: SOURCE_ROOTS.codex,
    preferredVariants: [
      "codex",
      "cursor",
      "cursor-staging",
      "claudecode",
      "agents",
      ...PORTABLE_SKILL_VARIANTS
    ]
  },
  claudecode: {
    root: SOURCE_ROOTS.claudecode,
    preferredVariants: [
      "claudecode",
      "codex",
      "cursor",
      "cursor-staging",
      "agents",
      ...PORTABLE_SKILL_VARIANTS
    ]
  },
  cursor: {
    root: SOURCE_ROOTS.cursor,
    preferredVariants: [
      "cursor",
      "cursor-staging",
      "codex",
      "claudecode",
      "agents",
      ...PORTABLE_SKILL_VARIANTS
    ]
  },
  "cursor-rules": {
    root: SOURCE_ROOTS["cursor-rules"],
    preferredVariants: [
      "cursor-rules",
      "cursor-rules-staging",
      "cursor",
      "cursor-staging",
      "codex",
      ...PORTABLE_SKILL_VARIANTS
    ]
  },
  antigravity: {
    root: SOURCE_ROOTS.antigravity,
    preferredVariants: [
      "antigravity",
      "cursor",
      "cursor-staging",
      "codex",
      "claudecode",
      ...PORTABLE_SKILL_VARIANTS
    ]
  },
  openclaw: {
    root: SOURCE_ROOTS.openclaw,
    preferredVariants: [
      "openclaw",
      "codex",
      "cursor",
      "cursor-staging",
      "claudecode",
      ...PORTABLE_SKILL_VARIANTS
    ]
  }
};

export const SYSTEM_SKILL_NAMES = new Set([".system"]);
