import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

@customElement('asf-carousel')
export class Carousel extends LitElement {
  static styles = css`
    :host { display: inline-block; font-family: var(--font-sans, system-ui); }
    button {
      padding: var(--space-2) var(--space-3);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-1);
      background: var(--color-bg);
      color: var(--color-fg);
      cursor: pointer;
      transition: border-color var(--motion-fast);
    }
    button:hover:not([disabled]) { border-color: var(--color-accent); }
    button[disabled] { opacity: 0.5; cursor: not-allowed; }
  `;

  @property({ type: String }) label = '';
  @property({ type: Boolean, reflect: true }) disabled = false;
  @state() private _active = false;

  private _onActivate(): void {
    if (this.disabled) return;
    this._active = !this._active;
    this.dispatchEvent(new CustomEvent('asf-carousel-activate', {
      detail: { active: this._active }, bubbles: true, composed: true
    }));
  }

  render() {
    return html`
      <button part="base" ?disabled=${this.disabled} @click=${this._onActivate}>
        ${this.label || 'Carousel'}
      </button>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap { 'asf-carousel': Carousel; }
}
