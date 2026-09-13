import { button, element } from '#web/dom.ts';
import { message } from '#web/localization.ts';

export class SoundControls {
  readonly view = element('section');

  readonly status = element('p');

  private readonly prompt = element('textarea');

  private readonly apply = button(message('sound.applyPrompt'), 'submit');

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
    const form = element('form');
    this.status.setAttribute('role', 'status');
    this.view.className = 'reactor-prompt';
    const actions = element('div');
    actions.className = 'reactor-prompt-actions';
    actions.append(this.status, this.apply);
    form.append(label, element('small', message('sound.promptNotice')), actions);
    this.view.append(form);

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      this.pending = this.prompt.value;
      this.apply.disabled = true;
    });
    this.setReady(false);
  }

  /**
   * Enable sound input only when the session accepts changes.
   * @param ready - Whether the model accepts live controls.
   */
  setReady(ready: boolean): void {
    this.prompt.disabled = !ready;
    if (!ready) {
      this.apply.disabled = true;
      return;
    }
    this.apply.disabled = this.pending !== undefined;
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
