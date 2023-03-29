# List (technically, tuple) of all possible answers
# Source: https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee
ANSWERS = ('APPLE')
# List of all valid (allowed) guesses, excluding the words already in the answers list
# Source: https://gist.github.com/cfreshman/d5fb56316158a1575898bba1eed3b5da
ALLOWED_GUESSES_EXCLUDING_ANSWERS = ('WEARY', 'KEBAB')

# The strings that the user needs to enter to select these options
CLASSIC_GUESS_OPTION = '1'
QUANTUM_GUESS_OPTION = '2'
MEASURE_OPTION = '3'
EXIT_OPTION = '4'


def safe_input(user_prompt=''):
    """Safely take in user input
    
    Input:
        user_prompt: Optional string to be printed as a prompt for user prior to reading in their input

    Output:
        Returns validated user input
    """

    user_input = None

    # Keep asking user for input until we get valid (non-empty) input
    while not user_input:
        # Note: input('') appears to be the same as input()
        user_input = input(user_prompt)
        # Remove any extra spaces from user input
        user_input = user_input.strip()
        # user_input is an empty string
        if not user_input:
            print('Please enter valid input!\n')
    
    # For consistency, ensure input is in upper case
    user_input = user_input.upper()
    return user_input


def validate_guess(guess, allowed_guesses_excluding_answers=ALLOWED_GUESSES_EXCLUDING_ANSWERS, answers=ANSWERS):
    """Check if guess input by user is valid (allowed)
    
    Input:
        guess: Guess word entered by user
        allowed_guesses_excluding_answers: List of allowed guesses, excluding words that are already in the answers list
        answers: List of possible answers

    Output:
        Returns True/False, depending on whether or not the guess is considered valid
    """
    if (guess in allowed_guesses_excluding_answers) or (guess in answers):
        return True
    else:
        return False


def run_game(classic_guess_option=CLASSIC_GUESS_OPTION, quantum_guess_option=QUANTUM_GUESS_OPTION, measure_option=MEASURE_OPTION, exit_option=EXIT_OPTION):

    # Print only the first time
    print('Welcome to Quantum Wordle!')

    keep_playing = True

    while keep_playing:
        
        keep_playing = False
        print('Select an option by entering the corresponding number:')
        print(f'{classic_guess_option}: Classic guess (1 word)')
        print(f'{quantum_guess_option}: Quantum guess (superposition of 2 words)')
        print(f'{measure_option}: Measure (collapse) all superpositions')
        print(f'{exit_option}: Exit')
        user_choice = safe_input('--> ')

        if user_choice == classic_guess_option:
            guess = safe_input('Enter guess: ')
            print(f'You entered "{guess}"')
            if validate_guess(guess):
                print('Guess is valid')
            else:
                print('Guess is invalid')

run_game()