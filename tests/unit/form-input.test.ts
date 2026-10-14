import { describe, it, expect, beforeEach } from 'vitest';
import '../../public/src/components/form-input.ts';

describe('FormInput', () => {
  let el: HTMLElement;

  beforeEach(() => {
    document.body.innerHTML = `<asf-form-input label="hi"></asf-form-input>`;
    el = document.querySelector('asf-form-input') as HTMLElement;
  });

  it('renders a button with the label', async () => {
    await customElements.whenDefined('asf-form-input');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  });

  it('dispatches activate event on click', async () => {
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('asf-form-input-activate', () => { fired = true; });
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  });
});
