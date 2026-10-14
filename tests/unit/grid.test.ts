import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/grid.ts';

describe('Grid', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-grid label="hi"></asf-grid>`;
    el = document.querySelector('asf-grid') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-grid');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-grid-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
