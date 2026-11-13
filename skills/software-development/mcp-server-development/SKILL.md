---
name: mcp-server-development
description: "Use when vetting, building, or hardening MCP servers."
version: 1.1.0
platforms: [macos, linux, windows]
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mcp, model-context-protocol, security, typescript, oauth, code-review]
    related_skills: [github, requesting-code-review, test-driven-development]
---

# MCP server development and vetting

## When to Use
Use this skill for two kinds of request that usually come one after the other:
1. "Is this MCP server / repo safe?": a security review of third-party code. This also covers any small integration repo that holds OAuth tokens.
2. "Remake it better and safer, then push it to my GitHub": a hardened rewrite or a new MCP server.

## A. Security review of a third-party MCP repo

1. Clone it into scratch, not into the user's home dir:
   `cd "${HERMES_HOME:-$HOME/.hermes}/cache/scratch" && git clone --depth 50 -q <url> && git log -5 --format='%h %ad %an %s' --date=short`
   Use git rather than web_extract, because GitHub tree URLs often come back empty.
2. Inventory: `find . -path ./.git -prune -o -type f -print`, `wc -l src/*`, read `package.json`, plus the Dockerfile, `.env.example` and `.gitignore` if present.
3. Grep for risky patterns before reading anything line by line:
   `child_process|exec\(|spawn|eval\(|new Function|fetch\(|https?://|writeFile|readFile|unlink|process\.env|listen\(|0\.0\.0\.0|Access-Control|cors`
   Every outbound host must be the expected vendor. List each one.
4. Check for install hooks in the lockfile (`grep '"hasInstallScript": true' -B3 package-lock.json`). Then run `npm ci --ignore-scripts` and `npm audit --omit=dev --package-lock-only`. For each advisory, say whether the vulnerable code path is actually used.
5. Read the auth/token code, the HTTP transport and the config writer in full. Check them against `references/security-checklist.md`.
6. Report a verdict first, then a table of the checks and their results, then the residual risks: token scopes, plaintext secrets, prompt injection through user-generated text, and network exposure. Give practical advice such as pinning to a reviewed commit.

## B. Building a hardened MCP server

Do it in this order:
1. **Check the upstream API's current endpoints before coding.** Vendor APIs change (Spotify changed in 2026). Read the original repo's comments and the vendor's migration guide and changelog. `curl` + strip HTML works when web_extract can't get the page.
2. **Reuse the SDK version the reference repo pins.** Install it in the clone and read `dist/*.d.mts` to get the exact `registerTool`, `serveStdio` and `InMemoryTransport` API. Don't write SDK code from memory. Patterns are in `references/typescript-sdk-v2.md`.
3. Lay out the modules as config → token store → oauth (PKCE) → API client → sanitise/format → tools → server → CLI. Use dependency injection (`fetchImpl`, `now`, `sleep`, `configDir`) so everything can be tested without network.
4. Apply every item in `references/security-checklist.md`. The most important are: least-privilege permission groups that gate both the scopes requested and the tools registered; destructive tools off by default behind an explicit env flag; annotations on every tool; stdio only; a minimal set of dependencies.
5. Write tests with `node:test` against `build/`, using a scripted fetch that fails on any unexpected request or any unused step. Also run an MCP round-trip with an in-memory client, and spawn the real `build/index.js` over stdio once as a smoke test.
6. Run lint, typecheck, test and `npm audit --omit=dev`. Then commit, create the repo and push, and watch CI until it's green (the `github` skill's repo-management reference has a section called "New local project → GitHub, end to end").
7. Final report: the repo URL and visibility, what was verified (test counts, CI matrix), and what could NOT be verified. Say plainly that real vendor sign-in needs the user's own credentials.

## Pitfalls

- **Take crypto test vectors from the source, not from memory.** `curl` the RFC and grep for the values. A misremembered vector fails a correct implementation, and you then waste time "fixing" code that works.
- **Use `.refine()` for argument validation in zod schemas, not `.transform()`.** The SDK converts schemas to JSON Schema, and transforms can't be represented, so parse references inside the handler.
- **A bare ID is ambiguous when a tool accepts several resource types.** Reject it with a message that asks for a URI or link. Don't guess the type.
- **TypeScript 7 doesn't auto-load `@types/node`.** Add `"types": ["node"]` to tsconfig, or every `node:` import fails to resolve.
- **Keep stdout clean in stdio mode.** It's the protocol channel, so all logging goes to `console.error`. Grep `console.log` outside the CLI entry before you ship.
- **Default a new GitHub repo to private** unless the user says public. Tell them how to flip it.
- **Keep the upstream MIT copyright line in LICENSE and credit the original in the README** when rewriting someone else's project.

## References
- `references/security-checklist.md`: the review/hardening checklist (OAuth, token storage, callbacks, requests, untrusted text, surface area, CI).
- `references/typescript-sdk-v2.md`: `@modelcontextprotocol/server` v2 registration, stdio, in-memory test harness, scripted fetch.
- `references/spotify-web-api-2026.md`: Spotify endpoint and field changes, scopes, dev-mode limits.

## On Windows (this PC)
The workflow is the same (git-bash has `git`, `find`, `grep`, `wc`; node 24 / npm 11 installed). Differences:
- **Scratch dir:** `$HERMES_HOME/cache/scratch` = `C:/Users/<you>/AppData/Local/hermes/cache/scratch` (not `~/.hermes/...`).
- **Client config:** Claude Desktop reads `%APPDATA%\Claude\claude_desktop_config.json` (`C:/Users/<you>\AppData\Roaming\Claude\`; not present on this PC — Claude Desktop isn't installed), Mac: `~/Library/Application Support/Claude/`. Use absolute `C:\` paths (escaped backslashes) in JSON `args`. Any config writer in a reviewed server must resolve the dir via `process.platform` / `%APPDATA%` and not hardcode `~/Library`.
- **Spawning `npx`/`npm`:** on Windows `spawn('npx')` → ENOENT and `spawn('npx.cmd')` → EINVAL (Node ≥ 20.12 blocks .cmd without a shell; verified here). In configs use `"command": "cmd", "args": ["/c","npx","-y","pkg"]`; in tests and `StdioClientTransport` prefer `command: process.execPath, args: ['build/index.js']` (plain `node` works too).
- **chmod:** the `chmodSync('build/index.js', 0o755)` build step is a harmless no-op on Windows (verified); the shebang is ignored, run `node build/index.js`. Npm `bin` shims still work.
- **Paths in tests:** use `path.join`/`os.tmpdir()`, never `/tmp`; the browser-open step (`execFile` with no shell) must use `rundll32 url.dll,FileProtocolHandler <url>` on Windows (avoids cmd.exe parsing of `&`; `cmd /c start` mangles it), `open` on Mac, `xdg-open` on Linux — still only for the vendor URL prefix, never `shell:true`. (Not tested here.)
