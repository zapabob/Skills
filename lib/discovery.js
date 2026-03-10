import fs from "node:fs/promises";
import path from "node:path";
import { SOURCE_ROOTS, SYSTEM_SKILL_NAMES } from "./constants.js";
import { pathExists, listDirectories } from "./fs-utils.js";

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

export async function discoverSourceSkills(sourceName) {
  const rootPath = SOURCE_ROOTS[sourceName];
  if (!rootPath || !(await pathExists(rootPath))) {
    return [];
  }

  const dirs = await listDirectories(rootPath);
  const skills = [];

  for (const dirName of dirs) {
    if (SYSTEM_SKILL_NAMES.has(dirName)) {
      continue;
    }

    const skillPath = path.join(rootPath, dirName);
    const metadata = await maybeReadSkillMetadata(skillPath);
    if (!metadata?.hasSkillFile) {
      continue;
    }

    skills.push({
      source: sourceName,
      sourcePath: skillPath,
      directoryName: dirName,
      slug: slugifySkillName(dirName),
      displayName: metadata.displayName,
      description: metadata.description
    });
  }

  return skills.sort((left, right) => left.slug.localeCompare(right.slug));
}

export async function discoverAllSources(selectedSources = Object.keys(SOURCE_ROOTS)) {
  const results = {};
  for (const sourceName of selectedSources) {
    results[sourceName] = await discoverSourceSkills(sourceName);
  }
  return results;
}
