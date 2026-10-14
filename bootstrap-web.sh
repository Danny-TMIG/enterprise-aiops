cd ~/aether && bash <<'BASH_EOF'
set -euo pipefail

# ================================================================ web/ tree
mkdir -p web/src web/public web/tests

cat > web/package.json <<'JSON'
{
  "name": "@asf/web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "ASF web frontend — reads GovernedOutcome, renders cognitive state",
  "license": "Apache-2.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "e2e": "playwright test",
    "typecheck": "tsc --noEmit",
    "lint": "echo 'lint: configured later'"
  },
  "dependencies": {
    "lit": "^3.1.0",
    "idb": "^8.0.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.45.0",
    "@types/node": "^20.11.0",
    "jsdom": "^24.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vitest": "^1.6.0"
  }
}
JSON

cat > web/tsconfig.json <<'JSON'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable", "WebWorker"],
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "useDefineForClassFields": false,
    "experimentalDecorators": true,
    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,
    "noEmit": true
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"]
}
JSON

cat > web/vite.config.ts <<'TS'
import { defineConfig } from "vite";

export default defineConfig({
  root: ".",
  publicDir: "public",
  build: {
    outDir: "dist",
    target: "es2022",
    sourcemap: true,
  },
  server: {
    port: 5173,
    strictPort: true,
  },
});
TS

cat > web/vitest.config.ts <<'TS'
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["tests/**/*.test.ts"],
    exclude: ["tests/**/*.e2e.ts", "node_modules/**"],
  },
});
TS

cat > web/playwright.config.ts <<'TS'
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  testMatch: "**/*.e2e.ts",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: {
    command: "npm run dev",
    port: 5173,
    reuseExistingServer: true,
  },
});
TS

cat > web/.gitignore <<'GITIGNORE'
node_modules/
dist/
.vite/
playwright-report/
test-results/
GITIGNORE

# ---------------------------------------------------------------- public/
cat > web/public/index.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Aether Sovereign Fabric</title>
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'" />
</head>
<body>
  <asf-app></asf-app>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
HTML

cat > web/public/manifest.webmanifest <<'JSON'
{
  "name": "Aether Sovereign Fabric",
  "short_name": "ASF",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a0a0a",
  "theme_color": "#0a0a0a",
  "icons": []
}
JSON

# ---------------------------------------------------------------- src/
cat > web/src/main.ts <<'TS'
import "./components/asf-app.ts";
TS

cat > web/src/components/asf-app.ts <<'TS'
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
TS

cat > web/src/lib/asf-client.ts <<'TS'
/**
 * ASFClient — the frontend's only interface to the fabric.
 *
 * It reads status. It does not authorize, execute, or construct
 * authority objects. See contracts/predicates/authority.py for what
 * the frontend must never do.
 */

export interface GovernedOutcomeView {
  status: string;
  componentsTotal: number;
  trackedFiles: number;
  verdict: string;
}

export class ASFClient {
  /**
   * Phase 1 reads status from the local status.py output that a
   * sidecar server publishes. There is no ASF server yet — the
   * transport decision (GOV-DEC-001 / CMP-DEC-001) is Open.
   *
   * For Phase 1 we read a static JSON snapshot at /status.json
   * that the ASF CLI can generate.
   */
  async fetchLatestOutcome(): Promise<GovernedOutcomeView> {
    const res = await fetch("/status.json", {
      headers: { accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error(`status fetch failed: ${res.status}`);
    }
    const data = (await res.json()) as {
      tree?: { components_total?: number };
      tracked?: { tracked_files?: number };
      verdict?: { status?: string };
    };
    return {
      status: "ok",
      componentsTotal: data.tree?.components_total ?? 0,
      trackedFiles: data.tracked?.tracked_files ?? 0,
      verdict: data.verdict?.status ?? "UNKNOWN",
    };
  }
}
TS

# ---------------------------------------------------------------- tests
cat > web/tests/asf-client.test.ts <<'TS'
import { describe, it, expect, vi } from "vitest";
import { ASFClient } from "../src/lib/asf-client.ts";

describe("ASFClient", () => {
  it("parses status.json into a GovernedOutcomeView", async () => {
    const payload = {
      tree: { components_total: 150 },
      tracked: { tracked_files: 3174 },
      verdict: { status: "OK" },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify(payload), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      ),
    );

    const client = new ASFClient();
    const view = await client.fetchLatestOutcome();
    expect(view.componentsTotal).toBe(150);
    expect(view.trackedFiles).toBe(3174);
    expect(view.verdict).toBe("OK");
  });

  it("fails closed when the response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("", { status: 503 })),
    );
    const client = new ASFClient();
    await expect(client.fetchLatestOutcome()).rejects.toThrow(/status fetch failed/);
  });

  it("defaults to zero when fields are missing", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response("{}", {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    const client = new ASFClient();
    const view = await client.fetchLatestOutcome();
    expect(view.componentsTotal).toBe(0);
    expect(view.verdict).toBe("UNKNOWN");
  });
});
TS

cat > web/tests/app.e2e.ts <<'TS'
import { test, expect } from "@playwright/test";

test("asf-app renders the fabric status", async ({ page }) => {
  // Serve a status.json fixture for the test
  await page.route("**/status.json", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        tree: { components_total: 150 },
        tracked: { tracked_files: 3174 },
        verdict: { status: "OK" },
      }),
    });
  });

  await page.goto("/");
  await expect(page.locator("h1")).toHaveText("Aether Sovereign Fabric");
  await expect(page.locator(".status .ok")).toContainText("verdict: OK");
  await expect(page.locator(".status")).toContainText("components_total: 150");
});
TS

# ================================================================ ASF integration
# tooling/validation/status_json.py — emit a JSON snapshot for the frontend
cat > tooling/validation/status_json.py <<'PY'
#!/usr/bin/env python3
"""Emit a static status.json snapshot for the frontend to read.

Wraps tooling/validation/status.py --json and writes the result to
web/public/status.json. Read-only with respect to the repo.

Run:  python3 tooling/validation/status_json.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parent.parent


def main() -> int:
    root = _repo_root()
    script = root / "tooling" / "validation" / "status.py"
    out = root / "web" / "public" / "status.json"

    r = subprocess.run(
        [sys.executable, str(script), "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode not in (0, 1):
        print(f"status.py failed: exit {r.returncode}", file=sys.stderr)
        print(r.stderr, file=sys.stderr)
        return 2

    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        print(f"status.py produced invalid JSON: {e}", file=sys.stderr)
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True))
    print(f"wrote {out.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PY
chmod +x tooling/validation/status_json.py

# Makefile targets
python3 - <<'PYEOF'
import pathlib
p = pathlib.Path("Makefile")
s = p.read_text()

additions = """

web-status:
\t@python3 tooling/validation/status_json.py

web-dev:
\t@cd web && npm run dev

web-build:
\t@cd web && npm install && npm run build

web-test:
\t@cd web && npm install && npm run test

web-e2e:
\t@cd web && npm install && npx playwright install --with-deps && npm run e2e
"""

if "web-status:" not in s:
    s = s.rstrip() + "\n" + additions
    p.write_text(s)
    print("Makefile: added web-* targets")
else:
    print("Makefile: web-* targets already present")
PYEOF

# ================================================================ web/README.md
cat > web/README.md <<'MD'
# ASF Web Frontend

## What this is

A web-based interface to Aether Cognition, Govern, and Compute. It renders
cognitive state, collects human intent, presents authorization requests,
and displays governed outcomes. It is not an orchestrator, not an agent
framework, and not a compute runtime.

## What this is not

The frontend does not authorize, does not execute, and does not construct
authority objects. It consumes `GovernedOutcome`, `ExecutionEvidence`, and
`AuthorizationDecision`; it produces `CognitiveRequest`,
`HumanDecisionSubmission`, and `ApprovalRequest`.

If a proposed feature requires the frontend to make an authority decision,
that feature is out of scope.

## Stack

| Concern | Choice | License |
|---|---|---|
| Language | TypeScript | Apache-2.0 |
| Components | Lit (Web Components) | BSD-3-Clause |
| Build | Vite | MIT |
| Unit tests | Vitest | MIT |
| E2E tests | Playwright | Apache-2.0 |
| Storage | IndexedDB via `idb` | ISC |

See `ASF-WEB-SPEC-001` for the full technology classification. Twenty-two of
the twenty-five layers in the source wishlist are deferred or rejected.

## Run

```bash
cd web
npm install
npm run dev          # http://localhost:5173
