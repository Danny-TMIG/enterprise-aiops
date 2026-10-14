import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/tabs.ts';

describe('Tabs', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-tabs label="hi"></asf-tabs>`;
    el = document.querySelector('asf-tabs') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-tabs');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-tabs-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
