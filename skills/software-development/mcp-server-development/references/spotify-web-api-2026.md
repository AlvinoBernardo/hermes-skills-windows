# Spotify Web API notes (Feb/Mar 2026 dev-mode migration)

Sources: developer.spotify.com `tutorials/february-2026-migration-guide` and the `references/changes/*` changelogs. The docs pages are server-rendered, so `curl` + strip tags works.

## Endpoint changes
- Library: all per-type save/remove/follow/contains endpoints are replaced by **`PUT /me/library`, `DELETE /me/library` and `GET /me/library/contains`**, with query `uris=` (comma-separated `spotify:<type>:<id>`, **max 40**). Saving playlists needs `playlist-modify-public`; following artists or users needs `user-follow-modify`.
- Playlists: `/playlists/{id}/tracks` → **`/playlists/{id}/items`** (GET/POST/PUT/DELETE). The DELETE body parameter `tracks` → `items`. Item entries moved from `.track` to **`.item`**, and `is_local` sits on the outer entry. Read both keys. Items are returned only for playlists the user owns or collaborates on; others give metadata only, or a 403.
- Playlist object: `tracks` → `items` (`items.total`, `items.items[].item`).
- Create a playlist with `POST /me/playlists` (`/users/{id}/playlists` was removed).
- Removed: batch GETs (`/tracks`, `/albums`, `/artists`, `/episodes`, `/shows`, …; fetch them one at a time), `/artists/{id}/top-tracks`, browse/new-releases/categories, `/users/{id}`, `/users/{id}/playlists`, `/markets`.
- Search: **limit max 10, default 5**. Paginate with offset.
- Removed fields: `popularity` (tracks/albums/artists), artist `followers`, album `label`, `/me` `email/country/product/followers`. Requesting `user-read-email` is now pointless.
- Still present: `GET /me/tracks`, `/me/albums`, `/me/playlists`, `/me/top/{type}`, `/me/following?type=artist`, the player endpoints, `PUT /playlists/{id}` (details), and `/artists/{id}/albums`.

## Auth and limits
- Authorization Code + PKCE is supported, so no secret is needed. Redirect URIs must use `http://127.0.0.1:<port>` (`localhost` isn't accepted). Refresh tokens may rotate, and they expire roughly six months after consent.
- Development Mode: the app owner needs Premium, and users must be on the app's **User Management** allowlist (a separate source of 403s).
- Daily-quota 429s carry `Retry-After` ≈ 86400, sometimes with no header at all. Treat a long value as stop, not wait. Disable library auto-retries that would sleep for a day.
- A player 404 usually means no active device. A 403 means a missing scope, no Premium, or the user isn't on the allowlist.
