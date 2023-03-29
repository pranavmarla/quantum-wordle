# List (technically, tuple) of all past and future answers
# Source: https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee
ANSWERS = ('APPLE')
# List of all valid (allowed) guesses, excluding the words already in answers
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
        raw_user_input = input(user_prompt)
        # Remove any extra spaces from user input
        user_input = raw_user_input.strip()
        # user_input is an empty string
        if not user_input:
            print('Please enter valid input!\n')
    
    return user_input


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

run_game()