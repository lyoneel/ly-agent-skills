#!/usr/bin/env python3
"""Send Telegram messages, files, and albums via the Bot API.

Unified CLI mirroring the Go tg-notify-cli interface. Flags may appear
anywhere on the command line; one positional text argument is accepted
(message text, or caption when a file flag is present; album items in
album mode).

Usage:
    python3 scripts/tg_notify.py "text"
    python3 scripts/tg_notify.py -m "text" --parse-mode HTML
    python3 scripts/tg_notify.py -f path/to/file
    python3 scripts/tg_notify.py "caption" -f path/to/file
    python3 scripts/tg_notify.py --url URL --type document
    python3 scripts/tg_notify.py --file-id ID --type photo
    python3 scripts/tg_notify.py --album a.jpg b.jpg
    python3 scripts/tg_notify.py --whoami
    python3 scripts/tg_notify.py --discover-chat-id
    python3 scripts/tg_notify.py --version

Environment:
    TELEGRAM_BOT_TOKEN  Bot token (required, or use --token)
    TELEGRAM_CHAT_ID    Target chat ID (required, or use --chat-id)
    TELEGRAM_BASE_URL   Bot API base URL (or use --base-url)
    TELEGRAM_PROXY      Proxy URL (or use --proxy)
"""

import argparse
import json
import mimetypes
import os
import random
import re
import stat as stat_module
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import tg_constants

DEFAULT_BASE_URL = "https://api.telegram.org"
TIMEOUT_SECONDS = 15

# Fixed values live in assets/constant-limits.md and
# assets/constant-filetypes.md (single source of truth), loaded via
# scripts/tg_constants.py. Never hardcode a duplicate here.
LIMITS = tg_constants.load_limits()
MAX_MESSAGE_CHARS = int(LIMITS["message_max_chars"])
MAX_CAPTION_CHARS = int(LIMITS["caption_max_chars"])
MAX_PHOTO_UPLOAD = int(LIMITS["photo_upload_max_mb"]) * 1024 * 1024
MAX_OTHER_UPLOADS = int(LIMITS["other_upload_max_mb"]) * 1024 * 1024
MAX_SELF_HOSTED_UPLOAD = int(LIMITS["self_hosted_upload_max_mb"]) * 1024 * 1024

DEFAULT_RETRIES = int(LIMITS["default_retries"])
DEFAULT_BASE_WAIT = float(LIMITS["default_base_wait_seconds"])
MAX_BACKOFF_SECONDS = float(LIMITS["backoff_cap_seconds"])

ALBUM_MIN_ITEMS = int(LIMITS["album_min_items"])
ALBUM_MAX_ITEMS = int(LIMITS["album_max_items"])

EXT_TO_TYPE, MIME_TO_TYPE = tg_constants.load_filetypes()

USAGE_TEXT = """usage: tg-notify [message] [flags]

  tg-notify "text"                          send a text message
  tg-notify -m "text" --parse-mode HTML     send a formatted message
  tg-notify -f path/to/file                 send a local file
  tg-notify "caption" -f path/to/file       send a local file with caption
  tg-notify --url URL --type document       send a remote file
  tg-notify --file-id ID --type photo       resend a file by file_id
  tg-notify --album a.jpg b.jpg             send a photo/video album
  tg-notify --reply-to 42 "done"            reply to message 42
  tg-notify --whoami                        print the bot's identity
  tg-notify --discover-chat-id              print the latest chat ID
  tg-notify -v                              print the version

flags:
  -m, --message          message text (1-{msg} chars); read from stdin if omitted
  -f, --file             local file path to upload
  -u, --url              remote file URL to send
  -F, --file-id          Telegram file_id to resend
  -a, --album            photo/video files or URLs to send as one album ({amin}-{amax})
  -t, --type             override type: photo, document, audio, video, voice, animation, sticker
  -c, --caption          caption text (0-{cap} chars)
  -p, --parse-mode       MarkdownV2, HTML, or empty for plain text
  -r, --reply-to         message ID to reply to
  -j, --json             print machine-readable JSON instead of text
      --no-trim          do not trim whitespace from the stdin message
  -w, --whoami           print the bot's identity and exit
  -T, --token            bot token (overrides TELEGRAM_BOT_TOKEN)
  -C, --chat-id          chat ID (overrides TELEGRAM_CHAT_ID)
  -n, --no-retry         disable auto-retry on 429 and transient errors
  -R, --retries          max retries on transient errors (default {retries})
  -B, --base-wait        first backoff wait on transient errors (default {wait}s)
  -d, --discover-chat-id print the chat ID from the latest bot update
  -o, --offset           past update ID to skip in --discover-chat-id
  -S, --silent           deliver without a phone notification
  -P, --proxy            proxy URL (http, https; socks5 not supported)
  -U, --base-url         Bot API base URL for a self-hosted server
  -D, --dry-run          print the resolved request without sending
  -v, --version          print the version
  -h, --help             show this help""".format(
    msg=MAX_MESSAGE_CHARS,
    cap=MAX_CAPTION_CHARS,
    amin=ALBUM_MIN_ITEMS,
    amax=ALBUM_MAX_ITEMS,
    retries=DEFAULT_RETRIES,
    wait=int(DEFAULT_BASE_WAIT),
)

TOKEN_URL_PATTERN = re.compile(r"/bot[^/\s]+/")

BOOL_FLAGS = {
    "no-retry", "noretry", "n", "discover-chat-id", "discoverchatid", "d",
    "json", "j", "silent", "S", "dry-run", "D", "no-trim", "whoami", "w",
    "help", "h",
}

VALUE_FLAG_NAMES = {
    "message", "m", "file", "f", "url", "u", "file-id", "fileid", "F",
    "album", "a", "type", "t", "caption", "c", "parse-mode", "parsemode",
    "p", "reply-to", "r", "token", "T", "chat-id", "chatid", "C",
    "retries", "R", "base-wait", "basewait", "B", "offset", "o",
    "proxy", "P", "base-url", "U",
}

INT_VALUE_FLAGS = {"retries", "R", "offset", "o", "reply-to", "r"}

DURATION_VALUE_FLAGS = {"base-wait", "basewait", "B"}

KNOWN_FLAG_NAMES = VALUE_FLAG_NAMES | BOOL_FLAGS

HELP_FLAG_TOKENS = {"-h", "--help"}

VERSION_FLAG_TOKENS = {"-v", "--version"}

VALID_FILE_TYPES = ("photo", "document", "audio", "video", "voice",
                    "animation", "sticker")

ENDPOINT_BY_TYPE = {
    "photo": "sendPhoto",
    "document": "sendDocument",
    "audio": "sendAudio",
    "video": "sendVideo",
    "voice": "sendVoice",
    "animation": "sendAnimation",
    "sticker": "sendSticker",
}

DURATION_PART = re.compile(r"(\d*\.?\d+)(ns|us|\u00b5s|ms|s|m|h)")

UNIT_SECONDS = {
    "ns": 1e-9, "us": 1e-6, "\u00b5s": 1e-6, "ms": 1e-3,
    "s": 1.0, "m": 60.0, "h": 3600.0,
}

INT64_MAX = 9223372036854775807
INT64_MIN = -9223372036854775808

_BASE_DIGITS = {"0x": "0123456789abcdefABCDEF", "0o": "01234567",
                "0b": "01", "": "0123456789"}
_BASE_RADIX = {"0x": 16, "0o": 8, "0b": 2, "": 10}


def parse_go_int(text):
    """Parse an integer the way Go's strconv.ParseInt(s, 0, 64) does.

    Base-0 semantics: a 0x/0X/0o/0O/0b/0B prefix selects hex, octal, or
    binary; a bare leading zero selects octal; otherwise decimal. Single
    underscores are allowed between digits and immediately after a base
    prefix. An optional sign is accepted. Returns the int, or raises
    ValueError (bad syntax) or OverflowError (outside int64 range).
    """
    body = text
    sign = 1
    if body and body[0] in "+-":
        if body[0] == "-":
            sign = -1
        body = body[1:]
    if len(body) >= 2 and body[0] == "0" and body[1] in "xXoObB":
        prefix = body[:2].lower()
        body = body[2:]
        base = _BASE_RADIX[prefix]
        digits = _BASE_DIGITS[prefix]
        previous_digit = True
    else:
        base = 8 if len(body) > 1 and body.startswith("0") else 10
        digits = "01234567" if base == 8 else "0123456789"
        previous_digit = False
    if not body or any(ch not in digits + "_" for ch in body):
        raise ValueError(f"invalid syntax: {text}")
    clean = []
    for ch in body:
        if ch == "_":
            if not previous_digit:
                raise ValueError(f"invalid syntax: {text}")
            previous_digit = False
            continue
        clean.append(ch)
        previous_digit = True
    if not previous_digit:
        raise ValueError(f"invalid syntax: {text}")
    value = sign * int("".join(clean), base)
    if value > INT64_MAX or value < INT64_MIN:
        raise OverflowError(f"value out of range: {text}")
    return value


class UsageRequested(Exception):
    """Signals that usage help should be printed without Failed prefix."""


class HelpRequested(Exception):
    """Signals that usage help should be printed to stdout, exit 0."""


class ApiError(Exception):
    """Error reported by the Telegram Bot API (ok: false)."""

    def __init__(self, code, description, retry_after=0):
        super().__init__(f"HTTP {code}: {description}")
        self.code = code
        self.description = description
        self.retry_after = retry_after


def scrub_secrets(text):
    """Replace any bot token embedded in a Bot API URL with <token>."""
    return TOKEN_URL_PATTERN.sub("/bot<token>/", text)


def go_quote(value):
    """Quote like Go's %q: double quotes, backslash-escaped."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def go_duration(seconds):
    """Format seconds the way Go's Duration.String does."""
    if seconds >= 1:
        text = f"{seconds:.9f}".rstrip("0").rstrip(".")
        return f"{text}s"
    millis = seconds * 1000
    text = f"{millis:.6f}".rstrip("0").rstrip(".")
    return f"{text}ms"


def parse_go_duration(text):
    """Parse a Go time.Duration string; return seconds or None."""
    body = text
    sign = 1.0
    if body.startswith(("+", "-")):
        if body[0] == "-":
            sign = -1.0
        body = body[1:]
    if not body:
        return None
    if body == "0":
        return 0.0
    total = 0.0
    position = 0
    for match in DURATION_PART.finditer(body):
        if match.start() != position:
            return None
        total += float(match.group(1)) * UNIT_SECONDS[match.group(2)]
        position = match.end()
    if position != len(body):
        return None
    return sign * total


def compact_json(value):
    """Marshal JSON the way Go does: compact, no spacing."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def read_skill_version():
    """Read the version field from the skill's SKILL.md frontmatter."""
    skill_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")
    try:
        with open(skill_path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return "unknown"
    match = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', text, re.MULTILINE)
    if not match:
        return "unknown"
    return match.group(1).strip()


def load_dotenv():
    """Fill TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from ./.env.

    Only variables not already set in the environment are filled. A
    missing file is not an error. Blank lines and # comment lines are
    skipped; surrounding whitespace is trimmed.
    """
    try:
        with open(".env", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key not in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            continue
        if key in os.environ:
            continue
        os.environ[key] = value.strip()
def reorder_args(args):
    """Move flag tokens ahead of positional tokens.

    Mirrors Go reorderArgs so the parser sees flags anywhere on the
    command line. A non-bool flag written without "=" consumes the next
    token as its value during the scan. The bare `--` token ends flag
    processing: it and everything after it stay positional.
    """
    flags = []
    positional = []
    i = 0
    separator_seen = False
    while i < len(args):
        arg = args[i]
        if separator_seen:
            positional.append(arg)
            i += 1
            continue
        if arg == "--":
            positional.append(arg)
            separator_seen = True
            i += 1
            continue
        if len(arg) < 2 or arg[0] != "-":
            positional.append(arg)
            i += 1
            continue
        name = arg.lstrip("-")
        flags.append(arg)
        if "=" not in name and name not in BOOL_FLAGS and i + 1 < len(args):
            i += 1
            flags.append(args[i])
        i += 1
    return flags + positional


def _go_flag_display(name):
    """Format a flag name the Go way: single dash, dashes stripped."""
    return "-" + name.lstrip("-")


SHORT_NAMES = set("mfuFatcprjwTCnRBdoSPUDh")

LONG_NAMES = {
    "message", "file", "url", "file-id", "fileid", "album", "type",
    "caption", "parse-mode", "parsemode", "reply-to", "json", "no-trim",
    "whoami", "token", "chat-id", "chatid", "no-retry", "noretry",
    "retries", "base-wait", "basewait", "discover-chat-id",
    "discoverchatid", "offset", "silent", "proxy", "base-url",
    "dry-run", "help",
}

BOOL_NAMES = {
    "n", "no-retry", "noretry", "d", "discover-chat-id",
    "discoverchatid", "j", "json", "S", "silent", "D", "dry-run",
    "no-trim", "w", "whoami", "h", "help",
}

VALUE_NAMES = {
    "m", "message", "f", "file", "u", "url", "F", "file-id", "fileid",
    "a", "album", "t", "type", "c", "caption", "p", "parse-mode",
    "parsemode", "r", "reply-to", "T", "token", "C", "chat-id",
    "chatid", "R", "retries", "B", "base-wait", "basewait", "o",
    "offset", "P", "proxy", "U", "base-url",
}

INT_NAMES = {"R", "retries", "o", "offset", "r", "reply-to"}

DURATION_NAMES = {"B", "base-wait", "basewait"}

KNOWN_NAMES = BOOL_NAMES | VALUE_NAMES

BOOL_TRUE_VALUES = {
    "1", "t", "T", "TRUE", "true", "True",
    "0", "f", "F", "FALSE", "false", "False",
}

BOOL_TRUTHY = {"1", "t", "T", "TRUE", "true", "True"}


def _canonical_form(name):
    """argparse-registered spelling for a flag name."""
    if len(name) == 1:
        return f"-{name}"
    return f"--{name}"


class Parser(argparse.ArgumentParser):
    """ArgumentParser emitting Go tg-notify-cli error strings."""

    raw_args = []

    def error(self, message):
        if message.startswith("unrecognized arguments: "):
            first = message[len("unrecognized arguments: "):].split()[0]
            sys.stderr.write(
                f"Failed: flag provided but not defined: "
                f"{_go_flag_display(first.split('=')[0])}\n")
            raise SystemExit(1)
        match = re.match(r"^argument ([^:]+): (.+)$", message)
        if match and "expected one argument" in match.group(2):
            names = match.group(1).split("/")
            used = [n for n in names if n in self.raw_args]
            name = used[0] if used else names[-1]
            sys.stderr.write(
                f"Failed: flag needs an argument: "
                f"{_go_flag_display(name)}\n")
            raise SystemExit(1)
        sys.stderr.write(f"Failed: {message}\n")
        raise SystemExit(1)


class Options:
    """Parsed option values, Go-options-struct style."""

    def __init__(self):
        self.message = ""
        self.file_path = ""
        self.file_url = ""
        self.file_id = ""
        self.albums = []
        self.file_type = ""
        self.caption = ""
        self.parse_mode = ""
        self.token = ""
        self.chat_id = ""
        self.base_url = ""
        self.proxy = ""
        self.reply_to = 0
        self.reply_to_set = False
        self.offset = 0
        self.offset_set = False
        self.retries = DEFAULT_RETRIES
        self.base_wait = DEFAULT_BASE_WAIT
        self.no_retry = False
        self.silent = False
        self.json_out = False
        self.dry_run = False
        self.no_trim = False
        self.discover = False
        self.whoami = False
        self.rest = []


def build_parser():
    parser = Parser(prog="tg-notify", add_help=False, allow_abbrev=False)
    parser.add_argument("rest", nargs="*", help=argparse.SUPPRESS)
    parser.add_argument("--message", "-m", dest="message", default="",
                        help="message text (1-%d chars); read from stdin "
                             "if omitted" % MAX_MESSAGE_CHARS)
    parser.add_argument("--file", "-f", dest="file_path", default="",
                        help="local file path to upload")
    parser.add_argument("--url", "-u", dest="file_url", default="",
                        help="remote file URL to send")
    parser.add_argument("--file-id", "--fileid", "-F", dest="file_id",
                        default="", help="Telegram file_id to resend")
    parser.add_argument("--album", "-a", dest="albums", action="append",
                        default=[],
                        help="photo/video files or URLs to send as one "
                             "album (%d-%d)" % (ALBUM_MIN_ITEMS,
                                                 ALBUM_MAX_ITEMS))
    parser.add_argument("--type", "-t", dest="file_type", default="",
                        help="override auto-detection: photo, document, "
                             "audio, video, voice, animation, sticker")
    parser.add_argument("--caption", "-c", dest="caption", default="",
                        help="caption text (0-%d chars)" % MAX_CAPTION_CHARS)
    parser.add_argument("--parse-mode", "--parsemode", "-p",
                        dest="parse_mode", default="",
                        help="MarkdownV2, HTML, or empty for plain text")
    parser.add_argument("--reply-to", "-r", dest="reply_to", default="0",
                        help="message ID to reply to")
    parser.add_argument("--json", "-j", dest="json_out",
                        action="store_true",
                        help="print machine-readable JSON instead of text")
    parser.add_argument("--no-trim", dest="no_trim", action="store_true",
                        help="do not trim whitespace from the stdin "
                             "message")
    parser.add_argument("--whoami", "-w", dest="whoami",
                        action="store_true",
                        help="print the bot's identity and exit")
    parser.add_argument("--token", "-T", default="",
                        help="bot token (overrides TELEGRAM_BOT_TOKEN)")
    parser.add_argument("--chat-id", "--chatid", "-C", dest="chat_id",
                        default="",
                        help="chat ID (overrides TELEGRAM_CHAT_ID)")
    parser.add_argument("--no-retry", "--noretry", "-n", dest="no_retry",
                        action="store_true",
                        help="disable auto-retry on 429 and transient "
                             "errors")
    parser.add_argument("--retries", "-R", dest="retries",
                        default=str(DEFAULT_RETRIES),
                        help="max retries on transient errors "
                             "(default %d)" % DEFAULT_RETRIES)
    parser.add_argument("--base-wait", "--basewait", "-B",
                        dest="base_wait",
                        default="%ds" % int(DEFAULT_BASE_WAIT),
                        help="first backoff wait on transient errors "
                             "(default %ds)" % int(DEFAULT_BASE_WAIT))
    parser.add_argument("--discover-chat-id", "--discoverchatid", "-d",
                        dest="discover", action="store_true",
                        help="print the chat ID from the latest bot update")
    parser.add_argument("--offset", "-o", dest="offset", default="0",
                        help="past update ID to skip in --discover-chat-id")
    parser.add_argument("--silent", "-S", dest="silent",
                        action="store_true",
                        help="deliver without a phone notification")
    parser.add_argument("--proxy", "-P", dest="proxy", default="",
                        help="proxy URL (http, https; socks5 not "
                             "supported)")
    parser.add_argument("--base-url", "-U", dest="base_url", default="",
                        help="Bot API base URL for a self-hosted server")
    parser.add_argument("--dry-run", "-D", dest="dry_run",
                        action="store_true",
                        help="print the resolved request without sending")
    return parser


def _split_flag_token(arg):
    """Split a dash token into (dash_count, name, has_eq, eq_value)."""
    dash_count = len(arg) - len(arg.lstrip("-"))
    rest = arg[dash_count:]
    if "=" in rest:
        name, eq_value = rest.split("=", 1)
        return dash_count, name, True, eq_value
    return dash_count, rest, False, None


def normalize_flags(reordered):
    """Validate and normalise flag tokens in parse order.

    Mirrors Go flag.Parse error precedence: unknown flags, bad dash
    syntax, and invalid bool/int/duration values are all reported in
    first-seen order. The `--` separator ends flag validation; tokens
    after it are positional. Help tokens raise HelpRequested.
    Returns the argparse-ready token list.
    """
    out = []
    i = 0
    separator_seen = False
    while i < len(reordered):
        arg = reordered[i]
        if separator_seen:
            out.append(arg)
            i += 1
            continue
        if len(arg) < 2 or arg[0] != "-":
            out.append(arg)
            i += 1
            continue
        if arg == "--":
            separator_seen = True
            out.append(arg)
            i += 1
            continue
        dash_count, name, has_eq, eq_value = _split_flag_token(arg)
        if dash_count >= 3:
            raise ValidationError(f"bad flag syntax: {arg}")
        if not name:
            raise ValidationError(f"bad flag syntax: {arg}")
        if dash_count == 1 and len(name) > 1:
            raise ValidationError(
                f"flag provided but not defined: -{name}")
        if name in ("h", "help"):
            raise HelpRequested()
        if name not in KNOWN_NAMES:
            raise ValidationError(
                f"flag provided but not defined: -{name}")

        value = eq_value
        consumed_next = False
        if not has_eq and name in VALUE_NAMES:
            if i + 1 >= len(reordered):
                raise ValidationError(
                    f"flag needs an argument: -{name}")
            value = reordered[i + 1]
            consumed_next = True

        if has_eq and name in BOOL_NAMES:
            if eq_value not in BOOL_TRUE_VALUES:
                raise ValidationError(
                    f'invalid boolean value "{eq_value}" for '
                    f"-{name}: parse error")
            if eq_value in BOOL_TRUTHY:
                out.append(_canonical_form(name))
            i += 1
            continue
        if name in INT_NAMES and value is not None:
            try:
                parse_go_int(value)
            except ValueError:
                raise ValidationError(
                    f'invalid value "{value}" for flag '
                    f"-{name}: parse error")
            except OverflowError:
                raise ValidationError(
                    f'invalid value "{value}" for flag '
                    f"-{name}: value out of range")
        if name in DURATION_NAMES and value is not None:
            if parse_go_duration(value) is None:
                raise ValidationError(
                    f'invalid value "{value}" for flag '
                    f"-{name}: parse error")

        if has_eq:
            out.append(f"{_canonical_form(name)}={eq_value}")
        elif consumed_next:
            out.append(f"{_canonical_form(name)}={reordered[i + 1]}")
            i += 2
            continue
        else:
            out.append(_canonical_form(name))
        i += 1
    return out


def parse_options(args):
    """Run the full parse pipeline on raw args; return Options."""
    parser = build_parser()
    parser.raw_args = list(args)
    reordered = reorder_args(args)
    normalized = normalize_flags(reordered)
    parsed = parser.parse_args(normalized)

    opts = Options()
    opts.message = parsed.message
    opts.file_path = parsed.file_path
    opts.file_url = parsed.file_url
    opts.file_id = parsed.file_id
    opts.albums = list(parsed.albums)
    opts.file_type = parsed.file_type
    opts.caption = parsed.caption
    opts.parse_mode = parsed.parse_mode
    opts.token = parsed.token
    opts.chat_id = parsed.chat_id
    opts.base_url = parsed.base_url
    opts.proxy = parsed.proxy
    opts.no_retry = parsed.no_retry
    opts.silent = parsed.silent
    opts.json_out = parsed.json_out
    opts.dry_run = parsed.dry_run
    opts.no_trim = parsed.no_trim
    opts.discover = parsed.discover
    opts.whoami = parsed.whoami
    opts.rest = list(parsed.rest)

    opts.reply_to = parse_go_int(parsed.reply_to)
    opts.reply_to_set = any(
        a.lstrip("-").split("=")[0] in ("reply-to", "r")
        for a in normalized
        if len(a) >= 2 and a[0] == "-" and a != "--")
    opts.offset = parse_go_int(parsed.offset)
    opts.offset_set = any(
        a.lstrip("-").split("=")[0] in ("offset", "o")
        for a in normalized
        if len(a) >= 2 and a[0] == "-" and a != "--")
    opts.retries = parse_go_int(parsed.retries)
    opts.base_wait = parse_go_duration(parsed.base_wait)
    return opts


class ValidationError(Exception):
    """A validation error surfaced as `Failed: ...` exit 1."""
class Client:
    """Resolved HTTP client: base URL and optional proxy opener."""

    def __init__(self, base_url, opener):
        self.base_url = base_url.rstrip("/")
        self.opener = opener

    def call(self, method_verb, endpoint, data=None, headers=None):
        """Call one Bot API method and return the parsed result field.

        Raises ApiError for API-level failures and RuntimeError for
        network errors formatted like Go http client errors, so token
        scrubbing works identically.
        """
        url = f"{self.base_url}/bot{endpoint}"
        request = urllib.request.Request(
            url, data=data, headers=headers or {})
        open_func = (self.opener.open if self.opener is not None
                     else urllib.request.urlopen)
        try:
            with open_func(request, timeout=TIMEOUT_SECONDS) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as err:
            body_text = err.read().decode(errors="replace")
            try:
                body = json.loads(body_text)
                code = body.get("error_code", err.code)
                description = body.get("description", str(err.reason))
                retry_after = body.get("parameters", {}).get(
                    "retry_after", 0)
            except json.JSONDecodeError:
                code = err.code
                description = body_text[:200]
                retry_after = 0
            raise ApiError(code, description, retry_after)
        except (urllib.error.URLError, OSError) as err:
            reason = getattr(err, "reason", err)
            raise RuntimeError(f'{method_verb} "{url}": {reason}')

        if not payload.get("ok"):
            raise ApiError(
                payload.get("error_code", 0),
                payload.get("description", "unknown error"),
                payload.get("parameters", {}).get("retry_after", 0))
        return payload.get("result")


def is_transient(err):
    """Transient errors: network failures and HTTP 5xx API answers."""
    if isinstance(err, RuntimeError):
        return True
    return isinstance(err, ApiError) and 500 <= err.code <= 599


def retry_once(send, no_retry):
    """Run send; on a 429 API error wait retry_after and retry once."""
    try:
        return send()
    except ApiError as err:
        if no_retry or err.code != 429:
            raise
        wait = err.retry_after if err.retry_after > 0 else 5
        print(f"Rate limited. Retrying after {wait}s...", file=sys.stderr)
        time.sleep(wait)
        return send()


def execute_with_retries(send, opts):
    """Wrap send with the 429 single retry and the transient loop.

    Transient errors (network failures, HTTP 5xx) retry up to
    opts.retries times with exponential backoff: first wait is
    opts.base_wait, doubling per attempt, capped at 60s, jittered by
    plus/minus 25 percent. --no-retry disables both branches.
    """
    attempt = 0
    while True:
        try:
            return retry_once(send, opts.no_retry)
        except (ApiError, RuntimeError) as err:
            if (opts.no_retry or not is_transient(err)
                    or attempt >= opts.retries):
                raise
            attempt += 1
            wait = min(opts.base_wait * (2 ** (attempt - 1)),
                       MAX_BACKOFF_SECONDS)
            wait *= 1.0 + random.uniform(-0.25, 0.25)
            print(f"Transient error ({err}). Retry {attempt}/"
                  f"{opts.retries} in {go_duration(wait)}...",
                  file=sys.stderr)
            time.sleep(wait)


def json_output(pairs):
    """Print one compact JSON object preserving the given key order."""
    print(compact_json(dict(pairs)))


def optional_order_fields(payload, parse_mode, reply_to, silent):
    """Add parse_mode, reply_to_message_id, disable_notification."""
    if parse_mode:
        payload.append(("parse_mode", parse_mode))
    if reply_to:
        payload.append(("reply_to_message_id", reply_to))
    if silent:
        payload.append(("disable_notification", True))


def send_message_request(token, chat_id, text, parse_mode, reply_to,
                         silent, client, opts):
    payload = [("chat_id", chat_id), ("text", text)]
    optional_order_fields(payload, parse_mode, reply_to, silent)
    data = compact_json(dict(payload)).encode("utf-8")

    def send():
        result = client.call(
            "Post", f"{token}/sendMessage", data,
            {"Content-Type": "application/json"})
        return result.get("message_id")

    return execute_with_retries(send, opts)


def build_multipart(boundary, file_field, file_path, extra_fields):
    body = b""
    for key, value in extra_fields:
        body += f"--{boundary}\r\n".encode()
        body += (f'Content-Disposition: form-data; name="{key}"'
                 f"\r\n\r\n").encode()
        body += f"{value}\r\n".encode()
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as handle:
        file_data = handle.read()
    body += f"--{boundary}\r\n".encode()
    body += (f'Content-Disposition: form-data; name="{file_field}"; '
             f'filename="{filename}"\r\n').encode()
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += file_data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return body


def file_form_fields(chat_id, caption, parse_mode, reply_to, silent):
    fields = [("chat_id", str(chat_id))]
    if caption:
        fields.append(("caption", caption))
    if parse_mode:
        fields.append(("parse_mode", parse_mode))
    if reply_to:
        fields.append(("reply_to_message_id", str(reply_to)))
    if silent:
        fields.append(("disable_notification", "true"))
    return fields


def send_file_upload_request(token, chat_id, path, file_type, caption,
                             parse_mode, reply_to, silent, client, opts):
    fields = file_form_fields(chat_id, caption, parse_mode, reply_to,
                              silent)
    boundary = os.urandom(32).hex()
    body = build_multipart(boundary, file_type, path, fields)

    def send():
        result = client.call(
            "Post", f"{token}/{ENDPOINT_BY_TYPE[file_type]}", body,
            {"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return result.get("message_id")

    return execute_with_retries(send, opts)


def send_file_ref_request(token, chat_id, file_type, ref_value, caption,
                          parse_mode, reply_to, silent, client, opts):
    """Send a file by URL or file_id (JSON body, string-typed options)."""
    payload = [("chat_id", chat_id), (file_type, ref_value)]
    if caption:
        payload.append(("caption", caption))
    if parse_mode:
        payload.append(("parse_mode", parse_mode))
    if reply_to:
        payload.append(("reply_to_message_id", str(reply_to)))
    if silent:
        payload.append(("disable_notification", "true"))
    data = compact_json(dict(sorted(payload))).encode("utf-8")

    def send():
        result = client.call(
            "Post", f"{token}/{ENDPOINT_BY_TYPE[file_type]}", data,
            {"Content-Type": "application/json"})
        return result.get("message_id")

    return execute_with_retries(send, opts)


def album_media_items(items, item_types, caption, parse_mode, reply_to,
                      silent, url_mode):
    """Build the InputMedia array; options attach to the first item.

    Option values are strings in both transports, matching the Go CLI's
    JSON encoding of the media array.
    """
    media = []
    for index, (item, item_type) in enumerate(zip(items, item_types)):
        entry = {}
        if index == 0:
            if caption:
                entry["caption"] = caption
            if silent:
                entry["disable_notification"] = "true"
            if url_mode:
                entry["media"] = item
            else:
                entry["media"] = f"attach://file{index}"
            if parse_mode:
                entry["parse_mode"] = parse_mode
            if reply_to:
                entry["reply_to_message_id"] = str(reply_to)
        else:
            if url_mode:
                entry["media"] = item
            else:
                entry["media"] = f"attach://file{index}"
        entry["type"] = item_type
        media.append(entry)
    return media


def send_album_url_request(token, chat_id, items, item_types, caption,
                           parse_mode, reply_to, silent, client, opts):
    media = album_media_items(items, item_types, caption, parse_mode,
                              reply_to, silent, url_mode=True)
    payload = {"chat_id": chat_id, "media": media}
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True,
                      ensure_ascii=False).encode("utf-8")

    def send():
        result = client.call(
            "Post", f"{token}/sendMediaGroup", data,
            {"Content-Type": "application/json"})
        return [msg.get("message_id") for msg in result]

    return execute_with_retries(send, opts)


def send_album_upload_request(token, chat_id, items, item_types, caption,
                              parse_mode, reply_to, silent, client, opts):
    media = album_media_items(items, item_types, caption, parse_mode,
                              reply_to, silent, url_mode=False)
    media_json = json.dumps(
        {"chat_id": chat_id, "media": media}, separators=(",", ":"),
        sort_keys=True, ensure_ascii=False)
    boundary = os.urandom(32).hex()
    body = b""
    for key, value in [("chat_id", str(chat_id)), ("media", media_json)]:
        body += f"--{boundary}\r\n".encode()
        body += (f'Content-Disposition: form-data; name="{key}"'
                 f"\r\n\r\n").encode()
        body += f"{value}\r\n".encode()
    for index, path in enumerate(items):
        filename = os.path.basename(path)
        with open(path, "rb") as handle:
            file_data = handle.read()
        body += f"--{boundary}\r\n".encode()
        body += (f'Content-Disposition: form-data; name="file{index}"; '
                 f'filename="{filename}"\r\n').encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += file_data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    def send():
        result = client.call(
            "Post", f"{token}/sendMediaGroup", body,
            {"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return [msg.get("message_id") for msg in result]

    return execute_with_retries(send, opts)
def resolve_token(flag_value):
    return flag_value or os.environ.get("TELEGRAM_BOT_TOKEN", "")


def resolve_chat_id(flag_value):
    return flag_value or os.environ.get("TELEGRAM_CHAT_ID", "")


def detect_type(path):
    """Guess the Telegram media type: extension first, then MIME."""
    ext = os.path.splitext(path)[1].lower()
    if ext in EXT_TO_TYPE:
        return EXT_TO_TYPE[ext]
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type and mime_type in MIME_TO_TYPE:
        return MIME_TO_TYPE[mime_type]
    return "document"


def album_item_type(path):
    """Album item type: photo or video; anything else coerces to photo."""
    detected = detect_type(path)
    return detected if detected in ("photo", "video") else "photo"


def max_upload_size(file_type, base_url_flag):
    if base_url_flag:
        return MAX_SELF_HOSTED_UPLOAD
    if file_type == "photo":
        return MAX_PHOTO_UPLOAD
    return MAX_OTHER_UPLOADS


def validate_proxy(opts):
    """Reject invalid or socks proxies before any network call.

    Returns a ProxyHandler, or None when no proxy is configured.
    """
    proxy = opts.proxy or os.environ.get("TELEGRAM_PROXY", "")
    if not proxy:
        return None
    if "://" not in proxy:
        raise ValidationError(
            f'invalid proxy URL: "{proxy}" (want scheme://host)')
    parsed = urllib.parse.urlparse(proxy)
    if parsed.scheme in ("socks5", "socks5h"):
        raise ValidationError(
            "socks proxy is not supported: use http or https, or unset "
            "TELEGRAM_PROXY")
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(
            f"unsupported proxy scheme: {parsed.scheme}")
    if not parsed.netloc:
        raise ValidationError(
            f'invalid proxy URL: "{proxy}" (want scheme://host)')
    return urllib.request.ProxyHandler({"http": proxy, "https": proxy})


def build_client(opts, handler):
    """Build the API client from --base-url/env and a proxy handler."""
    base_url = (opts.base_url
                or os.environ.get("TELEGRAM_BASE_URL", "")
                or DEFAULT_BASE_URL)
    opener = urllib.request.build_opener(handler) if handler else None
    return Client(base_url, opener)


def credentials_error(opts):
    if not resolve_token(opts.token):
        return "bot token required: use --token or set TELEGRAM_BOT_TOKEN"
    if not resolve_chat_id(opts.chat_id):
        return "chat ID required: use --chat-id or set TELEGRAM_CHAT_ID"
    return None


def mode_conflict(opts):
    """Value-based conflict check: empty strings and zero do not count."""
    return (bool(opts.message) or bool(opts.file_path)
            or bool(opts.file_url) or bool(opts.file_id)
            or bool(opts.albums) or bool(opts.caption)
            or opts.reply_to != 0 or bool(opts.rest))


def bounds_errors(opts):
    """Global numeric bounds in the fixed Go order."""
    if opts.retries < 0:
        raise ValidationError("--retries must be >= 0")
    if opts.base_wait <= 0:
        raise ValidationError("--base-wait must be > 0")
    if opts.reply_to < 0:
        raise ValidationError("--reply-to must be >= 0")
    if opts.offset < 0:
        raise ValidationError("--offset must be >= 0")


def offset_mode_check(opts):
    if opts.offset != 0:
        raise ValidationError(
            "--offset is only valid with --discover-chat-id")


def dry_run_suffix(opts, caption_chars):
    parts = []
    if caption_chars:
        parts.append(f"caption ({caption_chars} chars)")
    if opts.parse_mode:
        parts.append(f"parse_mode={opts.parse_mode}")
    if opts.reply_to:
        parts.append(f"reply_to={opts.reply_to}")
    if opts.silent:
        parts.append("silent")
    return ", " + ", ".join(parts) if parts else ""


def dry_run_json_suffix(opts, caption_chars):
    return [("caption_length", caption_chars),
            ("parse_mode", opts.parse_mode),
            ("reply_to_message_id", opts.reply_to),
            ("disable_notification", bool(opts.silent))]


def run_whoami(opts):
    if mode_conflict(opts):
        raise ValidationError(
            "--whoami cannot be combined with message, file, album, "
            "caption, or reply-to flags")
    token = resolve_token(opts.token)
    if not token:
        raise ValidationError(
            "bot token required: use --token or set TELEGRAM_BOT_TOKEN")
    handler = validate_proxy(opts)
    client = build_client(opts, handler)

    def send():
        return client.call("Get", f"{token}/getMe")

    try:
        result = execute_with_retries(send, opts)
    except (ApiError, RuntimeError) as err:
        return str(err)
    if opts.json_out:
        json_output([
            ("ok", True),
            ("id", result.get("id", 0)),
            ("is_bot", result.get("is_bot", False)),
            ("first_name", result.get("first_name", "")),
            ("username", result.get("username", "")),
        ])
    else:
        print(f"@{result.get('username', '')} "
              f"(id: {result.get('id', 0)})")
    return None


def run_discover(opts):
    if mode_conflict(opts):
        raise ValidationError(
            "--discover-chat-id cannot be combined with message, file, "
            "album, caption, or reply-to flags")
    token = resolve_token(opts.token)
    if not token:
        raise ValidationError(
            "bot token required: use --token or set TELEGRAM_BOT_TOKEN")
    handler = validate_proxy(opts)
    client = build_client(opts, handler)
    endpoint = f"{token}/getUpdates"
    if opts.offset > 0:
        endpoint += f"?offset={opts.offset}"

    def send():
        return client.call("Get", endpoint)

    try:
        updates = execute_with_retries(send, opts)
    except (ApiError, RuntimeError) as err:
        return str(err)

    if not updates:
        return ("no updates found; open your bot in Telegram, send "
                "/start and any message, then retry with "
                "--discover-chat-id")

    latest = updates[-1]
    chat_id = None
    for key in ("message", "edited_message"):
        message = latest.get(key)
        if message and "chat" in message:
            chat_id = message["chat"]["id"]
            break
    if chat_id is None:
        return "no message found in latest update"

    if opts.json_out:
        json_output([("ok", True), ("chat_id", chat_id)])
    else:
        print(chat_id)
    return None


def stdin_is_char_device():
    try:
        mode = os.fstat(sys.stdin.fileno()).st_mode
        return stat_module.S_ISCHR(mode)
    except OSError:
        return True


def run_message(opts):
    offset_mode_check(opts)

    from_positional = False
    text = opts.message
    if not text:
        if opts.rest:
            text = opts.rest[0]
            from_positional = True
        else:
            if stdin_is_char_device():
                raise UsageRequested()
            text = sys.stdin.read()
            if not opts.no_trim:
                text = text.strip()
    if opts.message and opts.rest:
        raise ValidationError(
            f"unexpected positional argument {go_quote(opts.rest[0])} "
            f"next to --message")
    if from_positional:
        if opts.no_trim:
            raise ValidationError(
                "--no-trim only applies to a message read from stdin")
        if len(opts.rest) > 1:
            raise ValidationError(
                'quote multi-word messages: tg-notify "hello world"')

    err = credentials_error(opts)
    if err:
        return err
    handler = validate_proxy(opts)
    client = build_client(opts, handler)

    length = len(text)
    if length == 0 or length > MAX_MESSAGE_CHARS:
        raise ValidationError(
            f"message must be 1-{MAX_MESSAGE_CHARS} characters "
            f"({length} given)")

    chat_id = resolve_chat_id(opts.chat_id)
    if opts.dry_run:
        if opts.json_out:
            json_output([
                ("ok", True), ("dry_run", True),
                ("method", "sendMessage"),
                ("chat_id", chat_id),
                ("text_length", length),
                ("parse_mode", opts.parse_mode),
                ("reply_to_message_id", opts.reply_to),
                ("disable_notification", bool(opts.silent)),
            ])
        else:
            print(f"dry-run: sendMessage to {chat_id} ({length} chars)"
                  f"{dry_run_suffix(opts, 0)}")
        return None

    token = resolve_token(opts.token)
    try:
        msg_id = send_message_request(
            token, chat_id, text, opts.parse_mode, opts.reply_to,
            opts.silent, client, opts)
    except (ApiError, RuntimeError) as err:
        return str(err)
    if opts.json_out:
        json_output([("ok", True), ("message_id", msg_id)])
    else:
        print(f"Sent (message_id: {msg_id})")
    return None


def run_file(opts):
    offset_mode_check(opts)
    if opts.message:
        raise ValidationError(
            "--message cannot be combined with file sending; use "
            "--caption or positional text for the file caption")
    if len(opts.rest) == 1:
        if opts.caption:
            raise ValidationError(
                "positional text conflicts with --caption; use only one")
        opts.caption = opts.rest[0]
    elif len(opts.rest) > 1:
        raise ValidationError(
            f"unexpected positional argument {go_quote(opts.rest[1])}; "
            f"quote the caption as a single argument")

    sources = sum(1 for v in (opts.file_path, opts.file_url, opts.file_id)
                  if v)
    if sources > 1:
        raise ValidationError(
            "use a local file path, --url, or --file-id, not multiple")
    if opts.file_id and not opts.file_type:
        raise ValidationError(
            "--file-id requires --type (cannot auto-detect type from "
            "file_id)")
    if opts.file_type and opts.file_type not in VALID_FILE_TYPES:
        raise ValidationError(f"unknown file type: {opts.file_type}")

    err = credentials_error(opts)
    if err:
        raise ValidationError(err)
    handler = validate_proxy(opts)
    client = build_client(opts, handler)

    if opts.caption and len(opts.caption) > MAX_CAPTION_CHARS:
        raise ValidationError(
            f"caption too long ({len(opts.caption)} chars, "
            f"max {MAX_CAPTION_CHARS})")

    token = resolve_token(opts.token)
    chat_id = resolve_chat_id(opts.chat_id)

    try:
        if opts.file_path:
            return run_file_local(opts, token, chat_id, client)
        if opts.file_url:
            return run_file_url(opts, token, chat_id, client)
        return run_file_id(opts, token, chat_id, client)
    except (ApiError, RuntimeError) as err:
        return str(err)


def run_file_local(opts, token, chat_id, client):
    path = opts.file_path
    file_type = opts.file_type or detect_type(path)
    if opts.dry_run:
        emit_file_dry_run(opts, chat_id, "local", path)
        return None
    if not os.path.isfile(path):
        raise RuntimeError(f"file not found: {path}")
    size = os.path.getsize(path)
    max_size = max_upload_size(file_type, bool(opts.base_url))
    if size > max_size:
        raise RuntimeError(
            f"file too large ({size / (1024 * 1024):.1f} MB, "
            f"max {max_size / (1024 * 1024):.0f} MB for {file_type})")
    print(f"Sending {file_type}: {os.path.basename(path)} "
          f"({size / (1024 * 1024):.1f} MB)...", file=sys.stderr)
    msg_id = send_file_upload_request(
        token, chat_id, path, file_type, opts.caption, opts.parse_mode,
        opts.reply_to, opts.silent, client, opts)
    emit_send_success(opts, msg_id)
    return None


def run_file_url(opts, token, chat_id, client):
    file_type = opts.file_type or "document"
    if opts.dry_run:
        emit_file_dry_run(opts, chat_id, "url", opts.file_url)
        return None
    print(f"Sending {file_type} by URL: {opts.file_url}...",
          file=sys.stderr)
    msg_id = send_file_ref_request(
        token, chat_id, file_type, opts.file_url, opts.caption,
        opts.parse_mode, opts.reply_to, opts.silent, client, opts)
    emit_send_success(opts, msg_id)
    return None


def run_file_id(opts, token, chat_id, client):
    file_type = opts.file_type
    if opts.dry_run:
        emit_file_dry_run(opts, chat_id, "file_id", opts.file_id)
        return None
    print(f"Resending {file_type} by file_id: {opts.file_id}...",
          file=sys.stderr)
    msg_id = send_file_ref_request(
        token, chat_id, file_type, opts.file_id, opts.caption,
        opts.parse_mode, opts.reply_to, opts.silent, client, opts)
    emit_send_success(opts, msg_id)
    return None


def emit_file_dry_run(opts, chat_id, source, ref):
    if source == "local":
        shown_type = opts.file_type
        detail = f"local={ref}"
    elif source == "url":
        shown_type = opts.file_type or "document"
        detail = f"url={ref}"
    else:
        shown_type = opts.file_type
        detail = f"file_id={ref}"
    if opts.json_out:
        json_output([("ok", True), ("dry_run", True),
                     ("method", "sendFile"), ("chat_id", chat_id),
                     ("source", source), ("type", shown_type)]
                    + dry_run_json_suffix(opts, len(opts.caption)))
    else:
        print(f"dry-run: send {shown_type} file ({detail}) to {chat_id}"
              f"{dry_run_suffix(opts, len(opts.caption))}")


def emit_send_success(opts, msg_id):
    if opts.json_out:
        json_output([("ok", True), ("message_id", msg_id)])
    else:
        print(f"Sent (message_id: {msg_id})")


def run_album(opts):
    if opts.message:
        raise ValidationError("--message cannot be combined with --album")
    if opts.file_path or opts.file_url or opts.file_id:
        raise ValidationError(
            "--album cannot be combined with -f, --url, or --file-id")
    if opts.caption and len(opts.caption) > MAX_CAPTION_CHARS:
        raise ValidationError(
            f"caption too long ({len(opts.caption)} chars, "
            f"max {MAX_CAPTION_CHARS})")

    err = credentials_error(opts)
    if err:
        raise ValidationError(err)
    handler = validate_proxy(opts)
    client = build_client(opts, handler)

    items = list(opts.albums) + list(opts.rest)
    item_types = [album_item_type(item) for item in items]
    local_items = [item for item in items if "://" not in item]
    url_mode = not local_items

    try:
        for item in local_items:
            if not os.path.isfile(item):
                raise RuntimeError(f"file not found: {item}")

        if opts.dry_run:
            emit_album_dry_run(opts, resolve_chat_id(opts.chat_id), items,
                               item_types)
            return None

        if len(items) < ALBUM_MIN_ITEMS or len(items) > ALBUM_MAX_ITEMS:
            raise ValidationError(
                f"album must contain {ALBUM_MIN_ITEMS}-{ALBUM_MAX_ITEMS} "
                f"items ({len(items)} given)")
        if not url_mode and len(local_items) != len(items):
            raise ValidationError(
                "cannot mix local paths and URLs in one album")

        token = resolve_token(opts.token)
        chat_id = resolve_chat_id(opts.chat_id)
        if url_mode:
            msg_ids = send_album_url_request(
                token, chat_id, items, item_types, opts.caption,
                opts.parse_mode, opts.reply_to, opts.silent, client, opts)
        else:
            msg_ids = send_album_upload_request(
                token, chat_id, items, item_types, opts.caption,
                opts.parse_mode, opts.reply_to, opts.silent, client, opts)
    except (ApiError, RuntimeError) as err:
        return str(err)

    if opts.json_out:
        json_output([("ok", True), ("message_ids", msg_ids)])
    else:
        print(f"Sent album ({len(msg_ids)} messages)")
    return None


def emit_album_dry_run(opts, chat_id, items, item_types):
    if opts.json_out:
        json_output([("ok", True), ("dry_run", True),
                     ("method", "sendMediaGroup"), ("chat_id", chat_id),
                     ("item_count", len(items)), ("types", item_types)]
                    + dry_run_json_suffix(opts, len(opts.caption)))
    else:
        print(f"dry-run: send album ({len(items)} items)"
              f"{dry_run_suffix(opts, len(opts.caption))}")


def run(args):
    for arg in args:
        if arg in VERSION_FLAG_TOKENS:
            print(read_skill_version())
            return None

    try:
        opts = parse_options(args)
        bounds_errors(opts)
        if opts.whoami:
            return run_whoami(opts)
        if opts.discover:
            return run_discover(opts)
        if opts.albums:
            return run_album(opts)
        if opts.file_path or opts.file_url or opts.file_id:
            return run_file(opts)
        return run_message(opts)
    except ValidationError as err:
        return str(err)


def main(argv=None):
    load_dotenv()
    args = sys.argv[1:] if argv is None else argv
    try:
        err = run(args)
    except UsageRequested:
        print(USAGE_TEXT, file=sys.stderr)
        raise SystemExit(1)
    except HelpRequested:
        print(USAGE_TEXT)
        raise SystemExit(0)
    if err is not None:
        print(f"Failed: {scrub_secrets(str(err))}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
