import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/select.ts';

describe('Select', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-select label="hi"></asf-select>`;
    el = document.querySelector('asf-select') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-select');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-select-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
