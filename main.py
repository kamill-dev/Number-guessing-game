# NOTE: To run thiscode, ensure you have Python installed with Tkinter support.



import json
import random
import time
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


# Utility: Cross-platform beep

try:
    import winsound
    def beep():
        winsound.Beep(1000, 120)
except Exception:
    def beep():
        try:
            root = tk._default_root
            if root:
                root.bell()
        except Exception:
            pass

# score will save in scores.json 

SCORES_FILE = Path("scores.json")
HISTORY_FILE = Path("history.json")

DEFAULT_SCORES = {
    "Easy": None,
    "Medium": None,
    "Hard": None,
    "Extreme": None
}


def load_scores():
    if SCORES_FILE.exists():
        try:
            return json.load(open(SCORES_FILE))
        except Exception:
            pass
    return DEFAULT_SCORES.copy()


def save_scores(scores):
    json.dump(scores, open(SCORES_FILE, "w"), indent=2)


# -------------------------------
# Main App
# -------------------------------
class NumberGuessingGUI:
    """
    Feature-rich Number Guessing Game using Tkinter.
    Includes difficulty levels, multiplayer mode, hints,
    timers, persistent scores, and theming.
    """

    def __init__(self, master):
        self.master = master
        self.master.title("Number Guessing Game")
        self.master.resizable(False, False)
        self.center_window()

        # Game config
        self.difficulties = {
            "Easy": (1, 50),
            "Medium": (1, 100),
            "Hard": (1, 500),
            "Extreme": (1, 1000)
        }

        self.scores = load_scores()
        self.theme = "light"

        self.reset_state()
        self.setup_ui()
        self.apply_theme()

        # Shortcuts
        self.master.bind("<Control-r>", lambda e: self.reset_game())
        self.master.bind("<Control-h>", lambda e: self.give_hint())
        self.master.bind("<Escape>", lambda e: self.master.quit())

    # -------------------------------
    # State
    # -------------------------------
    def reset_state(self):
        self.level = "Medium"
        self.lowest, self.highest = self.difficulties[self.level]
        self.answer = random.randint(self.lowest, self.highest)
        self.guesses = 0
        self.hints_used = 0
        self.max_hints = 3
        self.start_time = None
        self.timer_running = False

        self.multiplayer = False
        self.current_player = 1
        self.players = {
            1: {"name": "Player 1", "guesses": 0},
            2: {"name": "Player 2", "guesses": 0}
        }

    # -------------------------------
    # UI
    # -------------------------------
    def setup_ui(self):
        frame = ttk.Frame(self.master, padding=10)
        frame.grid()

        ttk.Label(
            frame,
            text="🔥 Number Guessing Game",
            font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=5)

        ttk.Label(frame, text="Difficulty:").grid(row=1, column=0, sticky="w")
        self.diff_var = tk.StringVar(value=self.level)
        ttk.OptionMenu(
            frame, self.diff_var, self.level,
            *self.difficulties.keys(),
            command=self.change_difficulty
        ).grid(row=1, column=1, sticky="w")

        ttk.Button(
            frame, text="Toggle Theme",
            command=self.toggle_theme
        ).grid(row=1, column=2)

        self.info_label = ttk.Label(frame)
        self.info_label.grid(row=2, column=0, columnspan=3, pady=5)

        self.entry_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.entry_var, width=18)\
            .grid(row=3, column=0, columnspan=2, sticky="w")

        ttk.Button(frame, text="Guess", command=self.handle_guess)\
            .grid(row=3, column=2)

        self.hint_btn = ttk.Button(
            frame, text="Hint (3)", command=self.give_hint
        )
        self.hint_btn.grid(row=4, column=0, pady=5, sticky="w")

        self.timer_label = ttk.Label(frame, text="Time: 00:00")
        self.timer_label.grid(row=4, column=1)

        self.progress_val = tk.DoubleVar()
        ttk.Progressbar(
            frame, maximum=100, variable=self.progress_val
        ).grid(row=5, column=0, columnspan=3, sticky="ew")

        self.feedback = ttk.Label(frame)
        self.feedback.grid(row=6, column=0, columnspan=3, pady=5)

        ttk.Button(
            frame, text="Multiplayer (Off)",
            command=self.toggle_multiplayer
        ).grid(row=7, column=0)

        ttk.Button(
            frame, text="Reset Game",
            command=self.reset_game
        ).grid(row=7, column=1)

        ttk.Button(
            frame, text="Scoreboard",
            command=self.show_scoreboard
        ).grid(row=7, column=2)

        ttk.Label(
            frame,
            text="Shortcuts: Ctrl+R Reset | Ctrl+H Hint | Esc Exit",
            font=("Segoe UI", 8)
        ).grid(row=8, column=0, columnspan=3, pady=4)

        self.update_info()

    # -------------------------------
    # Game Logic  (you can change game logic here)
    # -------------------------------
  

    def handle_guess(self):
        value = self.entry_var.get().strip()
        if not value.isdigit():
            self.feedback.config(text="Enter a valid number.")
            return

        guess = int(value)
        if guess < self.lowest or guess > self.highest:
            self.feedback.config(
                text=f"Out of range ({self.lowest}-{self.highest})"
            )
            return

        if not self.timer_running:
            self.start_timer()

        self.guesses += 1
        self.players[self.current_player]["guesses"] += 1

        distance = abs(guess - self.answer)
        span = self.highest - self.lowest
        self.progress_val.set(max(0, 100 - (distance / span) * 100))

        if guess == self.answer:
            self.end_game()
            return

        direction = "higher" if guess < self.answer else "lower"
        self.feedback.config(text=f"Try {direction}!")
        beep()

        if self.multiplayer:
            self.switch_player()

        self.entry_var.set("")
        self.update_info()

    def end_game(self):
        self.stop_timer()
        elapsed = int(time.time() - self.start_time)

        if self.level == "Extreme" and elapsed > 60:
            messagebox.showwarning(
                "Time Up", "Extreme mode timeout!"
            )
            self.reset_game()
            return

        msg = (
            f"🎉 Correct!\n"
            f"Answer: {self.answer}\n"
            f"Guesses: {self.guesses}\n"
            f"Time: {elapsed}s"
        )

        messagebox.showinfo("You Win!", msg)
        beep()

        self.update_scores(elapsed)
        self.save_history(elapsed)
        self.reset_game(start_fresh=False)

    # -------------------------------
    # Helpers  (Default hint count 3, you can change it here)
    # -------------------------------
    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def _timer_loop(self):
        while self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(
                text=f"Time: {elapsed//60:02d}:{elapsed%60:02d}"
            )
            time.sleep(1)

    def stop_timer(self):
      self.timer_running = False

    def give_hint(self):
        if self.hints_used >= self.max_hints:
            messagebox.showinfo("Hints", "No hints left!")
            return

        self.hints_used += 1
        self.hint_btn.config(
            text=f"Hint ({self.max_hints - self.hints_used})"
        )

        hint = "Even" if self.answer % 2 == 0 else "Odd"
        messagebox.showinfo("Hint", f"The number is {hint}.")

    def toggle_multiplayer(self):
        self.multiplayer = not self.multiplayer
        if self.multiplayer:
            self.players[1]["name"] = simpledialog.askstring(
                "Player 1", "Enter Player 1 name:"
            ) or "Player 1"
            self.players[2]["name"] = simpledialog.askstring(
                "Player 2", "Enter Player 2 name:"
            ) or "Player 2"
        self.reset_game()

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1

    def update_info(self):
        if self.multiplayer:
            self.info_label.config(
                text=f"{self.players[self.current_player]['name']}'s turn"
            )
        else:
            self.info_label.config(
                text=f"Guess a number between {self.lowest}-{self.highest}"
            )

    def change_difficulty(self, level):
        self.level = level
        self.lowest, self.highest = self.difficulties[level]
        self.reset_game()

    def reset_game(self, start_fresh=True):
        self.reset_state()
        self.answer = random.randint(self.lowest, self.highest)
        self.feedback.config(text="")
        self.progress_val.set(0)
        self.hint_btn.config(text="Hint (3)")
        self.stop_timer()
        self.update_info()
        if start_fresh:
            beep()

    def update_scores(self, elapsed):
        current = self.scores.get(self.level)
        score = {"guesses": self.guesses, "time": elapsed}
        if current is None or score["guesses"] < current["guesses"]:
            self.scores[self.level] = score
            save_scores(self.scores)

    def save_history(self, elapsed):
        record = {
            "difficulty": self.level,
            "guesses": self.guesses,
            "time": elapsed,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        history = []
        if HISTORY_FILE.exists():
            history = json.load(open(HISTORY_FILE))
        history.append(record)
        json.dump(history[-20:], open(HISTORY_FILE, "w"), indent=2)

    def show_scoreboard(self):
        msg = "🏆 Best Scores\n\n"
        for k, v in self.scores.items():
            msg += f"{k}: {v['guesses']} guesses, {v['time']}s\n" if v else f"{k}: -\n"
        messagebox.showinfo("Scoreboard", msg)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam" if self.theme == "dark" else "default")

    def center_window(self, w=420, h=520):
        x = (self.master.winfo_screenwidth() - w) // 2
        y = (self.master.winfo_screenheight() - h) // 2
        self.master.geometry(f"{w}x{h}+{x}+{y}")


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    NumberGuessingGUI(root)
    root.mainloop()

