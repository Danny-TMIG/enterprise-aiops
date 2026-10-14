export interface Service {
  handle(payload: Record<string, unknown>): Record<string, unknown>;
}
