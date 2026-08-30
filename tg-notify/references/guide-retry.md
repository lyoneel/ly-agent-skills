# Guide: Retry Policy

tg-notify applies one retry policy to every send mode (message, file,
URL, file-id, album, discover, whoami). The policy has two branches:
the 429 rate-limit branch and the transient-error branch.

## 429 Rate Limit (exactly one retry)

Symptom: Telegram answers HTTP 429. The CLI prints
`Rate limited. Retrying after Ns...` to stderr, sleeps N seconds, and
retries exactly once. N is the `retry_after` value from the API
answer; when the answer carries no value, or a non-positive one, N
defaults to 5.

The single 429 retry also happens when `--retries 0` is set, because
`--retries` governs the transient loop only. `--no-retry` disables
this retry too.

## Transient Errors (up to 60 retries by default)

Transient errors are: network timeouts, connection errors, and HTTP
5xx answers from the API. Filesystem errors on local files (a missing
path, a permission error) are deliberately not transient, so a bad
local path fails fast instead of exhausting the retry budget.

Backoff schedule: the first wait is `--base-wait` (default 2s), the
wait doubles per attempt, and each wait is capped at 60s. Every wait
is jittered by plus/minus 25 percent. With defaults the uncapped
sequence is 2s, 4s, 8s, 16s, 32s, 60s, 60s, and so on, up to 60
attempts. Every retry prints
`Transient error (…). Retry N/60 in Xs...` to stderr. There is no
total-time cap; a fully exhausted budget can take about one hour.

## Override Flags

| Flag | Default | Effect |
|------|---------|--------|
| `--no-retry` / `-n` | off | disables all retries, including the single 429 retry; a send becomes fully one-shot |
| `--retries` / `-R` | 60 | max transient retries; 0 disables transient retries only (the single 429 retry still happens) |
| `--base-wait` / `-B` | 2s | first backoff wait; must be greater than 0 |

## Guidance

- For interactive one-shot sends, pass `--no-retry` to avoid long
  silent waits.
- A dead proxy or a refused connection is a transient error. Unless
  retries are disabled, the CLI retries up to 60 times before it
  reports the failure. When a proxy test must fail fast, combine
  `--no-retry` with the send or use `--dry-run` first.
- For long uploads over an unstable link, keep the defaults or raise
  `--retries`; each retry line on stderr names the attempt count and
  the wait.
