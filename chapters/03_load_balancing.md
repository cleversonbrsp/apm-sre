# Chapter 3: Load Balancing & Request Routing

## 3.1 Why Load Balance?
When many users access an application, a single server can become overloaded. Load balancing helps distribute incoming traffic across multiple servers to improve performance and reliability.

**Analogy:** Imagine a store with 100 customers and only 1 cashier. The line would be very long. If you add more cashiers (servers), customers (requests) get served faster.

## 3.2 Types of Load Balancing
1. **Round Robin**: Requests are distributed sequentially across servers.  
   Example: Request 1 → Server A, Request 2 → Server B, Request 3 → Server C.  

2. **Least Connections**: Requests are sent to the server with the fewest active connections.  
   Useful when requests have different processing times.  

3. **IP Hash**: A hash of the client’s IP address determines which server handles the request.  
   Ensures a client always reaches the same server (good for session persistence).  

4. **Weighted Round Robin**: Some servers receive more requests based on their capacity.  
   Example: A stronger server gets 2 requests for every 1 request sent to a weaker server.  

## 3.3 Example: Nginx as a Load Balancer
Nginx can act as a load balancer by defining an upstream group of servers and routing requests to them.

upstream backend {  
    server app1.example.com;  
    server app2.example.com;  
}  

server {  
    listen 80;  
    location / {  
        proxy_pass http://backend;  
    }  
}  

## 3.4 Real-World Scenario
When you type `amazon.com`, your request doesn’t go to just one server. A load balancer decides which server should handle your request, ensuring the system can handle millions of users simultaneously.

## 3.5 Exercises
1. Explain how Round Robin differs from Least Connections.  
2. Configure Nginx to load balance three servers.  
3. Describe a scenario where IP Hash would be useful.  
4. Which load balancing method would you choose for a video streaming service and why?  
