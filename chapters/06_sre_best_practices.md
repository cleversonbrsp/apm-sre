# Chapter 6: SRE Best Practices in Handling Requests

## 6.1 Microservices vs Monolithic Architectures
- **Monolithic**: The entire application runs as a single unit.  
  - Pros: Simple to deploy, easier to start with.  
  - Cons: Hard to scale, one bug can impact the whole system.  

- **Microservices**: Application is split into smaller, independent services.  
  - Pros: Scalable, easier to maintain parts of the system.  
  - Cons: Requests travel across many services, making observability and reliability harder.  

**Analogy:**  
- Monolithic = A single big factory producing everything.  
- Microservices = Multiple specialized workshops that depend on each other.  

## 6.2 Best Practices for Handling Requests
1. **Instrument Everything**  
   - Use observability tools (metrics, logs, traces) for all services.  

2. **Use Timeouts and Retries**  
   - Prevent a single slow request from blocking the entire system.  

3. **Implement Circuit Breakers**  
   - Stop sending requests to unhealthy services until they recover.  

4. **Monitor SLIs, SLOs, and Error Budgets**  
   - SLIs (Service Level Indicators): Latency, error rate.  
   - SLOs (Service Level Objectives): Targets (e.g., 99.9% of requests under 200ms).  
   - Error Budgets: Allowable margin for failures.  

5. **Load Balance Effectively**  
   - Ensure requests are distributed evenly.  
   - Use strategies like round robin, least connections, or weighted balancing.  

6. **Graceful Degradation**  
   - When a service fails, provide a fallback.  
   - Example: If a recommendation service is down, show static suggestions instead of failing the whole page.  

## 6.3 Real-World Scenario
A payment request fails intermittently in a microservices system:  
1. The SRE team checks load balancer metrics and sees one node is overloaded.  
2. Traces show that requests are getting stuck in the payment service.  
3. Logs confirm that the database is timing out.  
4. The team applies caching and adjusts database query limits.  

## 6.4 Checklist for SREs Monitoring Requests
- [ ] Are all services instrumented with observability?  
- [ ] Are timeouts and retries configured properly?  
- [ ] Is the load balancer distributing traffic fairly?  
- [ ] Are SLIs and SLOs defined and tracked?  
- [ ] Is there a fallback plan for failed services?  

## 6.5 Exercises
1. Design a retry strategy for a microservice request. What backoff policy would you use?  
2. Compare how observability differs in monolithic vs microservices architectures.  
3. Write an example of a graceful degradation plan for a search service.  
4. Create a checklist for monitoring HTTP requests in production environments.  
