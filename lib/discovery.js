import fs from "node:fs/promises";
import path from "node:path";
import { SOURCE_ROOTS, SYSTEM_SKILL_NAMES } from "./constants.js";
import { pathExists, listDirectories } from "./fs-utils.js";

const IGNORED_DIRECTORY_NAMES = new Set([
  ".git",
  ".hg",
  ".svn",
  ".venv",
  "venv",
  "node_modules",
  "__pycache__",
  ".pytest-cache",
  ".pytest_cache",
  ".ruff_cache"
]);

function slugifySkillName(name) {
  return name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

async function maybeReadSkillMetadata(skillPath) {
  const skillMdPath = path.join(skillPath, "SKILL.md");
  if (!(await pathExists(skillMdPath))) {
    return null;
  }

  const body = await fs.readFile(skillMdPath, "utf8");
  const frontmatterMatch = body.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const frontmatter = frontmatterMatch?.[1] ?? "";
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const descriptionMatch = frontmatter.match(/^description:\s*(.+)$/m);

  return {
    displayName: nameMatch?.[1]?.trim() ?? path.basename(skillPath),
    description: descriptionMatch?.[1]?.trim() ?? "",
    hasSkillFile: true
  };
}

async function listSkillDirectories(rootPath) {
  const results = [];

  async function visit(directoryPath) {
    const dirs = await listDirectories(directoryPath);

    for (const dirName of dirs) {
      if (SYSTEM_SKILL_NAMES.has(dirName) || IGNORED_DIRECTORY_NAMES.has(dirName)) {
        continue;
      }

      const childPath = path.join(directoryPath, dirName);
      if (await pathExists(path.join(childPath, "SKILL.md"))) {
        results.push(childPath);
        continue;
      }

      await visit(childPath);
    }
  }

  await visit(rootPath);
  return results;
}

export async function discoverSourceSkills(sourceName) {
  const rootPath = SOURCE_ROOTS[sourceName];
  if (!rootPath || !(await pathExists(rootPath))) {
    return [];
  }

  const skillPaths = await listSkillDirectories(rootPath);
  const skillsBySlug = new Map();

  for (const skillPath of skillPaths.sort((left, right) => left.localeCompare(right))) {
    const metadata = await maybeReadSkillMetadata(skillPath);
    if (!metadata?.hasSkillFile) {
      continue;
    }

    const directoryName = path.basename(skillPath);
    const slug = slugifySkillName(directoryName);
    if (skillsBySlug.has(slug)) {
      continue;
    }

    skillsBySlug.set(slug, {
      source: sourceName,
      sourcePath: skillPath,
      directoryName,
      relativePath: path.relative(rootPath, skillPath).replaceAll("\\", "/"),
      slug,
      displayName: metadata.displayName,
      description: metadata.description
    });
  }

  return [...skillsBySlug.values()].sort((left, right) => left.slug.localeCompare(right.slug));
}

export async function discoverAllSources(selectedSources = Object.keys(SOURCE_ROOTS)) {
  const results = {};
  for (const sourceName of selectedSources) {
    results[sourceName] = await discoverSourceSkills(sourceName);
  }
  return results;
}
