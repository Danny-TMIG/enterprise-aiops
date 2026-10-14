import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/tooltip.ts';

describe('Tooltip', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-tooltip label="hi"></asf-tooltip>`;
    el = document.querySelector('asf-tooltip') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-tooltip');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-tooltip-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
