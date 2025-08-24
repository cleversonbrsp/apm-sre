# Solutions – Chapter 4: Observability of Requests

## 1. List and explain the **three pillars of observability**.

<details>
<summary>Show Solution</summary>

1. **Metrics**: Numeric data over time, like request rate, latency, and error rate. Useful for monitoring trends and triggering alerts.  
2. **Logs**: Text records of events, errors, or transactions. Useful for detailed investigation and debugging.  
3. **Traces**: End-to-end view of requests as they flow through multiple services. Useful for pinpointing latency and bottlenecks in distributed systems.  
</details>

## 2. Trace a sample HTTP request across **three microservices** and identify where you would check metrics, logs, and traces.

<details>
<summary>Show Solution</summary>

- **Scenario:** User requests `/checkout` in an e-commerce app.  
  - **Microservice A:** API Gateway → Check **metrics** (request rate, latency)  
  - **Microservice B:** Payment Service → Check **traces** to see request flow and latency  
  - **Microservice C:** Database Service → Check **logs** for query errors or timeouts  

**Explanation:** Metrics give the overall health, traces show the journey of the request, and logs provide the detailed context for failures.
</details>

## 3. Explain why logs alone are not enough to debug issues in a distributed system.

<details>
<summary>Show Solution</summary>

- Logs are **local** to each service and can be overwhelming in large systems.  
- They don’t show the **end-to-end request flow**, making it hard to correlate events across services.  
- Traces and metrics are needed to understand request latency, identify bottlenecks, and provide a holistic view of system health.  
</details>

## 4. Imagine a web app suddenly becomes slow. Which observability tool (metrics, logs, or traces) would you check first and why?

<details>
<summary>Show Solution</summary>

- **First check:** **Metrics**  
  - Reason: Metrics provide a quick overview of which service is slow (e.g., increased latency or error rate).  
- **Next:** **Traces**  
  - Identify where in the request flow the slowdown occurs (e.g., API gateway, microservice, database).  
- **Finally:** **Logs**  
  - Examine specific error messages or exceptions causing the delay.  
</details>

## 5. Bonus: Write down 3 PromQL queries you could use to troubleshoot request latency.

<details>
<summary>Show Solution</summary>

1. **Average response time per endpoint**:
```

avg(http\_request\_duration\_seconds\_bucket) by (handler)

```

2. **95th percentile latency for all requests**:  
```

histogram\_quantile(0.95, sum(rate(http\_request\_duration\_seconds\_bucket\[5m])) by (le))

```

3. **Request error rate**:  
```

sum(rate(http\_requests\_total{status=\~"5.."}\[5m])) / sum(rate(http\_requests\_total\[5m]))

```
</details>