# HTTP

Read this rule when you change an HTTP service.

## Requests

- Validate input once where the request enters the service, with a schema. Handlers read the validated value, never the
  raw request.
- Reject unsupported content types on endpoints that take a body. Cap the body size per route, and keep the proxy limit
  equal to the application parser limit.
- Handlers adapt transport to domain calls. They define no validation policy, database access, provider mechanics,
  caching, or business decision.
- Middleware validates, authenticates, rate-limits, and attaches context, and makes no feature decision.

## Responses

- One handler formats error responses. Feature code throws and never builds an HTTP error body.
- The service documents one shape for success and one for errors, and keeps both stable.
- Use precise status codes: 201 for creation, 204 with no body, 4xx for caller errors, and 5xx only for failures the
  caller cannot fix.
- The endpoint or module maps provider and database shapes to responses. Responses name fields for the API, not for
  storage, unless the public interface explicitly exposes the provider format.
- Escape HTML for its rendering context, and never pre-escape JSON field values.

### Keep out of public responses

- Schema names, table names, column names, or function names.
- Internal identifiers such as row IDs, user IDs, or session tokens.
- Stack traces or file paths.
- Raw upstream, provider, or database errors.
- Implementation details such as trigger and policy names, or internal state like "deleted" flags.

## Sessions and transport

- Terminate TLS at the proxy, and trust forwarding headers only from it.
- When the service issues tokens, a revocation reaches every instance.
- Cookies that carry sessions: `HttpOnly`, `Secure`, `SameSite`, explicit `Max-Age`, and a non-default name. Writes
  never happen on `GET`. A cookie session needs cross-site request forgery (CSRF) protection on every state-changing
  request.
- Send security headers: HTTP Strict Transport Security (HSTS), `X-Content-Type-Options: nosniff`, frame policy,
  referrer policy, and a Content Security Policy that the application's own scripts satisfy.
- Never pair a wildcard Cross-Origin Resource Sharing (CORS) origin with credentials.

## Operations

- A startup failure stops the process before it accepts work.
- On shutdown, set readiness to false, stop accepting work, drain in-flight work for a bounded time, close resources,
  and exit.
- A fatal runtime error stops new work, reports the failure, and exits.
- Keep health and readiness endpoints cheap. Call no provider from them.
- Broad rate limits sit at the edge, application limits in middleware, and route limits beside the route.
