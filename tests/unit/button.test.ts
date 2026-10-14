import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/button.ts';

describe('Button', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-button label="hi"></asf-button>`;
    el = document.querySelector('asf-button') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-button');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-button-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
