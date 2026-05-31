import path from "node:path";
import { TARGETS } from "./constants.js";
import { copyDir, ensureDir, listDirectories, pathExists, removeDir } from "./fs-utils.js";
import { resolveVariantPath } from "./registry.js";

function slugifySkillName(name) {
  return name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

async function findExistingSkillPath(destinationRoot, slug) {
  if (!(await pathExists(destinationRoot))) {
    return null;
  }

  const directories = await listDirectories(destinationRoot);
  const matchingDirectory = directories.find((dirName) => slugifySkillName(dirName) === slug);
  return matchingDirectory ? path.join(destinationRoot, matchingDirectory) : null;
}

export function listTargets() {
  return Object.keys(TARGETS);
}

export function resolveTarget(targetName) {
  const target = TARGETS[targetName];
  if (!target) {
    throw new Error(`Unknown target "${targetName}". Available: ${listTargets().join(", ")}`);
  }
  return target;
}

export async function installSkillToTarget(skill, targetName, options = {}) {
  const target = resolveTarget(targetName);
  const destinationRoot = options.dest ? path.resolve(options.dest) : target.root;

  await ensureDir(destinationRoot);

  let sourcePath = null;
  for (const variantName of target.preferredVariants) {
    sourcePath = await resolveVariantPath(skill, variantName);
    if (sourcePath) {
      break;
    }
  }

  if (!sourcePath) {
    throw new Error(`No compatible variant found for ${skill.slug} -> ${targetName}`);
  }

  const destinationPath = path.join(destinationRoot, skill.slug);
  const existingPath = await findExistingSkillPath(destinationRoot, skill.slug);
  if (existingPath) {
    if (options.skipExisting) {
      return {
        sourcePath,
        destinationPath: existingPath,
        skipped: true,
        reason: "exists"
      };
    }

    if (!options.force) {
      throw new Error(`Destination already exists: ${existingPath}`);
    }
    await removeDir(existingPath);
  }

  await copyDir(sourcePath, destinationPath);
  return {
    sourcePath,
    destinationPath,
    skipped: false
  };
}
