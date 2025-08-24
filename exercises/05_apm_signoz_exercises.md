# Solutions – Chapter 5: APM Concepts with SigNoz

## 1. Install **SigNoz locally** using Docker or Kubernetes.

<details>
<summary>Show Solution</summary>

**Docker Example:**
```bash
# Pull SigNoz Docker Compose setup
git clone https://github.com/SigNoz/signoz.git
cd signoz/deploy/
docker-compose up -d
```

**Kubernetes Example (using Helm):**

```bash
# Add SigNoz Helm repo
helm repo add signoz https://charts.signoz.io
helm repo update

# Install SigNoz
helm install signoz signoz/signoz --namespace signoz --create-namespace
```

After installation, access the UI at `http://localhost:3301` (Docker) or the Kubernetes service endpoint.

</details>

## 2. Send a sample trace from a **demo application** to SigNoz.

<details>
<summary>Show Solution</summary>

* Use OpenTelemetry SDK in your app (Node.js example):

```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const provider = new NodeTracerProvider();
provider.register();

const exporter = new OTLPTraceExporter({ url: 'http://localhost:4318/v1/traces' });
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
```

* Generate a request in the app. You should see the trace appear in SigNoz dashboard.

</details>

## 3. Compare metrics of a **slow vs. fast request** using SigNoz dashboards.

<details>
<summary>Show Solution</summary>

* Navigate to **Dashboards → Performance** in SigNoz.
* Observe metrics like **request latency**, **throughput**, and **error rate**.
* **Slow request**: Higher latency, possibly higher error rate.
* **Fast request**: Low latency, consistent response times.
* Use graphs to compare multiple endpoints or time ranges.

</details>

## 4. Identify a bottleneck in a multi-service application using SigNoz traces.

<details>
<summary>Show Solution</summary>

1. Open **Traces** in SigNoz.
2. Filter by the request you want to investigate.
3. Examine the **span waterfall** to see which service or database call took the longest.
4. Identify slow spans or repeated retries.
5. Example: Payment service calls database → database query takes 2s → delay propagated upstream.

</details>

## 5. Bonus: Research how SigNoz differs from **Datadog** or **New Relic** in terms of cost and features.

<details>
<summary>Show Solution</summary>

* **SigNoz:**

  * Open-source and self-hosted.
  * No subscription cost for software (only infra).
  * Built on OpenTelemetry → supports metrics, logs, traces.

* **Datadog / New Relic:**

  * Commercial SaaS with subscription fees.
  * Fully managed with rich integrations.
  * Often easier to start but can be expensive at scale.

**Summary:** SigNoz is cost-effective and open-source but requires infrastructure setup. Datadog/New Relic are turnkey solutions with higher cost.

</details>