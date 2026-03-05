# Chapter 4: Observability of Requests: Metrics, Logs, Traces

## 4.1 What is Observability?
Observability is the ability to understand the internal state of a system by examining the data it produces.  
It helps answer questions like:
- Is the system healthy?  
- Why did a request fail?  
- Where is the performance bottleneck?  

**Analogy:** Observability is like the dashboard of a car. The speedometer, fuel gauge, and warning lights give you visibility into what’s happening inside the vehicle.

## 4.2 The Three Pillars of Observability
1. **Metrics**  
   - Numeric measurements over time (e.g., request latency, error rate).  
   - Example: Average response time = 200ms.  

2. **Logs**  
   - Textual records of events.  
   - Example: “2025-08-24 10:35:01 ERROR User authentication failed.”  

3. **Traces**  
   - End-to-end view of how a single request moves through services.  
   - Useful in microservices to detect where slowdowns occur.  

## 4.3 Real-World Scenario
When a user types `google.com`, their request passes through DNS, load balancers, web servers, and databases before returning a page.  
- Metrics help you see if latency increased.  
- Logs show error messages if something failed.  
- Traces reveal which step of the journey took the longest.  

## 4.4 Example with Prometheus and OpenTelemetry
- **Prometheus** collects metrics (e.g., request rate).  
- **OpenTelemetry** captures traces and metrics for deeper analysis.  

Simple scrape configuration for metrics collection:

scrape_configs:  
  - job_name: 'app'  
    static_configs:  
      - targets: ['localhost:9090']  

## 4.5 Exercises
1. List and explain the three pillars of observability.  
2. Trace a sample HTTP request across three microservices and identify where you would check metrics, logs, and traces.  
3. Explain why logs alone are not enough to debug issues in a distributed system.  
4. Imagine a web app suddenly becomes slow. Which observability tool (metrics, logs, or traces) would you check first and why?  
