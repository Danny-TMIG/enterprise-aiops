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
