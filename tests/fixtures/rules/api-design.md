---
title: api-design-patterns
description: REST API design best practices
category: architecture
tags: [rest, api, http]
version: 1.2.0
applies_to: [python, fastapi, flask]
---

# API Design Patterns

## Resource Naming

- Use plural nouns for collections: `/users`, `/posts`
- Use singular for singletons: `/profile`
- Use kebab-case for multi-word resources: `/user-profiles`

## HTTP Methods

- GET: Retrieve resources (idempotent)
- POST: Create new resources
- PUT: Replace entire resource
- PATCH: Partial update
- DELETE: Remove resource

## Response Codes

- 200 OK: Successful GET/PUT/PATCH
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid client input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Authenticated but not authorized
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Server-side error
