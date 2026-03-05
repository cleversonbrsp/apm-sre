# Chapter 1: HTTP Requests & Responses Fundamentals

## 1.1 What is an HTTP Request?
HTTP (Hypertext Transfer Protocol) is how your browser and servers communicate.

**Analogy:** Think of HTTP as a postal service:
- You (client) send a letter (request) to someone (server).
- The server reads the letter and replies (response).

### Components of an HTTP Request:
- **Method**: Action to perform (GET, POST, PUT, DELETE)
- **URL**: Where to send the request
- **Headers**: Metadata (like “From:” or “Subject:” in emails)
- **Body**: Data sent to the server (optional)

### Example HTTP Request:
POST /login HTTP/1.1  
Host: example.com  
Content-Type: application/json  

{  
  "username": "sre_learner",  
  "password": "secure123"  
}

## 1.2 HTTP Response
The server sends back a response including:
- **Status code** (200, 404, 500)
- **Headers**
- **Body**

### Example HTTP Response:
HTTP/1.1 200 OK  
Content-Type: application/json  

{  
  "message": "Login successful",  
  "token": "abcd1234"  
}

## 1.3 Exercises
1. What’s the difference between GET and POST methods? Provide an example for each.  
2. Write an HTTP request to fetch user details from `/users/42`.  
3. Identify the status code for “Resource Not Found” and “Server Error”.
