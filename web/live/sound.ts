import { button, element } from '#web/dom.ts';

export class SoundControls {
  readonly view = element('fieldset');

  private readonly prompt = element('textarea');

  private readonly apply = button('Apply sound prompt');

  private pending: string | undefined;

  /**
   * Build the sound prompt controls in their disabled state.
   * @param initialPrompt - The workflow's starting sound prompt.
   */
  constructor(initialPrompt: string) {
    this.prompt.value = initialPrompt;
    this.prompt.maxLength = 1000;
    this.prompt.rows = 2;
    const label = element('label', 'Sound prompt ');
    label.append(this.prompt);
    this.view.append(
      element('legend', 'Sound'),
      label,
      this.apply,
      element('p', 'Describe the sound briefly. Leave blank to use the picture alone.'),
    );
    // eslint-disable-next-line local/no-trivial-functions -- Applying sound queues the prompt and prevents duplicate submission.
    this.apply.addEventListener('click', () => {
      this.pending = this.prompt.value;
      this.apply.disabled = true;
    });
    this.setReady(false);
  }

  /**
   * Enable sound input only when the session accepts changes.
   * @param ready - Whether the model accepts live controls.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Both controls follow session readiness while a queued prompt keeps Apply disabled.
  setReady(ready: boolean): void {
    this.prompt.disabled = !ready;
    this.apply.disabled = !ready || this.pending !== undefined;
  }

  /**
   * Consume the next sound prompt queued by the user.
   * @returns The queued prompt, or undefined when none is waiting.
   */
  takePrompt(): string | undefined {
    const value = this.pending;
    this.pending = undefined;
    return value;
  }
}
