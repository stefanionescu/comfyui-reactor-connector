import { button, element } from "./dom.ts";

export class SoundControls {
  readonly view = element("fieldset");
  private readonly prompt = element("textarea");
  private readonly apply = button("Apply sound prompt");
  private pending: string | undefined;

  constructor(initialPrompt: string) {
    this.prompt.value = initialPrompt;
    this.prompt.maxLength = 1000;
    this.prompt.rows = 2;
    const label = element("label", "Sound prompt ");
    label.append(this.prompt);
    this.view.append(
      element("legend", "Sound"),
      label,
      this.apply,
      element("p", "Describe the sound briefly. Leave blank to use the picture alone."),
    );
    this.apply.addEventListener("click", () => {
      this.pending = this.prompt.value;
      this.apply.disabled = true;
    });
    this.setReady(false);
  }

  setReady(ready: boolean): void {
    this.prompt.disabled = !ready;
    this.apply.disabled = !ready || this.pending !== undefined;
  }

  takePrompt(): string | undefined {
    const value = this.pending;
    this.pending = undefined;
    return value;
  }
}
