````markdown
# Chapter 1: HTTP Requests & Responses Fundamentals

Welcome to Chapter 1! This chapter will help you understand how HTTP works, the building blocks of requests and responses, and how to interact with servers.  

---

## 1.1 What is an HTTP Request?

HTTP (Hypertext Transfer Protocol) is the foundation of data communication on the web.

**Analogy:**  
Imagine HTTP as a postal service:
- You (the client) send a letter (request) to a recipient (server).
- The server reads your letter and replies with a response.

---

### Components of an HTTP Request

1. **Method:** Defines the action you want to perform (GET, POST, PUT, DELETE)
2. **URL:** The address where the request is sent
3. **Headers:** Metadata about the request (like “From:” or “Subject:” in emails)
4. **Body:** Data sent to the server (optional)

**Example: POST Request**

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "sre_learner",
  "password": "secure123"
}
````

**Explanation:**

* `POST` is the method.
* `/login` is the URL path.
* Headers provide extra info (`Content-Type` specifies JSON).
* Body contains the credentials sent to the server.

---

## 1.2 HTTP Response

The server responds with:

* **Status code:** Indicates success, failure, or error (e.g., 200, 404, 500)
* **Headers:** Metadata about the response
* **Body:** Data returned from the server

**Example: Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Login successful",
  "token": "abcd1234"
}
```

**Explanation:**

* `200 OK` means the request succeeded.
* The body returns the success message and a token for authentication.

---

### 1.3 Common HTTP Methods

| Method | Description                | Example Use Case           |
| ------ | -------------------------- | -------------------------- |
| GET    | Retrieve data              | Get user info: `/users/42` |
| POST   | Create new resource        | Submit login credentials   |
| PUT    | Update existing resource   | Update user profile        |
| DELETE | Remove resource            | Delete account `/users/42` |
| PATCH  | Partial update of resource | Update user email only     |

---

### 1.4 Common HTTP Status Codes

| Code | Meaning               | Example Scenario                 |
| ---- | --------------------- | -------------------------------- |
| 200  | OK                    | Successful request               |
| 201  | Created               | New resource created             |
| 400  | Bad Request           | Invalid request format           |
| 401  | Unauthorized          | Missing or invalid credentials   |
| 403  | Forbidden             | No permission to access resource |
| 404  | Not Found             | Resource does not exist          |
| 500  | Internal Server Error | Unexpected server error          |

---

### 1.5 Mini Real-World Scenario

When you type `google.com` in your browser:

1. Browser sends a **GET request** to `google.com`.
2. Google servers respond with a **200 OK** and HTML content.
3. Browser renders the page.
4. Behind the scenes, headers, cookies, and body are exchanged.

---

## 1.6 Exercises

1. Explain the difference between GET and POST methods. Provide an example scenario for each.
2. Write an HTTP request to fetch the user details from `/users/42`. Include headers and method.
3. Identify the status code you would expect for:

   * A missing resource
   * Server error
   * Successful creation of a new resource
4. Bonus: Describe what happens behind the scenes from typing a URL in your browser to seeing the page.

---

**End of Chapter 1**

```

---

I can now create `02_rest_vs_grpc_vs_graphql.md` in the same progressive style with examples and exercises for your GitHub repo. Do you want me to do that next?
```
