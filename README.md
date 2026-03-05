# SRE Study Guide: Understanding Requests & Observability

Welcome to the **SRE Study Guide**!  
This repository is designed to help you progressively learn about HTTP requests, APIs, load balancing, observability, and SRE best practices.  
By the end of this guide, you will be able to monitor requests with **SigNoz** and apply this knowledge in your career as an SRE.

The content is organized by **learning tracks**. Each track groups theory, exercises, and labs for a specific focus.

---

## Repository structure: learning tracks

| Track | Description | Path |
|-------|-------------|------|
| **Track 1 – HTTP & Observability basics** | Chapters (HTTP, REST/gRPC/GraphQL, load balancing, observability, APM SigNoz, SRE best practices), exercises, and hands-on labs (Node.js + OTel, workshop). | [tracks/01_http_observability_basics/](tracks/01_http_observability_basics/) |
| **Track 2 – NVT Roadmap (Java + K8s)** | Material for a reference corporate environment: Java/Spring Boot on Kubernetes, Config Server, pipelines, SigNoz/OpenTelemetry. Overview, stack, SRE checklist, labs, exercises. | [tracks/02_java_k8s_nvt_roadmap/](tracks/02_java_k8s_nvt_roadmap/) |
| **Track 3 – Envoy + SigNoz metrics** | Lab for collecting Envoy Proxy metrics and visualizing them in SigNoz (OTel Collector, Envoy stats sink, K8s manifests). | [tracks/03_envoy_signoz_metrics/](tracks/03_envoy_signoz_metrics/) |

Start with **Track 1** for fundamentals; then follow **Track 2** or **Track 3** depending on your focus (Java/K8s vs proxy metrics).

---

## Track 1 – Table of contents (chapters)

1. [HTTP Requests & Responses Fundamentals](tracks/01_http_observability_basics/chapters/01_http_requests.md)  
2. [REST vs gRPC vs GraphQL](tracks/01_http_observability_basics/chapters/02_rest_vs_grpc_vs_graphql.md)  
3. [Load Balancing & Request Routing](tracks/01_http_observability_basics/chapters/03_load_balancing.md)  
4. [Observability of Requests: Metrics, Logs, Traces](tracks/01_http_observability_basics/chapters/04_observability.md)  
5. [APM Concepts with SigNoz](tracks/01_http_observability_basics/chapters/05_apm_signoz.md)  
6. [SRE Best Practices in Handling Requests](tracks/01_http_observability_basics/chapters/06_sre_best_practices.md)  

---

## Learning outcomes

After completing this study guide, you will be able to:

- Understand how HTTP requests and responses work.  
- Compare REST, gRPC, and GraphQL.  
- Configure load balancers for efficient request routing.  
- Apply the three pillars of observability (metrics, logs, traces).  
- Use **SigNoz** for application performance monitoring (APM).  
- Apply SRE best practices to handle requests in microservices and monolithic architectures.  

---

## Labs (Track 1)

### Lab 1: Node.js Application with OpenTelemetry & SigNoz

**Get hands-on experience with a complete Node.js application!**

The lab includes:

- Complete e-commerce API with user registrations, orders, and payments  
- OpenTelemetry instrumentation for traces and custom metrics  
- Docker Compose setup for easy deployment  
- SigNoz integration for visualization  
- Ready-to-run code with no complex setup  

**Quick start:**

1. Follow the instructions in [labs/01.md](tracks/01_http_observability_basics/labs/01.md)  
2. Run `docker-compose up --build`  
3. Access your instrumented app at http://localhost:3000  
4. View traces and metrics in SigNoz at http://localhost:3301  

**Perfect for:** Learning OpenTelemetry instrumentation, distributed tracing, custom metrics, and APM with SigNoz.

More labs (example application, workshop instrumentation) are under [tracks/01_http_observability_basics/labs/](tracks/01_http_observability_basics/labs/).

---

## Exercises

Each chapter has exercises to reinforce learning.  
For deeper practice, see the [exercises](tracks/01_http_observability_basics/exercises/) folder in Track 1.

---

## Contributions

This guide is intended as a living document. Feel free to open issues or submit pull requests if you'd like to improve or expand the content.

---

## Author

Created by **Cleverson Rodrigues** — SRE professional passionate about reliability, observability, and teaching.
