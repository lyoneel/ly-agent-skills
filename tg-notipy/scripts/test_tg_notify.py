#!/usr/bin/env python3
"""Stdlib unit tests for tg_notify.py parity behaviour."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tg_notify


class TestReorderArgs(unittest.TestCase):
    def test_flags_before_positional_unchanged(self):
        self.assertEqual(
            tg_notify.reorder_args(["-f", "a.png", "-c", "cap"]),
            ["-f", "a.png", "-c", "cap"])

    def test_flags_after_positional_moved_ahead(self):
        self.assertEqual(
            tg_notify.reorder_args(["stray", "-f", "a.png"]),
            ["-f", "a.png", "stray"])

    def test_bool_flag_after_positional_keeps_no_value(self):
        self.assertEqual(
            tg_notify.reorder_args(["text", "--no-retry"]),
            ["--no-retry", "text"])

    def test_equals_form_is_single_token(self):
        self.assertEqual(
            tg_notify.reorder_args(["text", "--file=a.png"]),
            ["--file=a.png", "text"])

    def test_long_and_short_mixed(self):
        self.assertEqual(
            tg_notify.reorder_args(
                ["hello", "--file", "a.png", "-c", "cap"]),
            ["--file", "a.png", "-c", "cap", "hello"])

    def test_separator_stops_flag_processing(self):
        self.assertEqual(
            tg_notify.reorder_args(["--dry-run", "--", "-m", "hi"]),
            ["--dry-run", "--", "-m", "hi"])

    def test_separator_positional_stays(self):
        self.assertEqual(
            tg_notify.reorder_args(["stray", "--", "text"]),
            ["stray", "--", "text"])

    def test_album_appends(self):
        self.assertEqual(
            tg_notify.reorder_args(["-a", "a.jpg", "b.jpg"]),
            ["-a", "a.jpg", "b.jpg"])


class TestScrubSecrets(unittest.TestCase):
    def test_token_in_url(self):
        self.assertEqual(
            tg_notify.scrub_secrets(
                'Post "https://api.telegram.org/bot12345:ABC-xyz/'
                'sendMessage": timeout'),
            'Post "https://api.telegram.org/bot<token>/sendMessage": '
            'timeout')

    def test_no_token_untouched(self):
        text = "caption too long (1025 chars, max 1024)"
        self.assertEqual(tg_notify.scrub_secrets(text), text)


class TestDetectType(unittest.TestCase):
    def test_extension_first(self):
        self.assertEqual(tg_notify.detect_type("x.png"), "photo")
        self.assertEqual(tg_notify.detect_type("x.ogg"), "voice")
        self.assertEqual(tg_notify.detect_type("x.mp4"), "video")
        self.assertEqual(tg_notify.detect_type("x.mp3"), "audio")

    def test_unknown_extension_falls_back_to_document(self):
        self.assertEqual(tg_notify.detect_type("x.bin"), "document")

    def test_extension_wins_over_mime(self):
        self.assertEqual(tg_notify.detect_type("x.bmp"), "photo")

    def test_album_item_type_coerces_to_photo(self):
        self.assertEqual(tg_notify.album_item_type("x.txt"), "photo")
        self.assertEqual(tg_notify.album_item_type("x.mp4"), "video")
        self.assertEqual(tg_notify.album_item_type("x.png"), "photo")


class TestDuration(unittest.TestCase):
    def test_parse_valid(self):
        self.assertEqual(tg_notify.parse_go_duration("2s"), 2.0)
        self.assertEqual(tg_notify.parse_go_duration("1m30s"), 90.0)
        self.assertEqual(tg_notify.parse_go_duration("500ms"), 0.5)
        self.assertEqual(tg_notify.parse_go_duration("1.5s"), 1.5)
        self.assertEqual(tg_notify.parse_go_duration("0"), 0.0)
        self.assertEqual(tg_notify.parse_go_duration("2"), None)
        self.assertEqual(tg_notify.parse_go_duration("abc"), None)

    def test_format(self):
        self.assertEqual(tg_notify.go_duration(2.0), "2s")
        self.assertEqual(tg_notify.go_duration(0.5), "500ms")
        self.assertEqual(tg_notify.go_duration(90.0), "90s")


class TestVersion(unittest.TestCase):
    def test_version_reads_skill_frontmatter(self):
        version = tg_notify.read_skill_version()
        self.assertNotEqual(version, "unknown")
        self.assertRegex(version, r"^\d{8}-\d+$")

    def test_version_flag_prints_live_value(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["--version"])
        self.assertIsNone(err)
        self.assertEqual(
            stdout.getvalue().strip(), tg_notify.read_skill_version())

    def test_version_short_and_long(self):
        for arg in ("-v", "--version"):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run([arg])
            self.assertIsNone(err)

    def test_version_beats_parse_errors(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["--version", "--bogus"])
        self.assertIsNone(err)
        self.assertEqual(
            stdout.getvalue().strip(), tg_notify.read_skill_version())


class TestDispatch(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def _stdout_of(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stdout.getvalue(), caught.exception.code

    def test_no_args_terminal_stdin_prints_usage_exit_1(self):
        fake_stdin = io.StringIO("")
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin),                 mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=True):
            stderr, code = self._stderr_of([])
        self.assertEqual(code, 1)
        self.assertTrue(stderr.startswith("usage: tg-notify [message]"))

    def test_help_prints_usage_to_stdout_exit_0(self):
        stdout, code = self._stdout_of(["-h"])
        self.assertEqual(code, 0)
        self.assertTrue(stdout.startswith("usage: tg-notify [message]"))

    def test_help_long_form(self):
        stdout, code = self._stdout_of(["--help"])
        self.assertEqual(code, 0)
        self.assertTrue(stdout.startswith("usage: tg-notify [message]"))

    def test_help_beats_bad_value(self):
        stdout, code = self._stdout_of(["-h", "-B", "abc"])
        self.assertEqual(code, 0)

    def test_help_beats_unknown_flag(self):
        stdout, code = self._stdout_of(["-h", "--bogus"])
        self.assertEqual(code, 0)

    def test_unknown_flag_before_help_wins(self):
        stderr, code = self._stderr_of(["--bogus", "-h"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: flag provided but not defined: -bogus\n")

    def test_unknown_flag_error_string(self):
        stderr, code = self._stderr_of(["--bogus", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: flag provided but not defined: -bogus\n")

    def test_missing_value_error_string(self):
        stderr, code = self._stderr_of(["--message"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: flag needs an argument: -message\n")

    def test_triple_dash_bad_syntax(self):
        stderr, code = self._stderr_of(["---message", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: bad flag syntax: ---message\n")

    def test_bare_equals_bad_syntax(self):
        stderr, code = self._stderr_of(["--=x"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: bad flag syntax: --=x\n")

    def test_bool_equals_invalid_value(self):
        stderr, code = self._stderr_of(["-j=maybe", "--dry-run", "hi"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            'Failed: invalid boolean value "maybe" for -j: '
            'parse error\n')

    def test_bool_equals_false(self):
        with mock.patch.object(tg_notify, "read_skill_version",
                               return_value="x"):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
                stderr = io.StringIO()
                stdout = io.StringIO()
                with contextlib.redirect_stderr(stderr),                         contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-j=false", "--dry-run", "hi"])
        self.assertIsNone(err)

    def test_single_dash_multiletter_rejected(self):
        stderr, code = self._stderr_of(["-message", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: flag provided but not defined: -message\n")

    def test_double_dash_single_letter_accepted(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--j", "--D", "x"])
        self.assertIsNone(err)
        self.assertIn("sendMessage", stdout.getvalue())

    def test_discover_requires_token(self):
        stderr, code = self._stderr_of(["--discover-chat-id"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: bot token required: use --token or set "
            "TELEGRAM_BOT_TOKEN\n")

    def test_file_id_requires_type(self):
        stderr, code = self._stderr_of(["--file-id", "abc123"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --file-id requires --type (cannot auto-detect type "
            "from file_id)\n")

    def test_message_conflicts_with_file(self):
        stderr, code = self._stderr_of(["-m", "x", "-f", "a.png"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --message cannot be combined with file sending; use "
            "--caption or positional text for the file caption\n")

    def test_multiple_positionals_quote_error(self):
        stderr, code = self._stderr_of(["x", "y"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            'Failed: quote multi-word messages: tg-notify "hello world"\n')

    def test_positional_conflicts_with_caption(self):
        stderr, code = self._stderr_of(
            ["cap", "-c", "other", "-f", "a.png"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: positional text conflicts with --caption; use only "
            "one\n")

    def test_credentials_checked_before_file_exists(self):
        stderr, code = self._stderr_of(["stray", "-f", "missing.png"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: bot token required: use --token or set "
            "TELEGRAM_BOT_TOKEN\n")

    def test_positional_next_to_message_flag(self):
        stderr, code = self._stderr_of(
            ["-m", "a", "stray", "--token", "t", "--chat-id", "1"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            'Failed: unexpected positional argument "stray" next to '
            '--message\n')

    def test_no_trim_only_stdin(self):
        stderr, code = self._stderr_of(
            ["hi", "--no-trim", "--token", "t", "--chat-id", "1"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --no-trim only applies to a message read from "
            "stdin\n")


class TestBounds(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_reply_to_negative(self):
        stderr, code = self._stderr_of(["--reply-to", "-1", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: --reply-to must be >= 0\n")

    def test_offset_negative(self):
        stderr, code = self._stderr_of(["-d", "--offset", "-1"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: --offset must be >= 0\n")

    def test_retries_negative(self):
        stderr, code = self._stderr_of(["--retries", "-1", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: --retries must be >= 0\n")

    def test_base_wait_zero(self):
        stderr, code = self._stderr_of(["--base-wait", "0", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: --base-wait must be > 0\n")

    def test_offset_mode_check(self):
        stderr, code = self._stderr_of(["--offset", "5", "hi"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --offset is only valid with --discover-chat-id\n")

    def test_bounds_order_retries_first(self):
        stderr, _ = self._stderr_of(
            ["-r", "-1", "--retries", "-1", "x"])
        self.assertEqual(stderr, "Failed: --retries must be >= 0\n")

    def test_retries_parse_error(self):
        stderr, code = self._stderr_of(["--retries", "abc", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            'Failed: invalid value "abc" for flag -retries: '
            'parse error\n')

    def test_base_wait_parse_error(self):
        stderr, code = self._stderr_of(["-B", "2", "x"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            'Failed: invalid value "2" for flag -B: parse error\n')


class TestProxy(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_invalid_proxy(self):
        stderr, code = self._stderr_of(
            ["--proxy", "not-a-url", "--dry-run", "hi"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            'Failed: invalid proxy URL: "not-a-url" (want '
            'scheme://host)\n')

    def test_socks_rejected(self):
        stderr, code = self._stderr_of(
            ["--proxy", "socks5://1.2.3.4:1080", "--dry-run", "x"])
        self.assertEqual(code, 1)
        self.assertIn("socks proxy is not supported", stderr)

    def test_socks_env_rejected(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_PROXY": "socks5h://x:1"}):
            stderr, code = self._stderr_of(["--dry-run", "x"])
        self.assertEqual(code, 1)
        self.assertIn("socks proxy is not supported", stderr)

    def test_unsupported_scheme(self):
        stderr, code = self._stderr_of(
            ["--proxy", "ftp://x", "--dry-run", "hi"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: unsupported proxy scheme: ftp\n")

    def test_valid_proxy_dry_run_passes(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--proxy", "http://1.2.3.4:8080", "--dry-run", "hi"])
        self.assertIsNone(err)

    def test_proxy_env_invalid(self):
        with mock.patch.dict(os.environ, {"TELEGRAM_PROXY": "garbage"}):
            stderr, code = self._stderr_of(["--dry-run", "x"])
        self.assertEqual(code, 1)
        self.assertIn("invalid proxy URL", stderr)


class TestDotEnv(unittest.TestCase):
    def test_env_file_fills_unset_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = os.path.join(tmp, ".env")
            with open(env_path, "w", encoding="utf-8") as handle:
                handle.write("TELEGRAM_BOT_TOKEN=fromfile\n"
                             "TELEGRAM_CHAT_ID=77\n"
                             "# comment\n\n")
            with mock.patch.object(tg_notify.os, "getcwd",
                                   return_value=tmp),                     mock.patch("builtins.open",
                               unittest.mock.mock_open(
                                   read_data=(
                                       "TELEGRAM_BOT_TOKEN=fromfile\n"
                                       "TELEGRAM_CHAT_ID=77\n"))):
                with mock.patch.dict(os.environ, {}, clear=True):
                    tg_notify.load_dotenv()
                    self.assertEqual(
                        os.environ["TELEGRAM_BOT_TOKEN"], "fromfile")
                    self.assertEqual(os.environ["TELEGRAM_CHAT_ID"], "77")

    def test_env_file_does_not_override(self):
        with mock.patch("builtins.open",
                        unittest.mock.mock_open(
                            read_data="TELEGRAM_BOT_TOKEN=fromfile\n")):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "real"}, clear=True):
                tg_notify.load_dotenv()
                self.assertEqual(
                    os.environ["TELEGRAM_BOT_TOKEN"], "real")

    def test_env_file_base_url_not_loaded(self):
        with mock.patch("builtins.open",
                        unittest.mock.mock_open(
                            read_data="TELEGRAM_BASE_URL=http://x\n")):
            with mock.patch.dict(os.environ, {}, clear=True):
                tg_notify.load_dotenv()
                self.assertNotIn("TELEGRAM_BASE_URL", os.environ)

    def test_missing_env_file_ok(self):
        with mock.patch("builtins.open",
                        side_effect=OSError("missing")):
            tg_notify.load_dotenv()


class TestAlbum(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name in ("a.jpg", "b.jpg", "c.txt", "v.mp4"):
            open(os.path.join(self.tmp.name, name), "wb").write(b"x")

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def _path(self, name):
        return os.path.join(self.tmp.name, name)

    def test_album_conflicts_file(self):
        stderr, code = self._stderr_of(
            ["--album", self._path("a.jpg"), self._path("b.jpg"),
             "-f", self._path("c.txt")])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --album cannot be combined with -f, --url, or "
            "--file-id\n")

    def test_album_conflicts_message(self):
        stderr, code = self._stderr_of(
            ["--album", self._path("a.jpg"), self._path("b.jpg"),
             "-m", "hi"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: --message cannot be combined with --album\n")

    def test_album_too_few(self):
        stderr, code = self._stderr_of(["--album", self._path("a.jpg")])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr, "Failed: album must contain 2-10 items (1 given)\n")

    def test_album_mixed_transport(self):
        stderr, code = self._stderr_of(
            ["--album", self._path("a.jpg"), "https://x/b.jpg"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: cannot mix local paths and URLs in one album\n")

    def test_album_missing_file_fails_fast(self):
        stderr, code = self._stderr_of(
            ["--album", self._path("a.jpg"), self._path("missing.jpg")])
        self.assertEqual(code, 1)
        self.assertIn("file not found", stderr)

    def test_album_dry_run_no_count_check(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["--album", self._path("a.jpg"),
                                 "--dry-run"])
        self.assertIsNone(err)
        self.assertIn("send album (1 items)", stdout.getvalue())

    def test_album_dry_run_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--album", "https://x/a.jpg", "https://x/b.mp4",
                 "--dry-run", "--json"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["method"], "sendMediaGroup")
        self.assertEqual(data["item_count"], 2)
        self.assertEqual(data["types"], ["photo", "video"])

    def test_album_dry_run_coerces_to_photo(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--album", self._path("c.txt"), self._path("c.txt"),
                 "--dry-run", "--json"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["types"], ["photo", "photo"])

    def test_album_send_success(self):
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=[1, 2]) as send:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--album", self._path("a.jpg"), self._path("b.jpg"),
                     "-c", "cap"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue(), "Sent album (2 messages)\n")
        self.assertEqual(send.call_args.args[3], ["photo", "photo"])

    def test_album_send_json(self):
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=[1, 2]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--album", self._path("a.jpg"), self._path("b.jpg"),
                     "--json"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data, {"ok": True, "message_ids": [1, 2]})

    def test_album_trailing_positionals(self):
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=[1, 2]) as send:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--album", self._path("a.jpg"), self._path("b.jpg")])
        self.assertIsNone(err)

    def test_album_media_options_first_item(self):
        media = tg_notify.album_media_items(
            ["a.jpg", "b.jpg"], ["photo", "photo"], "cap", "HTML", 7,
            True, url_mode=False)
        self.assertEqual(media[0]["caption"], "cap")
        self.assertEqual(media[0]["media"], "attach://file0")
        self.assertEqual(media[1]["media"], "attach://file1")
        self.assertNotIn("caption", media[1])

    def test_album_media_url_mode(self):
        media = tg_notify.album_media_items(
            ["https://x/a.jpg", "https://x/b.mp4"], ["photo", "video"],
            "", "", 0, False, url_mode=True)
        self.assertEqual(media[0]["media"], "https://x/a.jpg")
        self.assertEqual(media[1]["media"], "https://x/b.mp4")


class TestWhoami(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_whoami_requires_token(self):
        stderr, code = self._stderr_of(["--whoami"])
        self.assertEqual(code, 1)
        self.assertIn("bot token required", stderr)

    def test_whoami_conflict(self):
        stderr, code = self._stderr_of(
            ["--whoami", "-m", "hi", "--token", "t"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --whoami cannot be combined with message, file, "
            "album, caption, or reply-to flags\n")

    def test_whoami_success(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "Mock",
                                             "username": "mockbot"}):
            stdout = io.StringIO()
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["--whoami"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue(), "@mockbot (id: 7)\n")

    def test_whoami_json(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "Mock",
                                             "username": "mockbot"}):
            stdout = io.StringIO()
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["--whoami", "--json"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["username"], "mockbot")
        self.assertTrue(data["ok"])

    def test_whoami_api_error_handled(self):
        with mock.patch.object(tg_notify.Client, "call",
                               side_effect=tg_notify.ApiError(
                                   401, "Unauthorized")):
            stderr, code = self._stderr_of(
                ["--whoami", "--token", "t"])
        self.assertEqual(code, 1)
        self.assertIn("Failed: HTTP 401: Unauthorized", stderr)


class TestDiscover(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_discover_conflict(self):
        stderr, code = self._stderr_of(
            ["-d", "-m", "hi", "--token", "t"])
        self.assertEqual(code, 1)
        self.assertEqual(
            stderr,
            "Failed: --discover-chat-id cannot be combined with message, "
            "file, album, caption, or reply-to flags\n")

    def test_discover_no_updates(self):
        with mock.patch.object(tg_notify.Client, "call", return_value=[]):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stderr, code = self._stderr_of(["-d"])
        self.assertEqual(code, 1)
        self.assertIn("no updates found", stderr)

    def test_discover_success(self):
        updates = [{"update_id": 1, "message": {"chat": {"id": 123}}}]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            stdout = io.StringIO()
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-d"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue().strip(), "123")

    def test_discover_edited_message(self):
        updates = [
            {"update_id": 1, "edited_message": {"chat": {"id": -888}}}]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            stdout = io.StringIO()
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-d"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue().strip(), "-888")

    def test_discover_channel_post_not_supported(self):
        updates = [
            {"update_id": 9, "channel_post": {"chat": {"id": -100777}}}]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stderr, code = self._stderr_of(["-d"])
        self.assertEqual(code, 1)
        self.assertIn("no message found in latest update", stderr)

    def test_discover_json(self):
        updates = [{"update_id": 1, "message": {"chat": {"id": 123}}}]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            stdout = io.StringIO()
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-d", "--json"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data, {"ok": True, "chat_id": 123})

    def test_discover_offset_appended(self):
        captured = {}

        def fake_call(self_client, verb, endpoint, data=None,
                      headers=None):
            captured["endpoint"] = endpoint
            return [{"update_id": 1, "message": {"chat": {"id": 5}}}]

        with mock.patch.object(tg_notify.Client, "call", fake_call):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                err = tg_notify.run(["-d", "--offset", "100"])
        self.assertIsNone(err)
        self.assertIn("?offset=100", captured["endpoint"])

    def test_discover_offset_zero_not_appended(self):
        captured = {}

        def fake_call(self_client, verb, endpoint, data=None,
                      headers=None):
            captured["endpoint"] = endpoint
            return [{"update_id": 1, "message": {"chat": {"id": 5}}}]

        with mock.patch.object(tg_notify.Client, "call", fake_call):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                err = tg_notify.run(["-d", "--offset", "0"])
        self.assertIsNone(err)
        self.assertNotIn("offset", captured["endpoint"])


class TestRetry(unittest.TestCase):
    def test_429_retried_once_with_default_wait(self):
        calls = []

        def send():
            calls.append(1)
            if len(calls) == 1:
                raise tg_notify.ApiError(429, "Too Many Requests", 0)
            return 7

        with mock.patch.object(tg_notify.time, "sleep"):
            self.assertEqual(tg_notify.retry_once(send, False), 7)
        self.assertEqual(len(calls), 2)

    def test_no_retry_skips_second_attempt(self):
        def send():
            raise tg_notify.ApiError(429, "Too Many Requests", 3)

        with self.assertRaises(tg_notify.ApiError):
            tg_notify.retry_once(send, True)

    def test_retry_uses_retry_after(self):
        sleeps = []

        def send():
            raise tg_notify.ApiError(429, "Too Many Requests", 9)

        with mock.patch.object(
                tg_notify.time, "sleep", side_effect=sleeps.append):
            with self.assertRaises(tg_notify.ApiError):
                tg_notify.retry_once(send, False)
        self.assertEqual(sleeps, [9])

    def _opts(self, retries, base_wait, no_retry=False):
        opts = tg_notify.Options()
        opts.retries = retries
        opts.base_wait = base_wait
        opts.no_retry = no_retry
        return opts

    def test_transient_retries_with_backoff(self):
        calls = []

        def send():
            calls.append(1)
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        sleeps = []
        with mock.patch.object(tg_notify.time, "sleep",
                               side_effect=sleeps.append),                 mock.patch.object(tg_notify.random, "uniform",
                                  return_value=0.0):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(send, self._opts(3, 2.0))
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [2.0, 4.0, 8.0])

    def test_transient_backoff_capped(self):
        calls = []

        def send():
            calls.append(1)
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        sleeps = []
        with mock.patch.object(tg_notify.time, "sleep",
                               side_effect=sleeps.append),                 mock.patch.object(tg_notify.random, "uniform",
                                  return_value=0.0):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(
                    send, self._opts(10, 30.0))
        self.assertEqual(sleeps[:3], [30.0, 60.0, 60.0])

    def test_no_retry_disables_transient(self):
        def send():
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        with self.assertRaises(RuntimeError):
            tg_notify.execute_with_retries(
                send, self._opts(5, 2.0, no_retry=True))

    def test_retries_zero_no_transient(self):
        calls = []

        def send():
            calls.append(1)
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        with self.assertRaises(RuntimeError):
            tg_notify.execute_with_retries(send, self._opts(0, 2.0))
        self.assertEqual(len(calls), 1)

    def test_429_survives_retries_zero(self):
        calls = []

        def send():
            calls.append(1)
            if len(calls) == 1:
                raise tg_notify.ApiError(429, "Too Many Requests", 1)
            return 9

        with mock.patch.object(tg_notify.time, "sleep"):
            self.assertEqual(
                tg_notify.execute_with_retries(send, self._opts(0, 2.0)),
                9)

    def test_5xx_is_transient(self):
        calls = []

        def send():
            calls.append(1)
            if len(calls) == 1:
                raise tg_notify.ApiError(502, "Bad Gateway")
            return 11

        with mock.patch.object(tg_notify.time, "sleep"):
            self.assertEqual(
                tg_notify.execute_with_retries(
                    send, self._opts(2, 1.0)), 11)

    def test_400_not_transient(self):
        calls = []

        def send():
            calls.append(1)
            raise tg_notify.ApiError(400, "Bad Request")

        with self.assertRaises(tg_notify.ApiError):
            tg_notify.execute_with_retries(send, self._opts(3, 1.0))
        self.assertEqual(len(calls), 1)

    def test_jitter_within_25_percent(self):
        def send():
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        sleeps = []
        with mock.patch.object(tg_notify.time, "sleep",
                               side_effect=sleeps.append):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(send, self._opts(2, 2.0))
        self.assertTrue(1.5 <= sleeps[0] <= 2.5)


class TestDryRun(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def test_message_dry_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["--dry-run", "--json", "hello"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["method"], "sendMessage")
        self.assertEqual(data["text_length"], 5)
        self.assertTrue(data["dry_run"])

    def test_message_dry_json_options(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "--reply-to", "5", "--silent",
                 "--parse-mode", "HTML", "hello"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["reply_to_message_id"], 5)
        self.assertTrue(data["disable_notification"])
        self.assertEqual(data["parse_mode"], "HTML")

    def test_file_dry_no_stat(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--file", "/nonexistent/x.png"])
        self.assertIsNone(err)
        self.assertIn("local=/nonexistent/x.png", stdout.getvalue())

    def test_file_dry_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "-f", "a.png", "-c", "cap"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["source"], "local")
        self.assertEqual(data["caption_length"], 3)

    def test_album_dry_stats_local(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(
                    ["--dry-run", "--album", "/nonexistent/a.jpg",
                     "/nonexistent/b.jpg"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("file not found", stderr.getvalue())

    def test_dry_run_requires_token(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as caught:
                    tg_notify.main(["--dry-run", "hi"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("bot token required", stderr.getvalue())


class TestStdin(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _run_stdin(self, text, extra_args):
        fake_stdin = io.StringIO(text)
        stdout = io.StringIO()
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin),                 mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=False),                 contextlib.redirect_stdout(stdout):
            err = tg_notify.run(extra_args + ["--dry-run", "--json"])
        return err, stdout.getvalue()

    def test_stdin_trimmed(self):
        err, out = self._run_stdin("  hello  \n", [])
        self.assertIsNone(err)
        data = json.loads(out)
        self.assertEqual(data["text_length"], 5)

    def test_stdin_no_trim(self):
        err, out = self._run_stdin("  hello  \n", ["--no-trim"])
        self.assertIsNone(err)
        data = json.loads(out)
        self.assertEqual(data["text_length"], 10)

    def test_empty_stdin_fails(self):
        fake_stdin = io.StringIO("")
        stderr = io.StringIO()
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin),                 mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=False),                 contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(["--dry-run"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn(
            "message must be 1-4096 characters (0 given)",
            stderr.getvalue())

    def test_message_flag_beats_stdin(self):
        err, out = self._run_stdin("fromstdin", ["-m", "explicit"])
        self.assertIsNone(err)
        data = json.loads(out)
        self.assertEqual(data["text_length"], 8)


class TestFileMode(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_type_animation_sticker_valid(self):
        for file_type in ("animation", "sticker"):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--dry-run", "--json", "-f", "a.png", "--type",
                     file_type])
            self.assertIsNone(err)
            data = json.loads(stdout.getvalue())
            self.assertEqual(data["type"], file_type)

    def test_unknown_type(self):
        stderr, code = self._stderr_of(
            ["--dry-run", "-f", "a.png", "--type", "bogus"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "Failed: unknown file type: bogus\n")

    def test_caption_too_long(self):
        stderr, code = self._stderr_of(
            ["-f", "a.jpg", "-c", "x" * 1025])
        self.assertEqual(code, 1)
        self.assertIn("caption too long", stderr)

    def test_file_not_found(self):
        stderr, code = self._stderr_of(["-f", "/nonexistent/z.png"])
        self.assertEqual(code, 1)
        self.assertIn("file not found", stderr)

    def test_url_dry_defaults_document(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "--url", "https://x/y"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["type"], "document")
        self.assertEqual(data["source"], "url")

    def test_base_url_flag_relaxes_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "big.bin")
            with open(path, "wb") as handle:
                handle.seek(60 * 1024 * 1024 - 1)
                handle.write(b"\0")
            with mock.patch.object(tg_notify, "send_file_upload_request",
                                   return_value=1):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout),                         contextlib.redirect_stderr(io.StringIO()):
                    err = tg_notify.run(
                        ["-f", path, "--base-url", "http://self:8081"])
            self.assertIsNone(err)

    def test_base_url_off_keeps_50mb(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "big.bin")
            with open(path, "wb") as handle:
                handle.seek(60 * 1024 * 1024 - 1)
                handle.write(b"\0")
            stderr, code = self._stderr_of(["-f", path])
            self.assertEqual(code, 1)
            self.assertIn("file too large", stderr)

    def test_aliases_chatid_parsemode(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--chatid", "43", "--parsemode", "HTML", "--dry-run",
                 "--json", "x"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["chat_id"], "43")
        self.assertEqual(data["parse_mode"], "HTML")

    def test_json_success_message(self):
        with mock.patch.object(tg_notify, "send_message_request",
                               return_value=857):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--json", "hello"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data, {"ok": True, "message_id": 857})

    def test_json_failure_still_failed_prefix(self):
        stderr, code = self._stderr_of(
            ["--json", "-m", "x" * 4097])
        self.assertEqual(code, 1)
        self.assertTrue(stderr.startswith("Failed:"))
class TestGoIntParsing(unittest.TestCase):
    """parse_go_int mirrors Go's strconv.ParseInt(s, 0, 64)."""

    def test_decimal(self):
        self.assertEqual(tg_notify.parse_go_int("0"), 0)
        self.assertEqual(tg_notify.parse_go_int("5"), 5)
        self.assertEqual(tg_notify.parse_go_int("42"), 42)

    def test_sign(self):
        self.assertEqual(tg_notify.parse_go_int("+5"), 5)
        self.assertEqual(tg_notify.parse_go_int("-7"), -7)

    def test_hex_prefix(self):
        self.assertEqual(tg_notify.parse_go_int("0x10"), 16)
        self.assertEqual(tg_notify.parse_go_int("0X10"), 16)
        self.assertEqual(tg_notify.parse_go_int("0x1f"), 31)
        self.assertEqual(tg_notify.parse_go_int("-0x1"), -1)

    def test_octal_prefix(self):
        self.assertEqual(tg_notify.parse_go_int("0o17"), 15)
        self.assertEqual(tg_notify.parse_go_int("0O17"), 15)

    def test_binary_prefix(self):
        self.assertEqual(tg_notify.parse_go_int("0b101"), 5)
        self.assertEqual(tg_notify.parse_go_int("0B11"), 3)

    def test_leading_zero_is_octal(self):
        self.assertEqual(tg_notify.parse_go_int("010"), 8)
        self.assertEqual(tg_notify.parse_go_int("007"), 7)
        self.assertEqual(tg_notify.parse_go_int("0010"), 8)

    def test_octal_rejects_digit_8(self):
        with self.assertRaises(ValueError):
            tg_notify.parse_go_int("08")
        with self.assertRaises(ValueError):
            tg_notify.parse_go_int("09")

    def test_underscore_between_digits(self):
        self.assertEqual(tg_notify.parse_go_int("1_0"), 10)
        self.assertEqual(tg_notify.parse_go_int("0x10_0"), 256)

    def test_underscore_after_prefix(self):
        self.assertEqual(tg_notify.parse_go_int("0x_5"), 5)

    def test_bad_underscore_positions(self):
        for bad in ("_5", "5_", "1__0", "-_5"):
            with self.assertRaises(ValueError):
                tg_notify.parse_go_int(bad)

    def test_invalid_syntax(self):
        for bad in ("abc", "0x", "0xG", "1.5", "5e2", "", " ", "-", "+"):
            with self.assertRaises(ValueError):
                tg_notify.parse_go_int(bad)

    def test_int64_boundaries(self):
        self.assertEqual(
            tg_notify.parse_go_int("9223372036854775807"),
            9223372036854775807)
        self.assertEqual(
            tg_notify.parse_go_int("-9223372036854775808"),
            -9223372036854775808)

    def test_int64_overflow(self):
        for big in ("9223372036854775808", "-9223372036854775809",
                    "9" * 25):
            with self.assertRaises(OverflowError):
                tg_notify.parse_go_int(big)

    def test_flag_overflow_error_string(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(
                    ["--retries", "99999999999999999999", "x"])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(
            stderr.getvalue(),
            'Failed: invalid value "99999999999999999999" for flag '
            '-retries: value out of range\n')

    def test_flag_hex_value_accepted(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["-r", "0x5", "--dry-run", "--json", "hi"])
        self.assertIsNone(err)
        self.assertEqual(json.loads(stdout.getvalue())
                         ["reply_to_message_id"], 5)

    def test_flag_octal_leading_zero_accepted(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["-r", "010", "--dry-run", "--json", "hi"])
        self.assertIsNone(err)
        self.assertEqual(json.loads(stdout.getvalue())
                         ["reply_to_message_id"], 8)

    def test_flag_octal_digit_8_rejected(self):
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit):
                    tg_notify.main(["-r", "08", "x"])
        self.assertIn("parse error", stderr.getvalue())


class TestGoDurationParsingEdges(unittest.TestCase):
    def test_leading_dot_fraction(self):
        self.assertEqual(tg_notify.parse_go_duration(".5s"), 0.5)

    def test_small_fractions(self):
        self.assertEqual(tg_notify.parse_go_duration("0.001s"), 0.001)

    def test_compound_units(self):
        self.assertEqual(tg_notify.parse_go_duration("1s500ms"), 1.5)
        self.assertEqual(tg_notify.parse_go_duration("1m30.5s"), 90.5)
        self.assertEqual(tg_notify.parse_go_duration("1us500ns"),
                         1.5e-06)

    def test_hours(self):
        self.assertEqual(tg_notify.parse_go_duration("1.5h"), 5400.0)
        self.assertEqual(tg_notify.parse_go_duration("25h"), 90000.0)

    def test_sign(self):
        self.assertEqual(tg_notify.parse_go_duration("-2s"), -2.0)
        self.assertEqual(tg_notify.parse_go_duration("+2s"), 2.0)

    def test_micro_symbol(self):
        self.assertAlmostEqual(
            tg_notify.parse_go_duration("5\u00b5s"), 5e-6)

    def test_invalid_forms(self):
        for bad in ("0.5", "1.", "1_0s", "s", "1x", "", "1.s",
                    "1.5", "abc", "2", "-"):
            self.assertIsNone(tg_notify.parse_go_duration(bad),
                              f"{bad} should be invalid")

    def test_zero_special_case(self):
        self.assertEqual(tg_notify.parse_go_duration("0"), 0.0)

    def test_base_wait_fractional_flag(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["-B", ".5s", "--dry-run", "hi"])
        self.assertIsNone(err)


class TestGoDurationFormat(unittest.TestCase):
    def test_whole_seconds(self):
        self.assertEqual(tg_notify.go_duration(2.0), "2s")
        self.assertEqual(tg_notify.go_duration(90.0), "90s")

    def test_fractional_seconds(self):
        self.assertEqual(tg_notify.go_duration(2.143603747),
                         "2.143603747s")

    def test_milliseconds(self):
        self.assertEqual(tg_notify.go_duration(0.5), "500ms")
        self.assertEqual(tg_notify.go_duration(0.93027207),
                         "930.27207ms")

    def test_sub_millisecond(self):
        self.assertEqual(tg_notify.go_duration(0.0005), "0.5ms")

    def test_one_second_boundary(self):
        self.assertEqual(tg_notify.go_duration(1.0), "1s")


class TestBoundaryValues(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name in ("a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg",
                     "f.jpg", "g.jpg", "h.jpg", "i.jpg", "j.jpg",
                     "k.jpg"):
            open(os.path.join(self.tmp.name, name), "wb").write(b"x")

    def _path(self, name):
        return os.path.join(self.tmp.name, name)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_message_exactly_4096(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "-m", "x" * 4096])
        self.assertIsNone(err)
        self.assertEqual(json.loads(stdout.getvalue())["text_length"],
                         4096)

    def test_message_4097_rejected(self):
        stderr, code = self._stderr_of(["--dry-run", "-m", "x" * 4097])
        self.assertEqual(code, 1)
        self.assertIn("message must be 1-4096 characters (4097 given)",
                      stderr)

    def test_caption_exactly_1024(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "-f", self._path("a.jpg"),
                 "-c", "x" * 1024])
        self.assertIsNone(err)
        self.assertEqual(json.loads(stdout.getvalue())
                         ["caption_length"], 1024)

    def test_caption_1025_rejected(self):
        stderr, code = self._stderr_of(
            ["-f", self._path("a.jpg"), "-c", "x" * 1025])
        self.assertEqual(code, 1)
        self.assertIn("caption too long (1025 chars, max 1024)", stderr)

    def test_album_exactly_two_ok(self):
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=[1, 2]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--album", self._path("a.jpg"), self._path("b.jpg")])
        self.assertIsNone(err)

    def test_album_exactly_ten_ok(self):
        items = [self._path(n) for n in
                 ("a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg",
                  "f.jpg", "g.jpg", "h.jpg", "i.jpg", "j.jpg")]
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=list(range(10))):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--album"] + items)
        self.assertIsNone(err)

    def test_album_eleven_rejected(self):
        items = [self._path(n) for n in
                 ("a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg",
                  "f.jpg", "g.jpg", "h.jpg", "i.jpg", "j.jpg",
                  "k.jpg")]
        stderr, code = self._stderr_of(["--album"] + items)
        self.assertEqual(code, 1)
        self.assertIn("album must contain 2-10 items (11 given)", stderr)

    def test_album_url_exactly_two(self):
        with mock.patch.object(tg_notify, "send_album_url_request",
                               return_value=[1, 2]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--album", "https://x/a.jpg", "https://x/b.jpg"])
        self.assertIsNone(err)

    def test_chat_id_negative_passthrough(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t",
                "TELEGRAM_CHAT_ID": "-1001234567890"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--dry-run", "--json", "hi"])
        self.assertIsNone(err)
        self.assertEqual(
            json.loads(stdout.getvalue())["chat_id"], "-1001234567890")

    def test_chat_id_username_style_passthrough(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t",
                "TELEGRAM_CHAT_ID": "@channelname"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--dry-run", "--json", "hi"])
        self.assertIsNone(err)
        self.assertEqual(
            json.loads(stdout.getvalue())["chat_id"], "@channelname")

    def test_reply_to_large_value_ok(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["-r", "2147483647", "--dry-run", "--json", "hi"])
        self.assertIsNone(err)
        self.assertEqual(json.loads(stdout.getvalue())
                         ["reply_to_message_id"], 2147483647)

    def test_reply_to_zero_no_conflict_in_whoami(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "M",
                                             "username": "m"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--whoami", "-r", "0"])
        self.assertIsNone(err)

    def test_zero_offset_no_mode_error(self):
        opts = tg_notify.Options()
        tg_notify.offset_mode_check(opts)

class TestBoolEqualsValues(unittest.TestCase):
    """Boolean flags accept Go's bool parse values via =value form."""

    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _run_json(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(args)
        return err, stdout.getvalue()

    def test_json_equals_zero_disables(self):
        err, out = self._run_json(["-j=0", "--dry-run", "hi"])
        self.assertIsNone(err)
        self.assertNotIn("{", out)

    def test_json_equals_one_enables(self):
        err, out = self._run_json(["-j=1", "--dry-run", "hi"])
        self.assertIsNone(err)
        self.assertIn("sendMessage", out)

    def test_json_equals_true_variants(self):
        for value in ("true", "True", "TRUE", "t", "T", "1"):
            err, out = self._run_json(
                [f"-j={value}", "--dry-run", "hi"])
            self.assertIsNone(err, value)
            self.assertTrue(out.startswith("{"), value)

    def test_json_equals_false_variants(self):
        for value in ("false", "False", "FALSE", "f", "F", "0"):
            err, out = self._run_json(
                [f"-j={value}", "--dry-run", "hi"])
            self.assertIsNone(err, value)
            self.assertFalse(out.startswith("{"), value)

    def test_dry_run_equals_false_still_sends_blocked(self):
        with mock.patch.object(tg_notify, "send_message_request",
                               return_value=9) as send:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["-D=false", "hi"])
        self.assertIsNone(err)
        self.assertEqual(send.call_count, 1)

    def test_invalid_bool_value_message(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(["-j=maybe", "--dry-run", "hi"])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(
            stderr.getvalue(),
            'Failed: invalid boolean value "maybe" for -j: '
            'parse error\n')


class TestSeparator(unittest.TestCase):
    """The bare -- token ends flag processing."""

    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def test_tokens_after_separator_are_positional(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(
                    ["--dry-run", "--", "--json", "-m", "hi"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("quote multi-word messages", stderr.getvalue())

    def test_separator_only_is_usage(self):
        fake_stdin = io.StringIO("")
        stderr = io.StringIO()
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin), \
                mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=True), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(["--"])
        self.assertEqual(caught.exception.code, 1)
        self.assertTrue(stderr.getvalue().startswith("usage:"))

    def test_separator_preserves_flag_value(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["-m", "hello", "--dry-run"])
        self.assertIsNone(err)
        self.assertIn("(5 chars)", stdout.getvalue())


class TestStdinEdges(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _run(self, text, args):
        fake_stdin = io.StringIO(text)
        stdout = io.StringIO()
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin), \
                mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=False), \
                contextlib.redirect_stdout(stdout):
            err = tg_notify.run(args)
        return err, stdout.getvalue()

    def test_stdin_multiline(self):
        err, out = self._run("line1\nline2\nline3", ["--dry-run", "--json"])
        self.assertIsNone(err)
        self.assertEqual(json.loads(out)["text_length"], 17)

    def test_stdin_only_whitespace_trimmed(self):
        fake_stdin = io.StringIO("   \n")
        stderr = io.StringIO()
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin), \
                mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=False), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(["--dry-run"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("message must be 1-4096 characters (0 given)",
                      stderr.getvalue())

    def test_stdin_no_trim_keeps_internal_newlines(self):
        err, out = self._run("a\nb", ["--no-trim", "--dry-run", "--json"])
        self.assertIsNone(err)
        self.assertEqual(json.loads(out)["text_length"], 3)

    def test_stdin_unicode_message(self):
        err, out = self._run("\u4f60\u597d\u4e16\u754c",
                             ["--dry-run", "--json"])
        self.assertIsNone(err)
        self.assertEqual(json.loads(out)["text_length"], 4)

    def test_explicit_message_never_reads_stdin(self):
        fake_stdin = io.StringIO("from-stdin")
        stdout = io.StringIO()
        with mock.patch.object(tg_notify.sys, "stdin", fake_stdin), \
                mock.patch.object(tg_notify, "stdin_is_char_device",
                                  return_value=False), \
                contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["-m", "explicit", "--dry-run", "--json"])
        self.assertIsNone(err)
        self.assertEqual(fake_stdin.tell(), 0)
        self.assertEqual(json.loads(stdout.getvalue())["text_length"], 8)


class TestFileModeEdges(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _path(self, name):
        return os.path.join(self.tmp.name, name)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_url_type_never_autodetected(self):
        for url, want in (("https://x/photo.jpg", "document"),
                          ("https://x/movie.mp4", "document"),
                          ("https://x/noext", "document")):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--dry-run", "--json", "--url", url])
            self.assertIsNone(err, url)
            self.assertEqual(json.loads(stdout.getvalue())["type"], want)

    def test_empty_caption_flag_no_conflict(self):
        open(self._path("a.jpg"), "wb").write(b"x")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "-f", self._path("a.jpg"),
                 "-c", ""])
        self.assertIsNone(err)
        self.assertEqual(
            json.loads(stdout.getvalue())["caption_length"], 0)

    def test_directory_not_a_file(self):
        stderr, code = self._stderr_of(["-f", self.tmp.name])
        self.assertEqual(code, 1)
        self.assertIn("file not found", stderr)

    def test_all_valid_types_accepted(self):
        for file_type in tg_notify.VALID_FILE_TYPES:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--dry-run", "--json", "-f", "x.png",
                     "--type", file_type])
            self.assertIsNone(err, file_type)
            self.assertEqual(json.loads(stdout.getvalue())["type"],
                             file_type)

    def test_sticker_endpoint_mapping(self):
        self.assertEqual(tg_notify.ENDPOINT_BY_TYPE["sticker"],
                         "sendSticker")
        self.assertEqual(tg_notify.ENDPOINT_BY_TYPE["animation"],
                         "sendAnimation")

    def test_mime_fallback_without_extension(self):
        self.assertEqual(tg_notify.detect_type("noextension"), "document")

    def test_uppercase_extension_detected(self):
        self.assertEqual(tg_notify.detect_type("PHOTO.JPG"), "photo")

    def test_caption_with_newline_multiline(self):
        open(self._path("a.jpg"), "wb").write(b"x")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "--json", "-f", self._path("a.jpg"),
                 "-c", "line1\nline2"])
        self.assertIsNone(err)
        self.assertEqual(
            json.loads(stdout.getvalue())["caption_length"], 11)

    def test_file_id_empty_type_rejected(self):
        stderr, code = self._stderr_of(["--file-id", "abc", "--type", ""])
        self.assertEqual(code, 1)
        self.assertIn("--file-id requires --type", stderr)

    def test_all_three_sources_rejected(self):
        stderr, code = self._stderr_of(
            ["-f", "a.jpg", "--url", "https://x/y", "--file-id", "abc"])
        self.assertEqual(code, 1)
        self.assertIn("not multiple", stderr)

    def test_file_with_offset_zero_ok(self):
        open(self._path("a.jpg"), "wb").write(b"x")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--dry-run", "-f", self._path("a.jpg"), "--offset", "0"])
        self.assertIsNone(err)

    def test_file_with_offset_nonzero_mode_error(self):
        stderr, code = self._stderr_of(
            ["-f", "a.jpg", "--offset", "5", "--dry-run"])
        self.assertEqual(code, 1)
        self.assertIn("--offset is only valid with --discover-chat-id",
                      stderr)


class TestAlbumEdges(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name in ("a.jpg", "b.jpg", "pre.txt", "v.mp4"):
            open(os.path.join(self.tmp.name, name), "wb").write(b"x")

    def _path(self, name):
        return os.path.join(self.tmp.name, name)

    def test_album_needs_argument(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(["--album"])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(
            stderr.getvalue(), "Failed: flag needs an argument: -album\n")

    def test_album_items_in_source_order(self):
        items = [self._path("v.mp4"), self._path("a.jpg")]
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=[1, 2]) as send:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--album"] + items)
        self.assertIsNone(err)
        self.assertEqual(send.call_args.args[2], items)

    def test_album_trailing_and_flag_items_combined(self):
        flag_item = self._path("a.jpg")
        trailing = [self._path("b.jpg"), self._path("v.mp4")]
        with mock.patch.object(tg_notify, "send_album_upload_request",
                               return_value=[1, 2, 3]) as send:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--album", flag_item] + trailing)
        self.assertIsNone(err)
        self.assertEqual(send.call_args.args[2], [flag_item] + trailing)

    def test_album_positionals_before_flag_are_message_mode(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(
                    [self._path("pre.txt"), self._path("a.jpg"),
                     "--dry-run"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("quote multi-word messages", stderr.getvalue())

    def test_album_video_kept_photo_other_coerced(self):
        self.assertEqual(tg_notify.album_item_type(self._path("v.mp4")),
                         "video")
        self.assertEqual(tg_notify.album_item_type(self._path("a.jpg")),
                         "photo")
        self.assertEqual(tg_notify.album_item_type(self._path("pre.txt")),
                         "photo")

    def test_album_empty_caption_no_first_item_key(self):
        media = tg_notify.album_media_items(
            ["a.jpg", "b.jpg"], ["photo", "photo"], "", "", 0, False,
            url_mode=False)
        self.assertNotIn("caption", media[0])
        self.assertNotIn("parse_mode", media[0])

    def test_album_url_media_types(self):
        media = tg_notify.album_media_items(
            ["https://x/a.png", "https://x/b.mkv"], ["photo", "video"],
            "", "", 0, False, url_mode=True)
        self.assertEqual(media[0]["type"], "photo")
        self.assertEqual(media[1]["type"], "video")

    def test_album_with_file_id_rejected(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(
                    ["--file-id", "abc", "--type", "photo", "--album",
                     self._path("a.jpg")])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("--album cannot be combined", stderr.getvalue())

    def test_album_dry_run_shows_caption_suffix(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--album", "https://x/a.jpg", "https://x/b.jpg",
                 "-c", "cap", "--dry-run"])
        self.assertIsNone(err)
        self.assertIn("caption (3 chars)", stdout.getvalue())

    def test_album_dry_run_json_with_options(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(
                ["--album", "https://x/a.jpg", "https://x/b.jpg",
                 "-c", "cap", "--reply-to", "3", "--silent",
                 "--parse-mode", "HTML", "--dry-run", "--json"])
        self.assertIsNone(err)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["caption_length"], 3)
        self.assertEqual(data["reply_to_message_id"], 3)
        self.assertTrue(data["disable_notification"])
        self.assertEqual(data["parse_mode"], "HTML")

class TestModeDispatchOrder(unittest.TestCase):
    """Bounds and mode-conflict checks fire before network and creds."""

    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_bounds_before_whoami_conflict(self):
        stderr, _ = self._stderr_of(["-R", "-1", "--whoami", "-m", "hi"])
        self.assertIn("--retries must be >= 0", stderr)

    def test_bounds_before_discover_conflict(self):
        stderr, _ = self._stderr_of(["-r", "-1", "-d", "-m", "hi"])
        self.assertIn("--reply-to must be >= 0", stderr)

    def test_whoami_conflict_without_token(self):
        stderr, _ = self._stderr_of(["--whoami", "-m", "hi"])
        self.assertIn("--whoami cannot be combined", stderr)

    def test_discover_conflict_without_token(self):
        stderr, _ = self._stderr_of(["-d", "-m", "hi"])
        self.assertIn("--discover-chat-id cannot be combined", stderr)

    def test_whoami_then_discover_runs_whoami(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "M",
                                             "username": "m"}):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-w", "-d"])
        self.assertIsNone(err)
        self.assertIn("@m", stdout.getvalue())

    def test_discover_then_whoami_runs_whoami(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "M",
                                             "username": "m"}):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-d", "-w"])
        self.assertIsNone(err)
        self.assertIn("@m", stdout.getvalue())

    def test_file_branch_before_message(self):
        with mock.patch.object(tg_notify, "run_file",
                               return_value=None) as rf:
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t",
                    "TELEGRAM_CHAT_ID": "1"}):
                err = tg_notify.run(["-f", "a.jpg", "stray-text"])
        self.assertIsNone(err)
        rf.assert_called_once()

    def test_album_branch_before_file(self):
        with mock.patch.object(tg_notify, "run_album",
                               return_value=None) as ra:
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t",
                    "TELEGRAM_CHAT_ID": "1"}):
                err = tg_notify.run(["--album", "a.jpg", "b.jpg"])
        self.assertIsNone(err)
        ra.assert_called_once()


class TestWhoamiEdges(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def test_whoami_ignores_silent_and_offset(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "M",
                                             "username": "m"}):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-w", "-S", "-o", "3"])
        self.assertIsNone(err)

    def test_whoami_json_field_order(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value={"id": 7, "is_bot": True,
                                             "first_name": "Mock",
                                             "username": "mockbot"}):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["--whoami", "--json"])
        self.assertIsNone(err)
        line = stdout.getvalue()
        self.assertLess(line.index('"ok"'), line.index('"id"'))
        self.assertLess(line.index('"id"'), line.index('"is_bot"'))

    def test_whoami_network_error(self):
        with mock.patch.object(tg_notify.Client, "call",
                               side_effect=RuntimeError(
                                   'Get "http://x/bot1/x": timeout')):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as caught:
                        tg_notify.main(["--whoami", "-n"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("Failed:", stderr.getvalue())

    def test_whoami_empty_positional_conflict(self):
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t"}):
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as caught:
                    tg_notify.main(["--whoami", "stray"])
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("--whoami cannot be combined", stderr.getvalue())


class TestDiscoverEdges(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_offset_flag_requires_discover(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            stderr, _ = self._stderr_of(["--offset", "5", "-m", "hi"])
        self.assertIn("--offset is only valid with --discover-chat-id",
                      stderr)

    def test_offset_negative_with_discover(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t"}):
            stderr, _ = self._stderr_of(["-d", "--offset", "-5"])
        self.assertIn("--offset must be >= 0", stderr)

    def test_discover_callback_query_unsupported(self):
        updates = [{"update_id": 9, "callback_query":
                    {"message": {"chat": {"id": -999}}}}]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stderr, code = self._stderr_of(["-d"])
        self.assertEqual(code, 1)
        self.assertIn("no message found in latest update", stderr)

    def test_discover_update_without_chat(self):
        updates = [{"update_id": 9, "message": {}}]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stderr, code = self._stderr_of(["-d"])
        self.assertEqual(code, 1)
        self.assertIn("no message found in latest update", stderr)

    def test_discover_takes_last_update(self):
        updates = [
            {"update_id": 1, "message": {"chat": {"id": 111}}},
            {"update_id": 2, "message": {"chat": {"id": 222}}},
        ]
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=updates):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["-d"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue().strip(), "222")

    def test_discover_json_error_still_failed(self):
        with mock.patch.object(tg_notify.Client, "call",
                               return_value=[]):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "t"}):
                stderr, code = self._stderr_of(["-d", "--json"])
        self.assertEqual(code, 1)
        self.assertIn("Failed:", stderr)


class TestRetryEdges(unittest.TestCase):
    def _opts(self, retries, base_wait, no_retry=False):
        opts = tg_notify.Options()
        opts.retries = retries
        opts.base_wait = base_wait
        opts.no_retry = no_retry
        return opts

    def test_jitter_bounds(self):
        def send():
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        sleeps = []
        with mock.patch.object(tg_notify.time, "sleep",
                               side_effect=sleeps.append), \
                mock.patch.object(tg_notify.random, "uniform",
                                  return_value=0.25):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(
                    send, self._opts(1, 2.0))
        self.assertAlmostEqual(sleeps[0], 2.5, places=6)

    def test_jitter_lower_bound(self):
        def send():
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        sleeps = []
        with mock.patch.object(tg_notify.time, "sleep",
                               side_effect=sleeps.append), \
                mock.patch.object(tg_notify.random, "uniform",
                                  return_value=-0.25):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(
                    send, self._opts(1, 2.0))
        self.assertAlmostEqual(sleeps[0], 1.5, places=6)

    def test_retry_line_format(self):
        def send():
            raise RuntimeError('Post "http://x/bot1/x": conn refused')

        stderr = io.StringIO()
        with mock.patch.object(tg_notify.time, "sleep"), \
                mock.patch.object(tg_notify.random, "uniform",
                                  return_value=0.0), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(
                    send, self._opts(1, 2.0))
        self.assertIn(
            'Transient error (Post "http://x/bot1/x": conn refused). '
            'Retry 1/1 in 2s...', stderr.getvalue())

    def test_success_after_transient(self):
        calls = []

        def send():
            calls.append(1)
            if len(calls) < 3:
                raise RuntimeError('Post "http://x/bot1/x": timeout')
            return 77

        with mock.patch.object(tg_notify.time, "sleep"):
            self.assertEqual(
                tg_notify.execute_with_retries(send, self._opts(5, 1.0)),
                77)
        self.assertEqual(len(calls), 3)

    def test_429_retry_after_default(self):
        calls = []

        def send():
            calls.append(1)
            if len(calls) == 1:
                raise tg_notify.ApiError(429, "Too Many Requests", -3)
            return 8

        sleeps = []
        with mock.patch.object(tg_notify.time, "sleep",
                               side_effect=sleeps.append):
            self.assertEqual(
                tg_notify.execute_with_retries(
                    send, self._opts(0, 2.0)), 8)
        self.assertEqual(sleeps, [5])

    def test_http_404_not_transient(self):
        self.assertFalse(
            tg_notify.is_transient(tg_notify.ApiError(404, "Not Found")))

    def test_http_500_transient(self):
        self.assertTrue(
            tg_notify.is_transient(tg_notify.ApiError(500, "Server")))

    def test_runtime_error_transient(self):
        self.assertTrue(tg_notify.is_transient(RuntimeError("net")))

    def test_exact_retries_count(self):
        calls = []

        def send():
            calls.append(1)
            raise RuntimeError('Post "http://x/bot1/x": timeout')

        with mock.patch.object(tg_notify.time, "sleep"), \
                mock.patch.object(tg_notify.random, "uniform",
                                  return_value=0.0):
            with self.assertRaises(RuntimeError):
                tg_notify.execute_with_retries(
                    send, self._opts(60, 2.0))
        self.assertEqual(len(calls), 61)


class TestProxyEdges(unittest.TestCase):
    def setUp(self):
        env_patch = mock.patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "42"},
            clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def _stderr_of(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                tg_notify.main(args)
        return stderr.getvalue(), caught.exception.code

    def test_flag_wins_over_env(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_PROXY": "garbage-env"}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(
                    ["--proxy", "http://good:8080", "--dry-run", "hi"])
        self.assertIsNone(err)

    def test_proxy_only_scheme_rejected(self):
        stderr, _ = self._stderr_of(
            ["--proxy", "http://", "--dry-run", "hi"])
        self.assertIn("invalid proxy URL", stderr)

    def test_empty_proxy_env_ignored(self):
        with mock.patch.dict(os.environ, {"TELEGRAM_PROXY": ""}):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                err = tg_notify.run(["--dry-run", "hi"])
        self.assertIsNone(err)


class TestDotEnvEdges(unittest.TestCase):
    def test_env_file_comments_and_whitespace(self):
        content = "  # leading comment\n\n  TELEGRAM_BOT_TOKEN =  tok1  \n"
        with mock.patch("builtins.open",
                        unittest.mock.mock_open(read_data=content)):
            with mock.patch.dict(os.environ, {}, clear=True):
                tg_notify.load_dotenv()
                self.assertEqual(os.environ.get("TELEGRAM_BOT_TOKEN"),
                                 "tok1")

    def test_env_file_without_equals_skipped(self):
        with mock.patch("builtins.open",
                        unittest.mock.mock_open(
                            read_data="JUSTAKEY\nTELEGRAM_CHAT_ID=5\n")):
            with mock.patch.dict(os.environ, {}, clear=True):
                tg_notify.load_dotenv()
                self.assertEqual(os.environ.get("TELEGRAM_CHAT_ID"), "5")
                self.assertNotIn("JUSTAKEY", os.environ)

    def test_env_file_other_keys_ignored(self):
        with mock.patch("builtins.open",
                        unittest.mock.mock_open(
                            read_data="OTHER=1\nTELEGRAM_PROXY=x\n")):
            with mock.patch.dict(os.environ, {}, clear=True):
                tg_notify.load_dotenv()
                self.assertNotIn("OTHER", os.environ)
                self.assertNotIn("TELEGRAM_PROXY", os.environ)

    def test_env_file_chat_only_token(self):
        with mock.patch("builtins.open",
                        unittest.mock.mock_open(
                            read_data="TELEGRAM_CHAT_ID=9\n")):
            with mock.patch.dict(os.environ, {
                    "TELEGRAM_BOT_TOKEN": "real"}, clear=True):
                tg_notify.load_dotenv()
                self.assertEqual(os.environ["TELEGRAM_CHAT_ID"], "9")
                self.assertEqual(os.environ["TELEGRAM_BOT_TOKEN"], "real")


class TestScrubAndOutputEdges(unittest.TestCase):
    def test_scrub_multiple_tokens(self):
        text = ('Post "https://a/botAAA/x": fail; '
                'Get "https://b/botBBB/y": fail')
        scrubbed = tg_notify.scrub_secrets(text)
        self.assertNotIn("botAAA", scrubbed)
        self.assertNotIn("botBBB", scrubbed)
        self.assertEqual(scrubbed.count("<token>"), 2)

    def test_go_quote_escapes(self):
        self.assertEqual(tg_notify.go_quote('say "hi"'), '"say \\"hi\\""')
        self.assertEqual(tg_notify.go_quote("back\\slash"),
                         '"back\\\\slash"')

    def test_compact_json_no_spaces(self):
        out = tg_notify.compact_json({"a": 1, "b": [1, 2]})
        self.assertEqual(out, '{"a":1,"b":[1,2]}')

    def test_compact_json_unicode_passthrough(self):
        out = tg_notify.compact_json({"t": "\u4f60"})
        self.assertIn("\u4f60", out)

    def test_json_success_message_no_trailing_garbage(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            with mock.patch.object(tg_notify, "send_message_request",
                                   return_value=42):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    err = tg_notify.run(["--json", "hi"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue(),
                         '{"ok":true,"message_id":42}\n')

    def test_network_error_token_scrubbed(self):
        with mock.patch.dict(os.environ, {
                "TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "1"}):
            with mock.patch.object(tg_notify, "send_message_request",
                                   side_effect=RuntimeError(
                                       'Post "https://api.telegram.org'
                                       '/botSECRET123/sendMessage": '
                                       "timeout")):
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as caught:
                        tg_notify.main(["hi"])
        self.assertEqual(caught.exception.code, 1)
        self.assertNotIn("SECRET123", stderr.getvalue())
        self.assertIn("/bot<token>/", stderr.getvalue())


class TestVersionEdges(unittest.TestCase):
    def test_version_beats_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["--version", "--help"])
        self.assertIsNone(err)
        self.assertEqual(stdout.getvalue().strip(),
                         tg_notify.read_skill_version())

    def test_version_beats_bounds(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            err = tg_notify.run(["-v", "--retries", "-1"])
        self.assertIsNone(err)

    def test_version_missing_skill_file(self):
        with mock.patch.object(tg_notify.os.path, "abspath",
                               return_value="/nonexistent/x/y.py"):
            self.assertEqual(tg_notify.read_skill_version(), "unknown")


import tg_constants


class TestConstantsLoader(unittest.TestCase):
    def test_load_limits_keys_and_types(self):
        limits = tg_constants.load_limits()
        for key in ("message_max_chars", "caption_max_chars",
                    "photo_upload_max_mb", "other_upload_max_mb",
                    "self_hosted_upload_max_mb", "backoff_cap_seconds",
                    "default_retries", "default_base_wait_seconds",
                    "album_min_items", "album_max_items",
                    "rate_limit_messages_per_second"):
            self.assertIn(key, limits)
            self.assertIsInstance(limits[key], (int, float))

    def test_load_filetypes_maps(self):
        ext_map, mime_map = tg_constants.load_filetypes()
        self.assertEqual(ext_map[".jpg"], "photo")
        self.assertEqual(ext_map[".opus"], "voice")
        self.assertEqual(mime_map["image/jpeg"], "photo")
        self.assertEqual(mime_map["video/x-ms-wmv"], "video")

    def test_dump_all_covers_both_sets(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = tg_constants.main(["--dump", "all"])
        self.assertEqual(rc, 0)
        out = json.loads(stdout.getvalue())
        self.assertIn("limits", out)
        self.assertIn("filetypes", out)
        self.assertIn("extensions", out["filetypes"])
        self.assertIn("mime", out["filetypes"])

    def test_missing_constant_file_exits(self):
        with mock.patch.object(tg_constants, "ASSETS_DIR", "/nonexistent"):
            with self.assertRaises(SystemExit):
                tg_constants.load_limits()


class TestDriftGuard(unittest.TestCase):
    """Module constants must equal the constant file values."""

    def test_char_limits_match(self):
        limits = tg_constants.load_limits()
        self.assertEqual(tg_notify.MAX_MESSAGE_CHARS,
                         int(limits["message_max_chars"]))
        self.assertEqual(tg_notify.MAX_CAPTION_CHARS,
                         int(limits["caption_max_chars"]))

    def test_upload_limits_match(self):
        limits = tg_constants.load_limits()
        self.assertEqual(
            tg_notify.MAX_PHOTO_UPLOAD,
            int(limits["photo_upload_max_mb"]) * 1024 * 1024)
        self.assertEqual(
            tg_notify.MAX_OTHER_UPLOADS,
            int(limits["other_upload_max_mb"]) * 1024 * 1024)
        self.assertEqual(
            tg_notify.MAX_SELF_HOSTED_UPLOAD,
            int(limits["self_hosted_upload_max_mb"]) * 1024 * 1024)

    def test_retry_defaults_match(self):
        limits = tg_constants.load_limits()
        self.assertEqual(tg_notify.DEFAULT_RETRIES,
                         int(limits["default_retries"]))
        self.assertEqual(tg_notify.DEFAULT_BASE_WAIT,
                         float(limits["default_base_wait_seconds"]))
        self.assertEqual(tg_notify.MAX_BACKOFF_SECONDS,
                         float(limits["backoff_cap_seconds"]))

    def test_album_bounds_match(self):
        limits = tg_constants.load_limits()
        self.assertEqual(tg_notify.ALBUM_MIN_ITEMS,
                         int(limits["album_min_items"]))
        self.assertEqual(tg_notify.ALBUM_MAX_ITEMS,
                         int(limits["album_max_items"]))

    def test_type_maps_match(self):
        ext_map, mime_map = tg_constants.load_filetypes()
        self.assertEqual(tg_notify.EXT_TO_TYPE, ext_map)
        self.assertEqual(tg_notify.MIME_TO_TYPE, mime_map)


if __name__ == "__main__":
    unittest.main()
