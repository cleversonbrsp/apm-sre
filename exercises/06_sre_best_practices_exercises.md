# Solutions – Chapter 6: SRE Best Practices in Handling Requests

## 1. Design a **retry strategy** for a microservice request. Which backoff policy would you use (fixed, exponential, jitter)?

<details>
<summary>Show Solution</summary>

**Recommended Strategy:** Exponential Backoff with Jitter  

- **Fixed:** Retry after a constant delay (simple but can cause thundering herd).  
- **Exponential:** Delay doubles after each retry (reduces load on a failing service).  
- **Jitter:** Adds randomness to the delay (prevents synchronized retries across clients).  

**Example:**  
- 1st retry → 200ms + random(0-100ms)  
- 2nd retry → 400ms + random(0-100ms)  
- 3rd retry → 800ms + random(0-100ms)  
- Stop after 5 retries or if request succeeds.
</details>

## 2. Compare how **observability differs** in monolithic vs. microservices architectures.

<details>
<summary>Show Solution</summary>

- **Monolithic:**  
  - Single process → easier to collect metrics and logs.  
  - Tracing is simpler; request flow is mostly internal.  

- **Microservices:**  
  - Multiple independent services → must track distributed traces.  
  - Logs must be centralized to correlate events across services.  
  - Metrics are aggregated per service; overall system view is required.  
</details>

## 3. Write an example of a **graceful degradation plan** for a search service.

<details>
<summary>Show Solution</summary>

- **Scenario:** Search service is down.  
- **Plan:**  
  1. Show cached search results instead of real-time results.  
  2. Display a message: "Search is currently slow, showing cached results."  
  3. Log degraded requests for later review.  
  4. Continue serving other parts of the website without interruption.
</details>

## 4. Create a **checklist** for monitoring HTTP requests in production environments.

<details>
<summary>Show Solution</summary>

**Checklist:**  
- [ ] Monitor request rate (throughput)  
- [ ] Track latency (avg, p95, p99)  
- [ ] Measure error rates (4xx, 5xx)  
- [ ] Instrument all microservices with logs and traces  
- [ ] Set up alerts for abnormal behavior  
- [ ] Use dashboards to visualize trends  
- [ ] Ensure fallback or circuit breaker strategies are active
</details>

## 5. Bonus: Define an **SLO** for an e-commerce checkout service (latency and error rate).

<details>
<summary>Show Solution</summary>

- **Service Level Objective (SLO):**  
  - **Latency:** 99% of checkout requests should complete within 500ms.  
  - **Error Rate:** No more than 0.5% of requests should fail.  

- **Rationale:** Sets measurable targets for reliability and performance. Can be used with an **error budget** to guide SRE decisions.
</details>
