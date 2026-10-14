import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/footer.ts';

describe('Footer', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-footer label="hi"></asf-footer>`;
    el = document.querySelector('asf-footer') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-footer');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-footer-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
