"""Tk window for the optional AI chat, styled like the settings dashboard."""
import threading
import tkinter as tk
from tkinter import messagebox

from core import ai_chat

BG, PANEL, FG, MUTED = "#1e1e1e", "#2d2d2d", "white", "#e1e4e8"


class ChatWindow:
    def __init__(self, root, directory, prompt_path, on_reply=None):
        self.root, self.directory = root, directory
        self.prompt = ai_chat.load_prompt(prompt_path)
        self.settings = ai_chat.load_settings(directory)
        self.history = []
        self.busy = False
        self.win = tk.Toplevel(root)
        self.win.title("Pulchra Comms")
        self.win.configure(bg=BG)
        self.win.geometry("440x560")
        self.win.minsize(380, 460)
        self._build()
        self._refresh_state()

    def _build(self):
        w = self.win
        top = tk.Frame(w, bg=BG)
        top.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(top, text="Comms (optional AI chat)", bg=BG, fg=FG,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self.status = tk.Label(top, text="", bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.status.pack(side="right")

        self.setup = tk.Frame(w, bg=BG)
        self.var_enabled = tk.BooleanVar(value=self.settings.enabled and self.settings.consent)
        tk.Checkbutton(self.setup, text="Enable AI chat (sends messages online)", variable=self.var_enabled,
                       bg=BG, fg=FG, selectcolor=PANEL, activebackground=BG, activeforeground=FG,
                       font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(2, 6))
        self.var_endpoint = tk.StringVar(value=self.settings.endpoint)
        self.var_model = tk.StringVar(value=self.settings.model)
        self.var_key = tk.StringVar(value=self.settings.api_key)
        for label, var, secret in (("Service address", self.var_endpoint, False),
                                   ("Model", self.var_model, False),
                                   ("Your API key", self.var_key, True)):
            tk.Label(self.setup, text=label, bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
            tk.Entry(self.setup, textvariable=var, show="*" if secret else "", bg=PANEL, fg=FG,
                     insertbackground=FG, bd=0, font=("Segoe UI", 9)).pack(fill="x", ipady=4, pady=(0, 6))
        tk.Button(self.setup, text="Save AI Settings", command=self.save_setup, bg=PANEL, fg=FG, bd=0,
                  pady=6, font=("Segoe UI", 9)).pack(fill="x")
        self.setup.pack(fill="x", padx=14, pady=4)

        self.log = tk.Text(w, bg=PANEL, fg=FG, bd=0, wrap="word", state="disabled", font=("Segoe UI", 9),
                           padx=8, pady=8)
        self.log.tag_configure("you", foreground="#9aa4b2")
        self.log.tag_configure("her", foreground=FG)
        self.log.pack(fill="both", expand=True, padx=14, pady=6)
        row = tk.Frame(w, bg=BG)
        row.pack(fill="x", padx=14, pady=(0, 12))
        self.entry = tk.Entry(row, bg=PANEL, fg=FG, insertbackground=FG, bd=0, font=("Segoe UI", 9))
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self.send())
        self.btn = tk.Button(row, text="Send", command=self.send, bg=PANEL, fg=FG, bd=0, padx=14,
                             font=("Segoe UI", 9))
        self.btn.pack(side="left", padx=(6, 0))

    def lift(self):
        self.win.lift()
        self.win.focus_force()

    def exists(self):
        return bool(self.win.winfo_exists())

    def _refresh_state(self):
        ready = self.settings.is_ready()
        self.status.config(text="online" if ready else "off")
        state = "normal" if ready else "disabled"
        self.entry.config(state=state)
        self.btn.config(state=state)
        if not ready:
            self._append("Pulchra", "Comms are off. Enable AI chat above and add your own key to talk.", "her")

    def _append(self, who, text, tag):
        self.log.config(state="normal")
        self.log.insert("end", who + ": ", tag)
        self.log.insert("end", text + "\n\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def save_setup(self):
        wants = self.var_enabled.get()
        if wants and not (self.settings.enabled and self.settings.consent):
            if not messagebox.askokcancel("Enable AI chat?", ai_chat.DISCLOSURE, parent=self.win):
                self.var_enabled.set(False)
                wants = False
        s = self.settings
        s.endpoint, s.model = self.var_endpoint.get().strip(), self.var_model.get().strip()
        s.api_key = self.var_key.get().strip()
        s.enabled = s.consent = wants
        problem = s.endpoint_problem()
        if wants and problem:
            messagebox.showerror("AI chat", problem, parent=self.win)
            s.enabled = s.consent = False
            self.var_enabled.set(False)
        ai_chat.save_settings(self.directory, s)
        self._refresh_state()

    def send(self):
        text = self.entry.get().strip()
        if not text or self.busy or not self.settings.is_ready():
            return
        self.entry.delete(0, "end")
        self._append("You", text, "you")
        self.busy = True
        self.btn.config(state="disabled")
        history = list(self.history)
        threading.Thread(target=self._worker, args=(text, history), daemon=True).start()

    def _worker(self, text, history):
        try:
            reply, error = ai_chat.send_message(self.settings, self.prompt, history, text), None
        except (ai_chat.AIChatError, ai_chat.AIChatDisabled) as exc:
            reply, error = None, str(exc)
        try:
            self.win.after(0, self._done, text, reply, error)
        except (tk.TclError, RuntimeError):
            pass

    def _done(self, text, reply, error):
        self.busy = False
        if error:
            self._append("Pulchra", error, "her")
        else:
            self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
            self._append("Pulchra", reply, "her")
        if self.exists():
            self.btn.config(state="normal" if self.settings.is_ready() else "disabled")
