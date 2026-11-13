# MCP server security checklist

Use it twice: to grade a third-party server, and as a build spec for your own.

## Credentials / OAuth
- [ ] Use Authorization Code + **PKCE (S256)** when the vendor supports public clients, so no client secret is stored. Refresh with `client_id` and the refresh token only.
- [ ] Store tokens outside the repo (`$XDG_CONFIG_HOME/<app>/tokens.json`), with the directory at 0700 and the file at 0600. Write atomically: a temp file opened with `wx`, then `fsync`, then `rename`. Refuse symlinks and files owned by another uid. Tighten loose permissions when you read the file.
- [ ] Validate the token file's shape with zod. On corruption, give an actionable message ("logout and auth again").
- [ ] Make refresh single-flight, so a rotated refresh token is never spent twice. Persist rotated tokens. On `invalid_grant`, clear the in-memory tokens and tell the user to re-run auth.
- [ ] If the configured client ID differs from the stored one, force a re-auth.
- [ ] Redact `Bearer …`, `access_token`, `refresh_token`, `code` and `code_verifier` from every error and log line.

## Local OAuth callback server
- [ ] The redirect URI must be a loopback IP literal (`127.0.0.1` / `[::1]`) with an explicit port. Reject `localhost`, `0.0.0.0`, credentials, query strings and fragments.
- [ ] The server runs only during `auth`, and has a timeout that also frees the port.
- [ ] Use 256-bit `state` with a constant-time compare (`timingSafeEqual` after checking lengths). Answer a wrong state with 400 but **keep waiting**, so a stray request can't abort or hijack the flow. Use a one-shot `exchanging` flag.
- [ ] Serve static pages only and reflect nothing from the request. Send `CSP default-src 'none'`, `no-store`, `no-referrer`, `nosniff` and `X-Frame-Options: DENY`.
- [ ] Open the browser with `execFile` (no shell), and only for the vendor authorize-URL prefix. Also print the URL.

## Least privilege
- [ ] Use permission groups that map to the minimal scopes. Those groups decide BOTH which scopes are requested AND which tools are registered. Default to read plus the obviously wanted actions.
- [ ] Register destructive tools (delete/remove/unfollow) only when an explicit opt-in env flag is set **and** the permission is granted.
- [ ] Give every tool annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`.
- [ ] Before calling the API, check that the granted scopes cover the tool. If they don't, return an explanation instead of a raw 403.
- [ ] Don't request scopes you don't need (for example email or profile).

## Requests
- [ ] Pin the API host. Build paths from segments, each passed through `encodeURIComponent`, and reject `''`, `.` and `..`. Assert the origin after building the URL.
- [ ] Validate every ID, URI and link strictly (for example, 22-char base62). Accept web links only from exact hostnames with no userinfo or port.
- [ ] Use `redirect: 'error'` so the bearer token is never forwarded to another host. Set `AbortSignal.timeout` on every request and cap the response size.
- [ ] Retry once on 401 after a forced refresh. Sleep through a short `Retry-After` once; fail fast on a long one (vendor daily quotas can send ~86400s). Retry a GET once on 5xx.
- [ ] Add a local requests-per-minute brake against runaway agent loops.

## Untrusted text (prompt injection)
- [ ] Before returning user-generated strings to the model, strip C0/C1 controls, zero-width characters, bidi overrides and isolates, Unicode tag characters (`\uDB40[\uDC00-\uDC7F]`), the BOM and real HTML tags (`/<\/?[a-z][^>]*>/gi`, which keeps `<3`). Flatten to one line and cap the length.
- [ ] Pass through only well-formed URIs, IDs and vendor links; drop anything else (for example a `javascript:` URL).
- [ ] State in the server `instructions` and the relevant tool descriptions that this text is data, not instructions. Tell users in plain terms that this reduces the risk but doesn't eliminate it.

## Surface area / supply chain
- [ ] Use stdio only unless remote access is required. If you need HTTP: bind to loopback by default, validate Host and Origin headers, and require auth whenever the bind isn't loopback.
- [ ] Keep runtime dependencies to the SDK plus zod where possible, and avoid packages with install scripts.
- [ ] In CI, run lint, typecheck, test and `npm audit --omit=dev --audit-level=high` across a Node matrix. Use `npm ci --ignore-scripts`, `persist-credentials: false` and `permissions: contents: read`, and pin actions to commit SHAs. Add Dependabot for npm and github-actions.
- [ ] Ship a SECURITY.md with the threat model, the controls, what's out of scope, and a private reporting channel.
