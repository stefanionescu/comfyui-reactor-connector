import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

function isRegularFile(root, relative) {
  // reason: Git supplies repository-relative filenames; the following checks reject symbolic links.
  // bearer:disable javascript_lang_path_traversal
  const absolute = path.join(root, relative);
  if (!fs.existsSync(absolute)) return false;
  // A file reached through a symbolic link may expose content outside the repository.
  for (let current = absolute; current !== root; current = path.dirname(current)) {
    if (fs.lstatSync(current).isSymbolicLink()) {
      throw new Error(`Use a regular repository file instead of a symbolic link: ${relative}`);
    }
  }
  return fs.statSync(absolute).isFile();
}

/**
 * List existing files that Git tracks or would include from the worktree.
 * @param root - Repository root used for the Git query and file checks.
 * @returns Sorted, unique paths relative to the repository root.
 */
export function visibleFiles(root) {
  const output = execFileSync(
    'git',
    ['-C', root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
    { encoding: 'utf8' },
  );
  const files = new Set(output.split('\0').filter(Boolean));
  return [...files].filter((relative) => isRegularFile(root, relative)).sort();
}
