# Study Guide: Understanding Requests for SREs

Welcome to this progressive study guide designed for Site Reliability Engineers (SREs) and aspiring professionals.  
By the end of this guide, you will:

- ✅ Understand HTTP requests deeply.  
- ✅ Compare REST, gRPC, and GraphQL.  
- ✅ Learn about load balancing and request routing.  
- ✅ Explore observability (metrics, logs, traces).  
- ✅ Get hands-on with APM using SigNoz.  
- ✅ Apply SRE best practices for handling requests in real-world systems.  

---

## 📖 Chapter 1: HTTP Requests & Responses Fundamentals

### 1.1 What is an HTTP Request?

Think of an HTTP request as sending a **letter** to a web server.  
- The **address** (URL) tells the server where to deliver.  
- The **method** tells the server what you want to do.  
- The **headers** are like the envelope details (language, format, authorization).  
- The **body** is the actual message (data you send).  

**Example (cURL command):**
```bash
curl -X GET "https://jsonplaceholder.typicode.com/posts/1"
