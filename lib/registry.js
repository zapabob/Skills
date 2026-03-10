import path from "node:path";
import {
  REGISTRY_INDEX_PATH,
  REGISTRY_SKILLS_ROOT,
  SOURCE_PRIORITY
} from "./constants.js";
import { copyDir, ensureDir, pathExists, readJson, removeDir, writeJson } from "./fs-utils.js";

export async function loadRegistry() {
  const registry = await readJson(REGISTRY_INDEX_PATH, { generatedAt: null, skills: [] });
  registry.skills ??= [];
  return registry;
}

function sortVariants(variants) {
  return [...variants].sort((left, right) => {
    const leftPriority = SOURCE_PRIORITY.indexOf(left.source);
    const rightPriority = SOURCE_PRIORITY.indexOf(right.source);
    return leftPriority - rightPriority;
  });
}

export async function importSkills(discoveredBySource) {
  const entries = new Map();

  await ensureDir(REGISTRY_SKILLS_ROOT);

  for (const skills of Object.values(discoveredBySource)) {
    for (const skill of skills) {
      const skillRoot = path.join(REGISTRY_SKILLS_ROOT, skill.slug);
      const variantsRoot = path.join(skillRoot, "variants");
      const variantRoot = path.join(variantsRoot, skill.source);

      await ensureDir(variantsRoot);
      await removeDir(variantRoot);
      await copyDir(skill.sourcePath, variantRoot);

      const current = entries.get(skill.slug) ?? {
        slug: skill.slug,
        displayName: skill.displayName,
        description: skill.description,
        variants: []
      };

      current.variants.push({
        source: skill.source,
        path: path.relative(skillRoot, variantRoot).replaceAll("\\", "/"),
        originPath: skill.sourcePath
      });

      if (!current.description && skill.description) {
        current.description = skill.description;
      }

      entries.set(skill.slug, current);
    }
  }

  const skills = [...entries.values()]
    .map((entry) => ({
      ...entry,
      variants: sortVariants(entry.variants),
      canonicalVariant: sortVariants(entry.variants)[0]?.source ?? null
    }))
    .sort((left, right) => left.slug.localeCompare(right.slug));

  const registry = {
    generatedAt: new Date().toISOString(),
    skills
  };

  await writeJson(REGISTRY_INDEX_PATH, registry);
  return registry;
}

export function resolveSkill(registry, requestedName) {
  const normalized = requestedName.trim().toLowerCase();
  return registry.skills.find((entry) => {
    return entry.slug === normalized || entry.displayName.toLowerCase() === normalized;
  });
}

export async function resolveVariantPath(skill, variantSource) {
  const variant = skill.variants.find((item) => item.source === variantSource);
  if (!variant) {
    return null;
  }

  const variantPath = path.join(REGISTRY_SKILLS_ROOT, skill.slug, variant.path);
  return (await pathExists(variantPath)) ? variantPath : null;
}
