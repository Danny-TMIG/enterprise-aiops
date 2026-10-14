import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/table.ts';

describe('Table', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-table label="hi"></asf-table>`;
    el = document.querySelector('asf-table') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-table');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-table-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
