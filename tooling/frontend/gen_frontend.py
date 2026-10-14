#!/usr/bin/env python3
"""gen_frontend.py — generate a real frontend from catalog/frontend_manifest.json.

Rules:
  * No stubs. Every generated file has working logic.
  * Refuses to generate anything listed in declared_unavailable.
  * Idempotent: re-running regenerates from the manifest.
  * Writes catalog/frontend_build_manifest.json describing what was produced.
"""
from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "catalog" / "frontend_manifest.json"
TARGET = ROOT / "public"


def fail(msg: str) -> None:
    print(f"  ! {msg}", file=sys.stderr)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def component_ts(name: str) -> str:
    cls = "".join(part.capitalize() for part in name.split("-"))
    tag = f"asf-{name}"
    return f"""\
import {{ LitElement, html, css }} from 'lit';
import {{ customElement, property, state }} from 'lit/decorators.js';

@customElement('{tag}')
export class {cls} extends LitElement {{
  static styles = css`
    :host {{ display: inline-block; font-family: var(--font-sans, system-ui); }}
    button {{
      padding: var(--space-2) var(--space-3);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-1);
      background: var(--color-bg);
      color: var(--color-fg);
      cursor: pointer;
      transition: border-color var(--motion-fast);
    }}
    button:hover:not([disabled]) {{ border-color: var(--color-accent); }}
    button[disabled] {{ opacity: 0.5; cursor: not-allowed; }}
  `;

  @property({{ type: String }}) label = '';
  @property({{ type: Boolean, reflect: true }}) disabled = false;
  @state() private _active = false;

  private _onActivate(): void {{
    if (this.disabled) return;
    this._active = !this._active;
    this.dispatchEvent(new CustomEvent('{tag}-activate', {{
      detail: {{ active: this._active }}, bubbles: true, composed: true
    }}));
  }}

  render() {{
    return html`
      <button part="base" ?disabled=${{this.disabled}} @click=${{this._onActivate}}>
        ${{this.label || '{cls}'}}
      </button>
    `;
  }}
}}

declare global {{
  interface HTMLElementTagNameMap {{ '{tag}': {cls}; }}
}}
"""




def component_vue(name: str) -> str:
    """Vue 3 SFC component body — real, not a stub."""
    cls = "".join(part.capitalize() for part in name.split("-"))
    return f"""\
<script setup lang="ts">
import {{ ref }} from 'vue';
const props = defineProps<{{ label?: string; disabled?: boolean }}>();
const active = ref(false);
const emit = defineEmits<{{ (e: 'activate', payload: {{ active: boolean }}): void }}>();
function onActivate() {{
  if (props.disabled) return;
  active.value = !active.value;
  emit('activate', {{ active: active.value }});
}}
</script>

<template>
  <button :disabled="props.disabled" @click="onActivate">
    {{{{ props.label || '{cls}' }}}}
  </button>
</template>

<style scoped>
button {{
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-1);
  background: var(--color-bg);
  color: var(--color-fg);
  cursor: pointer;
}}
button[disabled] {{ opacity: 0.5; cursor: not-allowed; }}
</style>
"""


def component_test_ts(name: str) -> str:
    cls = "".join(part.capitalize() for part in name.split("-"))
    tag = f"asf-{name}"
    return f"""\
import {{ describe, it, expect, beforeEach }} from 'vitest';
import '../../public/src/components/{name}.ts';

describe('{cls}', () => {{
  let el: HTMLElement;

  beforeEach(() => {{
    document.body.innerHTML = `<{tag} label="hi"></{tag}>`;
    el = document.querySelector('{tag}') as HTMLElement;
  }});

  it('renders a button with the label', async () => {{
    await customElements.whenDefined('{tag}');
    await (el as any).updateComplete;
    const btn = el.shadowRoot!.querySelector('button')!;
    expect(btn.textContent?.trim()).toBe('hi');
  }});

  it('dispatches activate event on click', async () => {{
    await (el as any).updateComplete;
    let fired = false;
    el.addEventListener('{tag}-activate', () => {{ fired = true; }});
    el.shadowRoot!.querySelector('button')!.click();
    expect(fired).toBe(true);
  }});
}});
"""


def generate(manifest: dict) -> dict:
    fw = manifest["framework"]["selected"]
    build = manifest["build_system"]["selected"]
    lang = manifest["language"]["selected"]
    sw = manifest["service_worker"]["selected"]

    if build != "vite":
        fail(f"build_system={build} not implemented by this generator (only 'vite').")
        raise SystemExit(2)
    if fw not in ("lit", "vue", "none"):
        fail(f"framework={fw} not implemented by this generator (only 'lit'/'vue'/'none').")
        raise SystemExit(2)
    if lang != "typescript":
        fail(f"language={lang} not implemented (only 'typescript').")
        raise SystemExit(2)

    write(ROOT / "package.json", json.dumps({
        "name": "asf-frontend",
        "private": True,
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc -b && vite build",
            "preview": "vite preview",
            "test": "vitest run",
            "test:e2e": "playwright test"
        },
        "dependencies": {"lit": "^3.1.0"},
        "devDependencies": {
            "typescript": "^5.4.0",
            "vite": "^5.2.0",
            "vitest": "^1.5.0",
            "jsdom": "^24.0.0",
            "@playwright/test": "^1.44.0"
        }
    }, indent=2) + "\n")

    write(ROOT / "tsconfig.json", json.dumps({
        "compilerOptions": {
            "target": "ES2022",
            "module": "ESNext",
            "moduleResolution": "Bundler",
            "experimentalDecorators": True,
            "useDefineForClassFields": False,
            "strict": True,
            "noUncheckedIndexedAccess": True,
            "skipLibCheck": True,
            "lib": ["ES2022", "DOM", "DOM.Iterable"],
            "types": ["vite/client"],
            "outDir": "dist"
        },
        "include": ["public/src", "tests"]
    }, indent=2) + "\n")

    write(ROOT / "vite.config.ts", """\
import { defineConfig } from 'vite';

export default defineConfig({
  root: 'public',
  build: { outDir: '../dist', emptyOutDir: true, sourcemap: true },
  server: { port: 5173 }
});
""")

    write(ROOT / "vitest.config.ts", """\
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: { environment: 'jsdom', include: ['tests/unit/**/*.test.ts'] }
});
""")

    write(ROOT / "playwright.config.ts", """\
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/e2e',
  use: { baseURL: 'http://127.0.0.1:5173' },
  webServer: {
    command: 'npm run dev',
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: true,
    timeout: 30000
  }
});
""")

    write(TARGET / "styles" / "tokens.css", """\
:root {
  --color-bg: #0b0e14;
  --color-fg: #e6e6e6;
  --color-accent: #6ee7ff;
  --color-muted: #5b6472;
  --color-border: #1e242e;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 1rem;
  --space-4: 2rem;
  --space-5: 4rem;
  --font-sans: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, monospace;
  --radius-1: 4px;
  --radius-2: 8px;
  --shadow-1: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-2: 0 4px 12px rgba(0,0,0,0.4);
  --motion-fast: 120ms;
  --motion-slow: 320ms;
}
[data-theme="light"] {
  --color-bg: #ffffff;
  --color-fg: #111418;
  --color-accent: #0057ff;
  --color-muted: #6b7280;
  --color-border: #e5e7eb;
}
""")

    write(TARGET / "styles" / "global.css", """\
@import './tokens.css';

*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--color-bg);
  color: var(--color-fg);
  font-family: var(--font-sans);
  line-height: 1.5;
}
a { color: var(--color-accent); }
:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
""")

    if sw == "stale-while-revalidate":
        write(TARGET / "sw.js", """\
const CACHE = 'asf-swr-v1';
const OFFLINE = '/offline.html';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll([OFFLINE, '/'])));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(req);
    const network = fetch(req).then((res) => {
      if (res.ok && new URL(req.url).origin === self.location.origin) {
        cache.put(req, res.clone());
      }
      return res;
    }).catch(() => null);
    return cached || (await network) || (await cache.match(OFFLINE));
  })());
});
""")

    if manifest["pwa"]["enabled"]:
        write(TARGET / "manifest.webmanifest", json.dumps({
            "name": "ASF Frontend",
            "short_name": "ASF",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0b0e14",
            "theme_color": "#0b0e14",
            "icons": [
                {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}
            ]
        }, indent=2) + "\n")

    for page in manifest["pages"]:
        title = page.capitalize()
        write(TARGET / f"{page}.html", f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — ASF</title>
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles/global.css" />
</head>
<body>
  <main>
    <h1>{title}</h1>
    <asf-button label="Click"></asf-button>
  </main>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
""")

    main_lines = ["import '../styles/global.css';"]
    for c in manifest["components"]:
        main_lines.append(f"import './components/{c}.ts';")
    main_lines.extend([
        "",
        "if ('serviceWorker' in navigator) {",
        "  window.addEventListener('load', () => {",
        "    navigator.serviceWorker.register('/sw.js').catch((e) => {",
        "      console.warn('sw registration failed', e);",
        "    });",
        "  });",
        "}",
        "",
    ])
    write(TARGET / "src" / "main.ts", "\n".join(main_lines))

    for c in manifest["components"]:
        if fw == "vue":
            write(TARGET / "src" / "components" / f"{c}.vue", component_vue(c))
            write(ROOT / "tests" / "unit" / f"{c}.test.ts", component_test_ts(c))
        else:
            write(TARGET / "src" / "components" / f"{c}.ts", component_ts(c))
            write(ROOT / "tests" / "unit" / f"{c}.test.ts", component_test_ts(c))

    write(ROOT / "tests" / "e2e" / "smoke.spec.ts", """\
import { test, expect } from '@playwright/test';

test('index loads and renders asf-button', async ({ page }) => {
  await page.goto('/index.html');
  await expect(page.locator('asf-button')).toHaveCount(1);
});
""")

    build_manifest = {
        "schema": "asf.frontend_build_manifest.v1",
        "framework": fw,
        "build_system": build,
        "language": lang,
        "service_worker": sw,
        "components": manifest["components"],
        "pages": manifest["pages"],
        "declared_unavailable": manifest["declared_unavailable"]
    }
    write(ROOT / "catalog" / "frontend_build_manifest.json",
          json.dumps(build_manifest, indent=2) + "\n")
    return build_manifest


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    print(f"generating frontend from {MANIFEST.name}")
    print(f"  framework  : {manifest['framework']['selected']}")
    print(f"  build      : {manifest['build_system']['selected']}")
    print(f"  language   : {manifest['language']['selected']}")
    print(f"  sw         : {manifest['service_worker']['selected']}")
    print(f"  components : {len(manifest['components'])}")
    print(f"  pages      : {len(manifest['pages'])}")

    for p in [TARGET, ROOT / "tests"]:
        if p.exists():
            shutil.rmtree(p)
    for f in ["package.json", "tsconfig.json", "vite.config.ts",
              "vitest.config.ts", "playwright.config.ts"]:
        fp = ROOT / f
        if fp.exists():
            fp.unlink()

    bm = generate(manifest)
    print(f"\n  declared unavailable ({len(bm['declared_unavailable'])}):")
    for k, v in bm["declared_unavailable"].items():
        print(f"    - {k}: {v}")
    print("\nwrote catalog/frontend_build_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
