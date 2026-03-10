import path from "node:path";
import { SOURCE_ROOTS } from "./constants.js";
import { discoverAllSources } from "./discovery.js";
import { ensureDir, writeJson } from "./fs-utils.js";
import { importSkills, loadRegistry, resolveSkill } from "./registry.js";
import { installSkillToTarget, listTargets } from "./targets.js";

function printHelp() {
  console.log(`agent-skill-unifier

Commands:
  discover
  import-local [--sources codex,cursor,claudecode,agents,cursor-rules,antigravity,openclaw]
  list
  install <skill...> --target <target>
  install --all --target <target>

Options:
  --dest <path>   Override target install directory
  --force         Overwrite existing target directory
`);
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const positional = [];
  const flags = {};

  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (!token.startsWith("--")) {
      positional.push(token);
      continue;
    }

    const [rawKey, inlineValue] = token.slice(2).split("=", 2);
    if (inlineValue !== undefined) {
      flags[rawKey] = inlineValue;
      continue;
    }

    const next = rest[index + 1];
    if (!next || next.startsWith("--")) {
      flags[rawKey] = true;
      continue;
    }

    flags[rawKey] = next;
    index += 1;
  }

  return { command, positional, flags };
}

async function runDiscover(flags) {
  const selectedSources = flags.sources
    ? String(flags.sources).split(",").map((item) => item.trim()).filter(Boolean)
    : Object.keys(SOURCE_ROOTS);
  const discovered = await discoverAllSources(selectedSources);

  for (const sourceName of selectedSources) {
    const sourceRoot = SOURCE_ROOTS[sourceName];
    const skills = discovered[sourceName] ?? [];
    console.log(`${sourceName}: ${sourceRoot}`);
    console.log(`  ${skills.length} skills`);
  }
}

async function runImportLocal(flags) {
  const selectedSources = flags.sources
    ? String(flags.sources).split(",").map((item) => item.trim()).filter(Boolean)
    : Object.keys(SOURCE_ROOTS);
  const discovered = await discoverAllSources(selectedSources);
  const registry = await importSkills(discovered);

  await ensureDir(path.join(process.cwd(), "registry"));
  await writeJson(path.join(process.cwd(), "registry", "sources.json"), {
    generatedAt: new Date().toISOString(),
    selectedSources
  });

  console.log(`Imported ${registry.skills.length} unified skills into registry/.`);
}

async function runList() {
  const registry = await loadRegistry();
  for (const skill of registry.skills) {
    const variants = skill.variants.map((variant) => variant.source).join(", ");
    console.log(`${skill.slug} [${variants}]`);
  }
}

async function runInstall(positional, flags) {
  const target = flags.target;
  if (!target) {
    throw new Error(`Missing --target. Available: ${listTargets().join(", ")}`);
  }

  const registry = await loadRegistry();
  const skills = flags.all ? registry.skills : positional.map((name) => {
    const skill = resolveSkill(registry, name);
    if (!skill) {
      throw new Error(`Skill not found: ${name}`);
    }
    return skill;
  });

  for (const skill of skills) {
    const result = await installSkillToTarget(skill, target, {
      dest: flags.dest,
      force: Boolean(flags.force)
    });
    console.log(`${skill.slug} -> ${result.destinationPath}`);
  }
}

export async function runCli(argv) {
  const { command, positional, flags } = parseArgs(argv);

  switch (command) {
    case "discover":
      await runDiscover(flags);
      break;
    case "import-local":
      await runImportLocal(flags);
      break;
    case "list":
      await runList();
      break;
    case "install":
      await runInstall(positional, flags);
      break;
    case undefined:
    case "help":
    case "--help":
      printHelp();
      break;
    default:
      throw new Error(`Unknown command "${command}"`);
  }
}
