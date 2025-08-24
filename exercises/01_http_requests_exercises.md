# Solutions – Chapter 1: HTTP Requests & Responses

---

## 1. Explain the difference between `GET` and `POST` methods. Provide an example for each.
<details>
<summary>Show Solution</summary>

- **GET**: Retrieves data from the server. It should not change the state of the server. Data is often sent in the URL query string.  
  Example:  
  ```http
  GET /products?category=books HTTP/1.1
  Host: example.com
````

* **POST**: Sends data to the server, usually to create or update a resource. The data is included in the request body.
  Example:

  ```http
  POST /users HTTP/1.1
  Host: example.com
  Content-Type: application/json

  {
    "name": "Alice",
    "email": "alice@example.com"
  }
  ```

</details>

---

## 2. Write an HTTP request to fetch user details from `/users/42`.

<details>
<summary>Show Solution</summary>

```http
GET /users/42 HTTP/1.1
Host: example.com
Accept: application/json
```

</details>

---

## 3. Identify the status code for:

<details>
<summary>Show Solution</summary>

* **Resource Not Found** → `404 Not Found`
* **Server Error** → `500 Internal Server Error`

</details>

---

## 4. Imagine you are debugging a slow login request. Which parts of the HTTP request/response would you inspect first and why?

<details>
<summary>Show Solution</summary>

1. **Request headers & body size** → to check if the client is sending too much data.
2. **Server response time** (measured by `Time-To-First-Byte`) → to see if backend processing is slow.
3. **Network latency** → check round-trip time and if the issue is network-related.
4. **Status codes** → see if there are errors (e.g., `401 Unauthorized`, `500 Internal Server Error`).
5. **Logs on the server** → to identify bottlenecks like slow database queries.

</details>

---

## 5. Bonus: Draw a diagram showing how a browser sends a request to a server and receives a response.

<details>
<summary>Show Solution</summary>

```
Browser (Client) -----> HTTP Request -----> Server
       |                                       |
       |<----- HTTP Response (HTML/JSON) <-----|
```

**Explanation:**

1. The browser sends an HTTP request (URL, method, headers, body).
2. The server processes the request.
3. The server sends back an HTTP response (status code, headers, body).

</details>
```

Do you want me to also make a **student version** (just the exercises) and a **solutions version** (with hidden answers) so you can keep both in your repo?
