const WORD_PATTERN = /[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|[0-9]+/g;

/**
 * Split an identifier at word, digit, and punctuation boundaries.
 * @param value - Identifier to split into words and numeric parts.
 * @returns Lowercase word and numeric parts in source order.
 */
function splitIdentifierParts(value) {
  const segments = String(value)
    .split(/[^A-Za-z0-9]+/u)
    .flatMap((segment) => segment.match(WORD_PATTERN) ?? []);
  const parts = segments.map((part) => part.toLowerCase()).filter(Boolean);
  return parts;
}

/**
 * Find the first repeated word in an identifier.
 * @param parts - Lowercase identifier parts in their original order.
 * @returns First repeated part, or null when all parts are distinct.
 */
function firstDuplicatePart(parts) {
  const seen = new Set();

  for (const part of parts) {
    if (seen.has(part)) {
      return part;
    }
    seen.add(part);
  }

  return null;
}

/**
 * Normalize banned terms and split each into words.
 * @param terms - Banned terms from the naming policy.
 * @returns Nonempty normalized terms and their word sequences.
 */
function buildTermEntries(terms) {
  const entries = [];
  for (const value of terms) {
    const term = String(value).trim().toLowerCase();
    if (!term) {
      continue;
    }
    const entry = {
      term,
      parts: splitIdentifierParts(term),
    };
    if (entry.parts.length > 0) {
      entries.push(entry);
    }
  }
  return entries;
}

/**
 * Find a banned word or consecutive phrase in an identifier.
 * @param parts - Lowercase identifier parts in their original order.
 * @param termEntries - Normalized banned terms and their word sequences.
 * @returns First matching banned term, or null when none matches.
 */
function findBannedTerm(parts, termEntries) {
  for (const entry of termEntries) {
    const lastStart = parts.length - entry.parts.length;
    for (let index = 0; index <= lastStart; index += 1) {
      if (entry.parts.every((part, offset) => parts[index + offset] === part)) return entry.term;
    }
  }

  return null;
}

export { buildTermEntries, findBannedTerm, firstDuplicatePart, splitIdentifierParts };
