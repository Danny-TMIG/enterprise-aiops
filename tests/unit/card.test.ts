import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/card.ts';

describe('Card', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-card label="hi"></asf-card>`;
    el = document.querySelector('asf-card') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-card');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-card-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
