import fs from "node:fs/promises";
import path from "node:path";

export async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

export async function ensureDir(targetPath) {
  await fs.mkdir(targetPath, { recursive: true });
}

export async function readJson(targetPath, fallback = null) {
  if (!(await pathExists(targetPath))) {
    return fallback;
  }

  const raw = await fs.readFile(targetPath, "utf8");
  return JSON.parse(raw);
}

export async function writeJson(targetPath, value) {
  await ensureDir(path.dirname(targetPath));
  await fs.writeFile(targetPath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

export async function copyDir(sourcePath, destPath) {
  await fs.cp(sourcePath, destPath, {
    recursive: true,
    force: true,
    dereference: true,
    filter: (source) => {
      const baseName = path.basename(source);
      if (baseName === "__pycache__") {
        return false;
      }
      if (baseName.endsWith(".pyc")) {
        return false;
      }
      return true;
    }
  });
}

export async function removeDir(targetPath) {
  if (await pathExists(targetPath)) {
    await fs.rm(targetPath, { recursive: true, force: true });
  }
}

export async function listDirectories(rootPath) {
  const entries = await fs.readdir(rootPath, { withFileTypes: true });
  const directories = [];

  for (const entry of entries) {
    if (entry.isDirectory()) {
      directories.push(entry.name);
      continue;
    }

    if (entry.isSymbolicLink()) {
      try {
        const stats = await fs.stat(path.join(rootPath, entry.name));
        if (stats.isDirectory()) {
          directories.push(entry.name);
        }
      } catch {
        // Skip broken links.
      }
    }
  }

  return directories;
}
