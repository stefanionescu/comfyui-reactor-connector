# CSS

Read this rule when you change a stylesheet or the style block of a component.

## Structure

- Keep shared color, spacing, type, radius, and motion tokens in one file.
- Keep feature styles with their component or import them through the stylesheet entry.
- Order rules from general styles to component states.

## Naming

### Selector and file names

- Name classes for the component or state, such as `order-card`, `order-card-title`, `is-active`, or `has-error`.
- A state class starts with `is-` or `has-`. A script toggles it. Never style it alone.
- Custom properties name the role of the value, not its appearance: `--color-surface`, `--space-2`, `--font-size-body`,
  never `--blue` or `--big-margin`.
- Theme overrides reuse the same property names under their selector and add no new ones.
- When the project uses a utility system, keep its class names. Do not write your own utility classes beside it.
