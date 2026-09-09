export const CASE_PATTERNS = {
  camel: /^[a-z][A-Za-z]*$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  kebab: /^[a-z]+(?:-[a-z]+)*$/,
  pascal: /^[A-Z][A-Za-z]*$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  'pascal-plus': /^[A-Z][A-Za-z]*(?:\+[A-Z][A-Za-z]*)+$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  snake: /^[a-z]+(?:_[a-z]+)*$/,
  // eslint-disable-next-line security/detect-unsafe-regex -- Separators cannot match word characters, so repetitions have no overlapping matches.
  'upper-snake': /^[A-Z]+(?:_[A-Z]+)*$/,
};

export const JAVASCRIPT_DIRECTORY_PREFIXES = ['web/', 'scripts/', 'quality/'];
export const SHELL_DIRECTORY_PREFIXES = ['.mise/', '.githooks/', 'quality/'];
