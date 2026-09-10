/**
 * Pause between status requests and wake when the panel closes.
 * @param milliseconds - Time before the next request.
 * @param signal - The panel lifetime, if it is still open.
 * @returns When the delay ends or the panel closes.
 */
export async function pause(milliseconds: number, signal?: AbortSignal): Promise<void> {
  if (signal?.aborted) return;
  await new Promise<void>((fulfill) => {
    const finish = (): void => {
      clearTimeout(timer);
      signal?.removeEventListener('abort', finish);
      fulfill();
    };
    const timer = setTimeout(finish, milliseconds);
    signal?.addEventListener('abort', finish);
  });
}
