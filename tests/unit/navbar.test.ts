import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/navbar.ts';

describe('Navbar', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-navbar label="hi"></asf-navbar>`;
    el = document.querySelector('asf-navbar') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-navbar');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-navbar-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
