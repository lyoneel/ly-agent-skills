# Retry Guide

Retry policy semantics and override flags. Every numeric default comes
from `../assets/constant-limits.md`; this file never re-lists values.

## 429 Rate Limit

On 429, the script waits the server `retry_after` seconds (Telegram
default applies when the field is absent) and retries exactly once.
This single retry also happens with `--retries 0`; only `--no-retry`
disables it. See `gotchas.md` G4.

## Transient Errors

Timeouts, connection errors, and HTTP 5xx retry with exponential
backoff:

- First wait: `--base-wait` (Go duration form like `1s500ms`, must be
  > 0); default from `../assets/constant-limits.md`
- Each attempt doubles the previous wait
- The wait is capped at the backoff cap from
  `../assets/constant-limits.md`
- Each wait is jittered ±25%
- The loop runs up to `--retries` attempts (default from
  `../assets/constant-limits.md`)
- One `Transient error ... Retry N/M in Xs...` line prints per retry

## Never Retried

Filesystem errors (missing local file) never retry.

## Override Flags

| Flag | Effect |
|------|--------|
| `--no-retry` | One-shot: no 429 retry, no transient backoff |
| `--retries N` | Max transient retries (>= 0) |
| `--base-wait D` | First backoff wait (Go duration form, > 0) |

## Rate Limits

Telegram's default budget appears in `../assets/constant-limits.md`.
The script does not pace sends; the server answers 429 and the 429
policy above applies.
