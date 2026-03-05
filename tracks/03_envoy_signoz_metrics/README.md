# Track 3 – Envoy + SigNoz Metrics

Labs and references for collecting **Envoy Proxy metrics** and visualizing them in SigNoz using OpenTelemetry.

## Audience

SREs or platform engineers who run Envoy (or similar proxies) and want to send metrics to SigNoz for dashboards and alerting.

## Suggested order

1. Read the track lab README and prerequisites.
2. Deploy the OTel Collector and Envoy with the provided manifests.
3. Generate traffic and import the SigNoz Envoy dashboard to validate metrics.

## Contents

- `signoz-envoy-proxy/` – Step-by-step lab: OTel Collector, Envoy stats sink (OTLP), backend (e.g. httpbin), K8s manifests, and SigNoz dashboard import.
