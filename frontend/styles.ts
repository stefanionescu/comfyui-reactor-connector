export const settingsStyles = `
.reactor-settings {
  width: min(38rem, calc(100vw - 2rem));
  max-height: calc(100vh - 2rem);
  overflow: auto;
  border: 1px solid var(--border-color, GrayText);
  border-radius: .6rem;
  padding: 1.5rem;
  color: var(--fg-color, CanvasText);
  background: var(--comfy-menu-bg, Canvas);
  font: inherit;
}
.reactor-settings::backdrop { background: #0008; }
.reactor-settings header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.reactor-settings h2 { margin: 0; font-size: 1.3rem; }
.reactor-settings p { line-height: 1.5; }
.reactor-settings form { margin-top: 1.5rem; }
.reactor-settings fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
.reactor-settings legend { font-weight: 600; margin-bottom: .75rem; }
.reactor-settings label { display: grid; gap: .35rem; margin: .8rem 0; }
.reactor-settings input {
  box-sizing: border-box; width: 100%; padding: .55rem; border: 1px solid var(--border-color, GrayText);
  border-radius: .25rem; color: var(--input-text, CanvasText); background: var(--comfy-input-bg, Field);
  font: inherit;
}
.reactor-settings button {
  font: inherit; padding: .45rem .75rem; border: 1px solid var(--border-color, GrayText);
  border-radius: .25rem; color: var(--input-text, ButtonText); background: var(--comfy-input-bg, ButtonFace);
  cursor: pointer;
}
.reactor-settings input[type="checkbox"] { width: auto; padding: 0; margin: 0; }
.reactor-settings label:has(input[type="checkbox"]) { display: flex; align-items: center; gap: .6rem; }
.reactor-settings button:disabled { cursor: default; opacity: .55; }
.reactor-settings :focus-visible { outline: 2px solid Highlight; outline-offset: 3px; }
.reactor-settings .reactor-actions { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: .75rem; }
.reactor-settings [role="status"] { min-height: 1.5em; }
.reactor-settings summary { cursor: pointer; padding: .5rem 0; }
`;
