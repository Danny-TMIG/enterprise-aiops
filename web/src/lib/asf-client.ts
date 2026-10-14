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
   * Phase 1 reads status from a static JSON snapshot at /status.json
   * that tooling/validation/status_json.py generates.
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
