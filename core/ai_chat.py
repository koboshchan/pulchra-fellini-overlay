"""Optional in-character AI chat. Everything here is OFF by default.

Nothing in this module touches the network until the user has explicitly
enabled the feature, accepted the data disclosure and supplied their own API
key. No API key is bundled with the application.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict

SETTINGS_FILE = "ai_chat.json"
KEY_ENV = "PULCHRA_AI_API_KEY"
DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"
MAX_HISTORY_TURNS = 12
MAX_REPLY_CHARS = 1200

DISCLOSURE = (
    "AI chat is optional and sends what you type in the chat window, plus "
    "Pulchra's character prompt and your recent chat turns, to the service "
    "address below using your own API key. Nothing else from your computer "
    "is sent, and nothing is sent until you press Send.\n\n"
    "Your key is stored in plain text in ai_chat.json inside Pulchra's "
    "settings folder (readable only by your account where the OS supports it). "
    "You can instead set the PULCHRA_AI_API_KEY environment variable and leave "
    "the key box empty.")


class AIChatDisabled(Exception):
    """Raised instead of making any request when chat is not fully opted in."""


class AIChatError(Exception):
    pass


@dataclass
class AISettings:
    enabled: bool = False
    consent: bool = False
    endpoint: str = DEFAULT_ENDPOINT
    model: str = DEFAULT_MODEL
    api_key: str = ""

    def effective_key(self):
        return (os.environ.get(KEY_ENV) or self.api_key or "").strip()

    def endpoint_problem(self):
        parts = urllib.parse.urlparse(self.endpoint.strip())
        if parts.scheme == "https" and parts.netloc:
            return None
        if parts.scheme == "http" and parts.hostname in ("localhost", "127.0.0.1", "::1"):
            return None
        return "Service address must be https (or http on this computer)."

    def is_ready(self):
        return (self.enabled and self.consent and bool(self.effective_key())
                and bool(self.model.strip()) and self.endpoint_problem() is None)

    def masked_key(self):
        key = self.api_key
        return "" if not key else "*" * max(len(key) - 4, 0) + key[-4:]


def load_settings(directory):
    path = os.path.join(directory, SETTINGS_FILE)
    settings = AISettings()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return settings
    if not isinstance(data, dict):
        return settings
    for name in ("endpoint", "model", "api_key"):
        if isinstance(data.get(name), str):
            setattr(settings, name, data[name])
    # Booleans must be real booleans so a stray string can never opt in.
    settings.enabled = data.get("enabled") is True
    settings.consent = data.get("consent") is True
    return settings


def save_settings(directory, settings):
    path = os.path.join(directory, SETTINGS_FILE)
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(asdict(settings), handle, indent=4)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, path)


def load_prompt(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return "You are Pulchra Fellini, a sharp-eyed Feline Thiren mercenary. Stay in character."


def styled_reply_parts(text):
    """Split action spans without removing asterisks or interpreting markup.

    Upstream 6.0.0a distinguishes *actions* from speech in its terminal.
    Native Text tags do the same safely, including an unfinished action span.
    """
    action = False
    chunk = ""
    for char in text:
        if char == "*":
            if action:
                chunk += char
                yield chunk, "action"
                chunk = ""
                action = False
            else:
                if chunk:
                    yield chunk, "her"
                chunk = char
                action = True
        else:
            chunk += char
    if chunk:
        yield chunk, "action" if action else "her"


def build_messages(prompt, history, user_text):
    turns = [m for m in history if m.get("role") in ("user", "assistant")]
    turns = turns[-MAX_HISTORY_TURNS * 2:]
    return ([{"role": "system", "content": prompt}] + turns
            + [{"role": "user", "content": user_text}])


def send_message(settings, prompt, history, user_text, opener=urllib.request.urlopen, timeout=45):
    """Return Pulchra's reply. Raises AIChatDisabled before any network use."""
    if not settings.is_ready():
        raise AIChatDisabled("AI chat is not enabled.")
    user_text = user_text.strip()
    if not user_text:
        raise AIChatError("Nothing to send.")
    body = json.dumps({"model": settings.model.strip(),
                       "messages": build_messages(prompt, history, user_text),
                       "max_tokens": 300}).encode("utf-8")
    request = urllib.request.Request(
        settings.endpoint.strip(), data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + settings.effective_key()})
    try:
        with opener(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        reply = payload["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as error:
        raise AIChatError("Comms failed (HTTP %s)." % error.code) from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise AIChatError("Comms failed: could not reach the service.") from None
    except (ValueError, KeyError, IndexError, TypeError):
        raise AIChatError("Comms failed: unexpected reply.") from None
    if not isinstance(reply, str) or not reply.strip():
        raise AIChatError("Comms failed: empty reply.")
    return reply.strip()[:MAX_REPLY_CHARS]
