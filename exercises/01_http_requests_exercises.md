# Exercises – Chapter 1: HTTP Requests & Responses

1. Explain the difference between `GET` and `POST` methods. Provide an example for each.  
2. Write an HTTP request to fetch user details from `/users/42`.  
3. Identify the status code for:  
   - Resource Not Found  
   - Server Error  
4. Imagine you are debugging a slow login request. Which parts of the HTTP request/response would you inspect first and why?  
5. Bonus: Draw a diagram showing how a browser sends a request to a server and receives a response.  

Got it ✅
I’ll give you the **solutions for `01_http_requests_exercises.md`** in Markdown format, with answers hidden inside `<details><summary>Click to show</summary>...</details>`.
That way, you can keep it clean for practice and only reveal the solution when you want.

Here’s the file:

---

# Solutions – 01\_http\_requests\_exercises.md

## Exercise 1

**Question:** What is the difference between HTTP GET and POST requests?

<details><summary>Click to show</summary>  
GET requests are used to retrieve data from a server without modifying it.  
POST requests are used to send data to the server to create or update resources.  
</details>  

---

## Exercise 2

**Question:** If you want to send sensitive information like a password, which HTTP method should you use and why?

<details><summary>Click to show</summary>  
You should use **POST** because the data is included in the request body, not in the URL.  
This helps prevent exposure in logs, browser history, or bookmarks.  
</details>  

---

## Exercise 3

**Question:** When making an HTTP request, what is the purpose of headers? Give two examples of commonly used headers.

<details><summary>Click to show</summary>  
Headers provide metadata about the request or response.  
Examples:  
- `Content-Type` → specifies the format of the request body (e.g., `application/json`).  
- `Authorization` → carries credentials for authentication.  
</details>  

---

## Exercise 4

**Question:** What is the difference between a 200, 404, and 500 status code?

<details><summary>Click to show</summary>  
- **200**: OK → request was successful.  
- **404**: Not Found → the resource does not exist on the server.  
- **500**: Internal Server Error → something went wrong on the server side.  
</details>  

---

## Exercise 5

**Question:** Imagine you are testing an API. You send a `GET /users/123` request and receive a 404 response. What does this mean?

<details><summary>Click to show</summary>  
It means that the resource `/users/123` does not exist on the server.  
The user with ID `123` is not found.  
</details>  

---

Do you want me to also prepare **solutions for `02_rest_vs_grpc_vs_graphql_exercises.md`** in the same hidden-click format?
