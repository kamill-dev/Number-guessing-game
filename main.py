
import json
import os
import random
import time
import threading
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Cross-platform beep
try:
    import winsound
    def beep():
        winsound.Beep(1000, 120)
except Exception:
    def beep():
        try:
            # Tk bell as fallback
            root = tk._default_root
            if root:
                root.bell()
        except Exception:
            pass

SCORES_FILE = Path("scores.json")

DEFAULT_SCORES = {"Easy": None, "Medium": None, "Hard": None, "Extreme": None}

def load_scores():
    if SCORES_FILE.exists():
        try:
            with open(SCORES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SCORES.copy()
    return DEFAULT_SCORES.copy()

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

class NumberGuessingGUI:
    def __init__(self, master):
        self.master = master
        master.title("Number Guessing Game")
        master.resizable(False, False)

        # Game state
        self.difficulties = {
            "Easy": (1, 50, 999),
            "Medium": (1, 100, 999),
            "Hard": (1, 500, 999),
            "Extreme": (1, 1000, 999)
        }
        self.scores = load_scores()
        self.reset_state()

        # UI setup
        self.style = ttk.Style(master)
        self.theme = 'light'
        self.setup_ui()

    def reset_state(self):
        self.level = "Medium"
        self.lowest, self.highest, _ = self.difficulties[self.level]
        self.answer = random.randint(self.lowest, self.highest)
        self.guesses = 0
        self.start_time = None
        self.timer_running = False
        self.hints_used = 0
        self.max_hints = 3
        self.multiplayer = False
        self.current_player = 1
        self.players = {1: {'name': 'Player 1', 'guesses': 0}, 2: {'name': 'Player 2', 'guesses': 0}}

    # UI builders
    def setup_ui(self):
        pad = 8
        frame = ttk.Frame(self.master, padding=pad)
        frame.grid(row=0, column=0, sticky='NSEW')

        title = ttk.Label(frame, text='🔥 Number Guessing Game', font=('Segoe UI', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 6))

        # Difficulty
        ttk.Label(frame, text='Difficulty:').grid(row=1, column=0, sticky='w')
        self.diff_var = tk.StringVar(value=self.level)
        diff_menu = ttk.OptionMenu(frame, self.diff_var, self.level, *self.difficulties.keys(), command=self.change_difficulty)
        diff_menu.grid(row=1, column=1, sticky='w')

        # Theme toggle
        self.theme_btn = ttk.Button(frame, text='Toggle Theme', command=self.toggle_theme)
        self.theme_btn.grid(row=1, column=2, sticky='e')

        # Info area
        self.info_label = ttk.Label(frame, text=self._info_text(), anchor='center')
        self.info_label.grid(row=2, column=0, columnspan=3, pady=(6, 6))

        # Entry and guess button
        self.entry_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.entry_var, width=20)
        entry.grid(row=3, column=0, columnspan=2, sticky='w')
        entry.bind('<Return>', lambda e: self.handle_guess())

        self.guess_btn = ttk.Button(frame, text='Guess', command=self.handle_guess)
        self.guess_btn.grid(row=3, column=2, sticky='e')

        # Hints and progress
        self.hint_btn = ttk.Button(frame, text=f'Hint ({self.max_hints})', command=self.give_hint)
        self.hint_btn.grid(row=4, column=0, sticky='w', pady=(6, 0))

        self.timer_label = ttk.Label(frame, text='Time: 00:00')
        self.timer_label.grid(row=4, column=1)

        self.closeness = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(frame, maximum=100.0, variable=self.closeness)
        self.progress.grid(row=5, column=0, columnspan=3, sticky='ew', pady=(6, 0))

        # Feedback
        self.feedback = ttk.Label(frame, text='Press Guess to start', font=('Segoe UI', 10))
        self.feedback.grid(row=6, column=0, columnspan=3, pady=(6, 0))

        # Multiplayer & Reset
        self.multi_btn = ttk.Button(frame, text='Multiplayer (Off)', command=self.toggle_multiplayer)
        self.multi_btn.grid(row=7, column=0, sticky='w', pady=(6, 0))

        self.reset_btn = ttk.Button(frame, text='Reset Game', command=self.reset_game)
        self.reset_btn.grid(row=7, column=1)

        self.stats_btn = ttk.Button(frame, text='Scoreboard', command=self.show_scoreboard)
        self.stats_btn.grid(row=7, column=2, sticky='e')

        # Scoreboard list at bottom
        self.scoreboard = tk.Text(frame, height=6, width=44, state='disabled')
        self.scoreboard.grid(row=8, column=0, columnspan=3, pady=(8, 0))
        self.update_scoreboard_text()

        # Start with theme
        self.apply_theme()

    # Core game logic
    def change_difficulty(self, value):
        self.level = value
        self.lowest, self.highest, _ = self.difficulties[value]
        self.reset_game(start_fresh=False)

    def reset_game(self, start_fresh=True):
        self.reset_state()
        self.answer = random.randint(self.lowest, self.highest)
        self.entry_var.set('')
        self.feedback.config(text=f'Guess a number between {self.lowest} and {self.highest}')
        self.closeness.set(0)
        self.update_hint_button()
        self.stop_timer()
        self.update_info()
        if start_fresh:
            beep()

    def toggle_multiplayer(self):
        self.multiplayer = not self.multiplayer
        self.multi_btn.config(text=f'Multiplayer ({"On" if self.multiplayer else "Off"})')
        self.reset_game()

    def give_hint(self):
        if self.hints_used >= self.max_hints:
            messagebox.showinfo('No hints', 'You used all hints.')
            return
        self.hints_used += 1
        # Hint types rotate: parity, range, divisible
        hint_type = self.hints_used % 3
        if hint_type == 1:
            hint = 'even' if self.answer % 2 == 0 else 'odd'
            message = f"Hint: The answer is {hint}."
        elif hint_type == 2:
            span = max(1, (self.highest - self.lowest) // 6)
            low = max(self.lowest, self.answer - span)
            high = min(self.highest, self.answer + span)
            message = f"Hint: The answer is between {low} and {high}."
        else:
            for d in [5, 3, 7, 11]:
                if self.answer % d == 0:
                    message = f"Hint: The answer is divisible by {d}."
                    break
            else:
                message = "Hint: The answer is a prime-ish (no small divisors)."
        messagebox.showinfo('Hint', message)
        self.update_hint_button()

    def update_hint_button(self):
        remaining = self.max_hints - self.hints_used
        self.hint_btn.config(text=f'Hint ({remaining})')

    def handle_guess(self):
        val = self.entry_var.get().strip()
        if not val:
            return
        if not val.lstrip('-').isdigit():
            self.feedback.config(text='Enter an integer value.')
            return
        guess = int(val)
        if guess < self.lowest or guess > self.highest:
            self.feedback.config(text=f'Out of range: choose {self.lowest}-{self.highest}.')
            return

        if not self.timer_running:
            self.start_timer()

        self.guesses += 1
        if self.multiplayer:
            self.players[self.current_player]['guesses'] += 1

        dist = abs(guess - self.answer)
        closeness_pct = max(0.0, 100.0 - (dist / max(1, self.highest - self.lowest)) * 100.0)
        self.closeness.set(closeness_pct)

        if guess == self.answer:
            self.end_game()
            return

        # Feedback severity
        if dist <= (self.highest - self.lowest) * 0.02:
            fb = 'Red hot! Almost there 🔥'
        elif dist <= (self.highest - self.lowest) * 0.06:
            fb = 'Very warm 👍'
        elif dist <= (self.highest - self.lowest) * 0.12:
            fb = 'Warm'
        else:
            fb = 'Cold ❄️'

        direction = 'higher' if guess < self.answer else 'lower'
        self.feedback.config(text=f'{fb} Try {direction}.')

        if self.multiplayer:
            self.switch_player()

        self.entry_var.set('')
        beep()
        self.update_info()

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.update_info()

    def end_game(self):
        self.stop_timer()
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        if self.multiplayer:
            winner = self.current_player
            msg = f"🎉 {self.players[winner]['name']} wins!\nGuesses: {self.players[winner]['guesses']}\nTime: {elapsed}s"
        else:
            msg = f"🎉 Correct! The answer was {self.answer}\nGuesses: {self.guesses}\nTime: {elapsed}s"

        messagebox.showinfo('You Won!', msg)
        beep()
        self.update_scores(elapsed)
        self.update_scoreboard_text()
        self.reset_game(start_fresh=False)

    def update_scores(self, elapsed):
        key = self.level
        score_value = {'guesses': self.guesses, 'time': elapsed}
        current = self.scores.get(key)
        better = False
        if current is None:
            better = True
        else:
            # lower guesses better, then lower time
            if score_value['guesses'] < current['guesses']:
                better = True
            elif score_value['guesses'] == current['guesses'] and score_value['time'] < current['time']:
                better = True
        if better:
            self.scores[key] = score_value
            save_scores(self.scores)

    # Timer
    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        threading.Thread(target=self._timer_thread, daemon=True).start()

    def stop_timer(self):
        self.timer_running = False

    def _timer_thread(self):
        while self.timer_running:
            elapsed = int(time.time() - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.timer_label.config(text=f'Time: {mins:02d}:{secs:02d}')
            time.sleep(1)

    # UI helpers
    def update_info(self):
        if self.multiplayer:
            info = f"{self.players[self.current_player]['name']}'s turn — Guess {self.lowest}-{self.highest}"
        else:
            info = f"Guess a number between {self.lowest} and {self.highest}"
        self.info_label.config(text=info)

    def show_scoreboard(self):
        sb = "Best Scores:\n"
        for k in self.difficulties.keys():
            s = self.scores.get(k)
            if s:
                sb += f"{k}: {s['guesses']} guesses, {s['time']}s\n"
            else:
                sb += f"{k}: -\n"
        messagebox.showinfo('Scoreboard', sb)

    def update_scoreboard_text(self):
        content = "Best Scores:\n"
        for k in self.difficulties.keys():
            s = self.scores.get(k)
            if s:
                content += f"{k}: {s['guesses']} guesses, {s['time']}s\n"
            else:
                content += f"{k}: -\n"
        self.scoreboard.config(state='normal')
        self.scoreboard.delete('1.0', tk.END)
        self.scoreboard.insert(tk.END, content)
        self.scoreboard.config(state='disabled')

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.apply_theme()

    def apply_theme(self):
        if self.theme == 'dark':
            try:
                self.style.theme_use('clam')
            except Exception:
                pass
            self.master.configure(bg='#2b2b2b')
        else:
            try:
                self.style.theme_use('default')
            except Exception:
                pass
            self.master.configure(bg=None)

    def _info_text(self):
        return f"Guess a number between {self.lowest} and {self.highest}"


if __name__ == '__main__':
    root = tk.Tk()
    app = NumberGuessingGUI(root)
    root.mainloop()