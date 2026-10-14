import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/carousel.ts';

describe('Carousel', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-carousel label="hi"></asf-carousel>`;
    el = document.querySelector('asf-carousel') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-carousel');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-carousel-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
