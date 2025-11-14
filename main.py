
# Import the random module to generate random numbers
import random

# Set the range for the guessing game
lowest_num = 1
highest_num = 100

# Generate a random number between lowest_num and highest_num
answer = random.randint(lowest_num, highest_num)

# Initialize counter to track number of guesses
gusses = 0 

# Initialize game status flag to control the game loop
is_running = True

# Display game title and instructions to the player
print("PYTHON NUMBER GUESSING GAME")
print(f"guess a number between {lowest_num} and {highest_num}")

# Main game loop - continues until player guesses correctly
while is_running:
    
    # Get player's guess as input from keyboard
    guess = input("Enter your guess : ")

    # Check if the input is a valid digit
    if guess.isdigit():

        # Convert the string input to an integer for comparison
        guess = int(guess)
        
        # Increment the guess counter
        gusses += 1

        # Check if the guess is outside the valid range
        if guess < lowest_num or guess > highest_num:
            print("This number is out of range")

        # Check if the guess is lower than the answer
        elif guess < answer:
            print("too low! Try again")

        # Check if the guess is higher than the answer
        elif guess > answer:
            print("too high! Try again")

        # Check if the guess matches the answer (correct!)
        else:
            print(f"Correct! The answer is {answer}")
            print(f"Number of guesses: {gusses}")
            is_running = False

    # Handle invalid input (non-numeric values)
    else:
        print("invalid guess")
        print(f"Please select a number between {lowest_num} and {highest_num}")