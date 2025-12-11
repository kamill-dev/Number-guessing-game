⭐ Python Number Guessing Game (GUI)

A fun and interactive number guessing game built with Python Tkinter. Try to guess the randomly generated number as quickly as possible while enjoying hints, multiplayer mode, timer, and score tracking.

🔧 Requirements

Python 3 installed on your system

Tkinter (usually comes pre-installed with Python)

VS Code or any other code editor to run/edit the script

▶️ How to Run

Open a terminal in the folder containing your script (main.py or number_guessing_gui.py).

Run the script:

python main.py


Interact with the GUI:

Enter your guess in the input box

Press Guess or hit Enter

Use Hints, Reset Game, Multiplayer, and Scoreboard features

🚀 Features

🎲 Random number generation with four difficulty levels: Easy, Medium, Hard, Extreme

⏱ Timer tracks how long it takes to guess

🧩 Hints system: parity, range, or divisibility hints (max 3 per game)

🏆 Scoreboard saves best scores for each difficulty in scores.json

🔄 Multiplayer mode for two players

🔔 Cross-platform beep for guesses (Windows winsound or Tkinter bell fallback)

📊 Guess progress bar shows closeness to the correct number

🌗 Light/Dark themes for the GUI

🎮 Gameplay

Select a difficulty level from the dropdown

Type a number within the specified range

Press Guess

Feedback will indicate if your guess is too high, too low, or close

Use Hints if you get stuck (limited to 3 per game)

The game ends when you guess correctly, and your score is updated if it’s a personal best

⚙️ Notes

Score tracking is saved in scores.json automatically

Works on Windows, Linux, and macOS

Supports two-player mode, switching turns after each guess

Timer and progress bar provide live feedback during the game.