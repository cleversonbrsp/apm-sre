# Chapter 5: APM Concepts with SigNoz

## 5.1 What is APM?
APM (Application Performance Monitoring) is the practice of monitoring and managing the performance and availability of software applications.  
It helps SREs and developers understand:
- How requests perform across services  
- Where bottlenecks exist  
- How users experience the application  

**Analogy:** APM is like having CCTV cameras inside a restaurant kitchen. Instead of just knowing customers are waiting, you can see *why* food is delayed (e.g., slow chef, missing ingredients).

## 5.2 Key Features of APM
- **Request Tracing**: Follow a request across multiple services.  
- **Error Tracking**: Identify failing services or endpoints.  
- **Performance Metrics**: Response time, throughput, error rate.  
- **Dashboards**: Visualize service health in real time.  

## 5.3 Introduction to SigNoz
SigNoz is an open-source APM and observability platform. It provides metrics, logs, and traces in one place.  
- Built on OpenTelemetry  
- Alternative to commercial APM tools (like Datadog, New Relic)  
- Self-hosted, making it great for cost-sensitive teams  

## 5.4 How Data Flows into SigNoz
1. Application generates telemetry data (metrics, logs, traces).  
2. OpenTelemetry Collector receives the data.  
3. Collector exports the data to SigNoz backend.  
4. SigNoz UI visualizes and analyzes the data.  

## 5.5 Example: OpenTelemetry Collector Sending Data to SigNoz
receivers:  
  otlp:  
    protocols:  
      grpc:  
      http:  

exporters:  
  otlp:  
    endpoint: "http://localhost:4317"  

service:  
  pipelines:  
    traces:  
      receivers: [otlp]  
      exporters: [otlp]  

## 5.6 Real-World Scenario
Imagine a payment service in a microservices architecture.  
- APM shows that 20% of requests are taking 5 seconds instead of 200ms.  
- Traces reveal the delay is caused by the database query.  
- The SRE team can then optimize the database or add caching.  

## 5.7 Exercises
1. Install SigNoz locally using Docker or Kubernetes.  
2. Send a sample trace from a demo application to SigNoz.  
3. Compare metrics of a slow vs. fast request using SigNoz dashboards.  
4. Identify a bottleneck in a multi-service application using SigNoz traces.  
