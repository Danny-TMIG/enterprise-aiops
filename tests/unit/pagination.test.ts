import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/pagination.ts';

describe('Pagination', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-pagination label="hi"></asf-pagination>`;
    el = document.querySelector('asf-pagination') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-pagination');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-pagination-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
