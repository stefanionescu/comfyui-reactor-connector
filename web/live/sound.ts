import { button, element } from '#web/dom.ts';
import { message } from '#web/localization.ts';

export class SoundControls {
  readonly view = element('fieldset');

  private readonly prompt = element('textarea');

  private readonly apply = button(message('sound.applyPrompt'));

  private pending: string | undefined;

  /**
   * Build the sound prompt controls in their disabled state.
   * @param initialPrompt - The workflow's starting sound prompt.
   * @param promptCharacterLimit - The model's maximum sound prompt length.
   */
  constructor(initialPrompt: string, promptCharacterLimit: number) {
    this.prompt.value = initialPrompt;
    this.prompt.maxLength = promptCharacterLimit;
    this.prompt.rows = 2;
    const label = element('label', message('sound.prompt'));
    label.append(this.prompt);
    this.view.append(
      element('legend', message('sound.title')),
      label,
      this.apply,
      element('p', message('sound.promptNotice')),
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
