# Solutions – Chapter 2: REST vs gRPC vs GraphQL

## 1. Convert the REST request `GET /users/42` into a GraphQL query.  

<details>
<summary>Show Solution</summary>

```graphql
query {
  user(id: 42) {
    id
    name
    email
  }
}
```

Here, we query a `user` by ID and specify which fields we want returned (`id`, `name`, `email`).

</details>

## 2. Compare REST and gRPC for a **chat application** that requires very high throughput. Which one would you choose and why?

<details>
<summary>Show Solution</summary>

* **Choice:** gRPC.
* **Why:**

  * gRPC uses HTTP/2 with multiplexing and streaming, enabling bidirectional communication with low latency.
  * REST (over HTTP/1.1) would require repeated requests/responses and is less efficient for real-time communication.
  * In chat apps where thousands of messages per second are exchanged, gRPC is more scalable and performant.

</details>

## 3. Explain a scenario where GraphQL is more efficient than REST.

<details>
<summary>Show Solution</summary>

* Scenario: A **mobile app dashboard** that needs data about a user, their recent posts, and comments.
* With REST: Requires multiple requests (`/user/42`, `/user/42/posts`, `/posts/:id/comments`).
* With GraphQL: A **single query** can fetch all required data at once, reducing network overhead and improving performance on slow mobile connections.

</details>

## 4. Identify benefits and drawbacks of using gRPC versus REST in a microservices architecture.

<details>
<summary>Show Solution</summary>

**Benefits of gRPC:**

* High performance (binary protocol, HTTP/2).
* Strong typing with Protocol Buffers.
* Built-in streaming support.
* Ideal for service-to-service communication.

**Drawbacks of gRPC:**

* Harder for humans to test/debug compared to REST (JSON is more readable).
* Limited browser support (needs a proxy or gateway).
* Steeper learning curve.

**REST:**

* Easier adoption, human-readable JSON.
* Wide browser and tool support (curl, Postman).
* But less efficient in high-performance microservices compared to gRPC.

</details>

## 5. Bonus: Design a small API (choose REST, gRPC, or GraphQL) for a library system (books, authors, borrowers).

<details>
<summary>Show Solution</summary>

### Option A – REST (example endpoints):

* `GET /books` → list all books
* `GET /books/{id}` → get book details
* `POST /books` → add new book
* `GET /authors` → list authors
* `GET /borrowers/{id}/loans` → list books borrowed by a user

### Option B – GraphQL (example schema):

```graphql
type Book {
  id: ID!
  title: String!
  author: Author!
}

type Author {
  id: ID!
  name: String!
  books: [Book!]!
}

type Borrower {
  id: ID!
  name: String!
  borrowedBooks: [Book!]!
}

type Query {
  books: [Book!]!
  book(id: ID!): Book
  authors: [Author!]!
  borrower(id: ID!): Borrower
}
```

</details>
