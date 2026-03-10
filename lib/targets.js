import path from "node:path";
import { TARGETS } from "./constants.js";
import { copyDir, ensureDir, pathExists, removeDir } from "./fs-utils.js";
import { resolveVariantPath } from "./registry.js";

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
  if (await pathExists(destinationPath)) {
    if (!options.force) {
      throw new Error(`Destination already exists: ${destinationPath}`);
    }
    await removeDir(destinationPath);
  }

  await copyDir(sourcePath, destinationPath);
  return {
    sourcePath,
    destinationPath
  };
}
