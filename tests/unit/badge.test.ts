import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/badge.ts';

describe('Badge', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-badge label="hi"></asf-badge>`;
    el = document.querySelector('asf-badge') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-badge');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-badge-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
