# Service Level Objectives (SLOs)

## 1. Availability
- **Target:** 99.9% uptime over a rolling 30-day window.
- **Measurement:** Successful HTTP responses (`status < 500`) divided by total valid requests.

## 2. Latency
- **Target:** 95% of API requests complete in under 250ms.
- **Measurement:** Histogram distribution of `http_request_duration_seconds`.
