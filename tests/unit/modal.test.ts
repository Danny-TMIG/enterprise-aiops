import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/modal.ts';

describe('Modal', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-modal label="hi"></asf-modal>`;
    el = document.querySelector('asf-modal') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-modal');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-modal-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
