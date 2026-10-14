import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { ASFClient, type GovernedOutcomeView } from "../lib/asf-client.ts";

@customElement("asf-app")
export class ASFApp extends LitElement {
  static styles = css`
    :host {
      display: block;
      font-family: ui-monospace, "SF Mono", Menlo, monospace;
      color: #e8e8e8;
      background: #0a0a0a;
      min-height: 100vh;
      padding: 2rem;
      box-sizing: border-box;
    }
    h1 { font-weight: 400; letter-spacing: 0.05em; }
    .status { margin-top: 1rem; padding: 1rem; border: 1px solid #333; }
    .line { padding: 0.25rem 0; }
    .ok { color: #6fbf73; }
    .warn { color: #d4a259; }
    .err { color: #c96a6a; }
  `;

  @state() private outcome: GovernedOutcomeView | null = null;
  @state() private error: string | null = null;

  private client = new ASFClient();

  async connectedCallback(): Promise<void> {
    super.connectedCallback();
    try {
      this.outcome = await this.client.fetchLatestOutcome();
    } catch (e) {
      this.error = e instanceof Error ? e.message : String(e);
    }
  }

  render() {
    return html`
      <h1>Aether Sovereign Fabric</h1>
      <p>Frontend Phase 1 — reads <code>GovernedOutcome</code>.</p>
      ${this.error
        ? html`<div class="status err">Error: ${this.error}</div>`
        : this.outcome
          ? html`
              <div class="status">
                <div class="line ok">status: ${this.outcome.status}</div>
                <div class="line">components_total: ${this.outcome.componentsTotal}</div>
                <div class="line">tracked_files: ${this.outcome.trackedFiles}</div>
                <div class="line">verdict: ${this.outcome.verdict}</div>
              </div>
            `
          : html`<div class="status">Loading…</div>`}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "asf-app": ASFApp;
  }
}
