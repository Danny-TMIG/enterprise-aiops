import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/dropdown.ts';

describe('Dropdown', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-dropdown label="hi"></asf-dropdown>`;
    el = document.querySelector('asf-dropdown') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-dropdown');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-dropdown-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
