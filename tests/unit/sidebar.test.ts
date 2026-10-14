import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/sidebar.ts';

describe('Sidebar', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-sidebar label="hi"></asf-sidebar>`;
    el = document.querySelector('asf-sidebar') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-sidebar');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-sidebar-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
