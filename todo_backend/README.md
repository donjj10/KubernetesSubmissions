# Todo Backend

Backend service for the Todo application used in the DevOps with Kubernetes MOOC.

## Exercise 2.2 — The Project, Step 8

The Todo Backend is responsible for storing and retrieving todo items.

For this exercise, todos are stored in memory. This means the data will be lost if the Todo Backend pod restarts.
## API Endpoints

### GET /todos

Returns all existing todos.


### POST /todos

Creates a new todo.

## Kubernetes

The application runs as a separate Kubernetes Deployment and is exposed internally using a ClusterIP Service:

todo-backend-svc

The Todo App communicates with the backend using Kubernetes DNS:

http://todo-backend-svc:3000/todos

