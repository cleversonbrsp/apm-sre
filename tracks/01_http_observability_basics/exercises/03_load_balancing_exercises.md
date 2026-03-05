# Solutions – Chapter 3: Load Balancing & Request Routing

## 1. Explain how Round Robin differs from Least Connections.

<details>
<summary>Show Solution</summary>

- **Round Robin**: Requests are distributed evenly in a circular order among all servers. Each server gets the next request in sequence, regardless of load.  
- **Least Connections**: Requests are sent to the server with the fewest active connections, which is more efficient when requests have uneven processing times.  

**Example:**  
- Round Robin: Server A → Server B → Server C → Server A …  
- Least Connections: If Server B has fewer active requests than others, it gets the next request.
</details>

## 2. Write an Nginx configuration to load balance three servers.

<details>
<summary>Show Solution</summary>

```nginx
upstream backend {
    server server1.example.com;
    server server2.example.com;
    server server3.example.com;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend;
    }
}
```

* `upstream backend` defines the pool of backend servers.
* `proxy_pass` sends incoming requests to one of the servers in the pool.

</details>

## 3. Describe a scenario where IP Hash would be useful.

<details>
<summary>Show Solution</summary>

* **Scenario:** Session persistence is required for a web application.
* Example: An online shopping cart that stores items in memory on a specific server.
* **IP Hash** ensures that a client with a given IP always connects to the same server, preserving session state without a shared database or cache.

</details>

## 4. Which load balancing method would you choose for a video streaming service and why?

<details>
<summary>Show Solution</summary>

* **Choice:** Weighted Round Robin or Least Connections.
* **Why:**

  * Video streaming can have uneven server loads depending on user bandwidth and video size.
  * Weighted Round Robin allows more powerful servers to handle more requests.
  * Least Connections ensures that no server is overloaded when handling long video streams.

</details>

## 5. Bonus: Research how cloud load balancers (AWS ELB, GCP Load Balancer, OCI LB) differ from Nginx-based load balancing.

<details>
<summary>Show Solution</summary>

* **Cloud Load Balancers:**

  * Fully managed, auto-scaling, and highly available.
  * Can handle millions of requests without manual configuration.
  * Integrated with cloud monitoring, logging, and security features.

* **Nginx-based Load Balancing:**

  * Requires manual setup and scaling.
  * More flexible for custom routing rules.
  * Cost-effective for smaller workloads but requires infrastructure management.

**Summary:** Cloud load balancers reduce operational overhead and scale automatically, while Nginx gives more control but needs maintenance.

</details>
