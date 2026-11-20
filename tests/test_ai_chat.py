"""Optional AI chat: off by default, no keys bundled, no network before opt-in."""
import io
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import unittest
from unittest.mock import Mock, patch

from core import ai_chat

ROOT = Path(__file__).resolve().parent.parent


def ready(**kw):
    return ai_chat.AISettings(enabled=True, consent=True, api_key="sk-test-1234", **kw)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def reply(text):
    return FakeResponse(json.dumps({"choices": [{"message": {"content": text}}]}).encode())


class AIChatTests(unittest.TestCase):
    def test_action_styling_preserves_all_text(self):
        for text in ("hello", "*ears flick* Pay up.", "one *two* three *four*", "*unfinished", "**", "<script>\\nhello"):
            parts = list(ai_chat.styled_reply_parts(text))
            self.assertEqual("".join(t for t, _ in parts), text)
        self.assertEqual(list(ai_chat.styled_reply_parts("*ears flick* Pay up.")),
                         [("*ears flick*", "action"), (" Pay up.", "her")])
        self.assertEqual(list(ai_chat.styled_reply_parts("")), [])

    def test_chat_relay_style_is_native_not_ansi_or_encryption_claim(self):
        source = (ROOT / "core" / "chat_window.py").read_text()
        self.assertIn('tag_configure("action"', source)
        self.assertIn("styled_reply_parts(text)", source)
        self.assertIn("BLAZEWOOD RELAY", source)
        self.assertNotIn("ENCRYPTED", source)

    def test_defaults_are_disabled(self):
        s = ai_chat.AISettings()
        self.assertFalse(s.enabled or s.consent or s.is_ready())
        self.assertEqual(s.api_key, "")

    def test_missing_file_and_garbage_stay_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(ai_chat.load_settings(d).enabled)
            for junk in ("not json", "[]", '{"enabled": "true", "consent": 1}'):
                Path(d, ai_chat.SETTINGS_FILE).write_text(junk)
                self.assertFalse(ai_chat.load_settings(d).is_ready(), junk)

    def test_needs_enable_consent_and_key(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ai_chat.KEY_ENV, None)
            self.assertFalse(ai_chat.AISettings(enabled=True, consent=True).is_ready())
            self.assertFalse(ai_chat.AISettings(enabled=True, api_key="k").is_ready())
            self.assertFalse(ai_chat.AISettings(consent=True, api_key="k").is_ready())
            self.assertTrue(ready().is_ready())

    def test_environment_key_supplies_key(self):
        with patch.dict(os.environ, {ai_chat.KEY_ENV: "env-key"}):
            s = ai_chat.AISettings(enabled=True, consent=True)
            self.assertTrue(s.is_ready())
            self.assertEqual(s.effective_key(), "env-key")

    def test_settings_roundtrip_and_private_file(self):
        with tempfile.TemporaryDirectory() as d:
            ai_chat.save_settings(d, ready(model="m"))
            loaded = ai_chat.load_settings(d)
            self.assertTrue(loaded.enabled and loaded.consent)
            self.assertEqual((loaded.model, loaded.api_key), ("m", "sk-test-1234"))
            if os.name == "posix":
                mode = stat.S_IMODE(os.stat(Path(d, ai_chat.SETTINGS_FILE)).st_mode)
                self.assertEqual(mode, 0o600)
            self.assertEqual(loaded.masked_key(), "********1234")

    def test_disabled_never_touches_network(self):
        opener = Mock()
        for s in (ai_chat.AISettings(), ai_chat.AISettings(enabled=True, api_key="k"),
                  ai_chat.AISettings(consent=True, api_key="k")):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop(ai_chat.KEY_ENV, None)
                with self.assertRaises(ai_chat.AIChatDisabled):
                    ai_chat.send_message(s, "p", [], "hi", opener=opener)
        opener.assert_not_called()

    def test_endpoint_must_be_https_or_local(self):
        for url, ok in (("https://x.example/v1", True), ("http://localhost:11434/v1", True),
                        ("http://evil.example/v1", False), ("ftp://x", False), ("", False)):
            s = ready(endpoint=url)
            self.assertEqual(s.is_ready(), ok, url)

    def test_send_builds_request_and_returns_reply(self):
        seen = {}

        def opener(request, timeout):
            seen["req"], seen["timeout"] = request, timeout
            return reply("  *ears flick* Pay up.  ")

        history = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
        out = ai_chat.send_message(ready(), "PROMPT", history, "hello", opener=opener)
        self.assertEqual(out, "*ears flick* Pay up.")
        body = json.loads(seen["req"].data)
        self.assertEqual(body["messages"][0], {"role": "system", "content": "PROMPT"})
        self.assertEqual(body["messages"][-1], {"role": "user", "content": "hello"})
        self.assertEqual(seen["req"].get_header("Authorization"), "Bearer sk-test-1234")

    def test_history_is_capped(self):
        history = [{"role": "user" if i % 2 == 0 else "assistant", "content": str(i)} for i in range(100)]
        msgs = ai_chat.build_messages("p", history, "now")
        self.assertEqual(len(msgs), 1 + ai_chat.MAX_HISTORY_TURNS * 2 + 1)

    def test_errors_do_not_leak_key(self):
        import urllib.error

        def boom(request, timeout):
            raise urllib.error.HTTPError("u", 401, "no", {}, io.BytesIO())

        with self.assertRaises(ai_chat.AIChatError) as cm:
            ai_chat.send_message(ready(), "p", [], "hi", opener=boom)
        self.assertNotIn("sk-test", str(cm.exception))
        bad = lambda request, timeout: FakeResponse(b"{}")
        with self.assertRaises(ai_chat.AIChatError):
            ai_chat.send_message(ready(), "p", [], "hi", opener=bad)

    def test_no_secrets_bundled(self):
        pattern = re.compile(r"(sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{20,}|gsk_[A-Za-z0-9]{20,})")
        for path in list((ROOT / "core").glob("*.py")) + list((ROOT / "assets").glob("*.txt")) \
                + list((ROOT / "assets").glob("*.json")):
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8", errors="ignore")), path.name)
        self.assertFalse((ROOT / "assets" / "pulchra_chat.exe").exists())

    def test_prompt_asset_loads(self):
        text = ai_chat.load_prompt(str(ROOT / "assets" / "pulchra_prompt.txt"))
        self.assertIn("Pulchra Fellini", text)

    def test_companion_chat_is_optional_and_lazy(self):
        from core import companion
        src = Path(companion.__file__).read_text(encoding="utf-8")
        self.assertIn("def open_ai_chat", src)
        self.assertNotIn("ChatWindow(", src.split("def open_ai_chat")[0])
        # Old fork features remain wired in.
        for needle in ("toggle_gravity_flip", "_spawn_floating_heart", "Flip Gravity"):
            self.assertIn(needle, src)


if __name__ == "__main__":
    unittest.main()
