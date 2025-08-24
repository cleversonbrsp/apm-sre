# Chapter 2: REST vs gRPC vs GraphQL

## 2.1 REST
REST (Representational State Transfer) is an architectural style for designing APIs.
- Uses HTTP verbs (GET, POST, PUT, DELETE)
- Endpoints represent resources
- Simple and widely adopted

**Analogy:** REST is like ordering dishes from a menu. Each endpoint is a dish, and you choose what you want using the HTTP verb.

**Example:** `/users/42` fetches the user with ID 42.

## 2.2 gRPC
gRPC is a high-performance, open-source RPC framework developed by Google.
- Uses HTTP/2 and binary protocol (faster than REST)
- Strongly typed using Protobuf (Protocol Buffers)
- Ideal for microservices communication

**Analogy:** gRPC is like calling someone on the phone with a script. You send a request and expect a specific type of response.

**Example RPC definition:**
service UserService {  
  rpc GetUser (UserRequest) returns (UserResponse);  
}

## 2.3 GraphQL
GraphQL is a query language for APIs that allows clients to request exactly the data they need.
- Single endpoint
- Flexible queries and responses
- Reduces over-fetching and under-fetching

**Analogy:** GraphQL is like customizing your order at a buffet. You choose exactly what items you want on your plate.

**Example Query:**
query {  
  user(id: 42) {  
    name  
    email  
  }  
}

## 2.4 Exercises
1. Convert a REST GET request `/users/42` into a GraphQL query.  
2. Compare REST and gRPC for high-throughput systems. Which would you choose for a chat application?  
3. Explain a scenario where GraphQL is more efficient than REST.  
4. Identify benefits and drawbacks of using gRPC versus REST in microservices architecture.
