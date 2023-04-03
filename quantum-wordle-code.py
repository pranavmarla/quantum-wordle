from qiskit import Aer, execute, QuantumCircuit


# Every answer and guess has to contain this many letters/characters
WORD_LENGTH = 5

# Number of chances the user has to guess the answer
MAX_ATTEMPTS = 6

# Max number of guesses user can make in one attempt
MAX_GUESSES_PER_ATTEMPT = 2

# List (technically, tuple) of all possible answers
# Source: https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee
#! DEBUG: Replace with actual list
ANSWERS = ('APPLE')
# List of all valid (allowed) guesses, excluding the words already in the answers list
# Source: https://gist.github.com/cfreshman/d5fb56316158a1575898bba1eed3b5da
#! DEBUG: Replace with actual list
ALLOWED_GUESSES_EXCLUDING_ANSWERS = ('WEARY', 'KEBAB')

# The strings that the user needs to enter to select these options
CLASSICAL_GUESS_OPTION = '1'
QUANTUM_GUESS_OPTION = '2'
MEASURE_OPTION = '3'
EXIT_OPTION = '4'

# Colour feedback chars: Indicate correctness of corresponding letter in guess word
RIGHT_LETTER_RIGHT_SPOT_COLOUR = '🟩'
RIGHT_LETTER_WRONG_SPOT_COLOUR = '🟨'
WRONG_LETTER_COLOUR = '🟥'


class Attempt:
    """Stores data about each attempt"""

    def __init__(self, attempt_num, qubit_index):
        # Keeps track of which attempt this is (starting at 1)
        self.attempt_num = attempt_num
        # Keeps track of which qubit is used to store info regarding this attempt's guesses
        self.qubit_index = qubit_index
        # Dictionary mapping each guess to colour feedback string indicating its correctness
        # Contains the words guessed by the user in this attempt, in the order that they guessed them in
        self.guess_to_feedback_dict = {}


def safe_input(user_prompt=''):
    """Safely take in user input, making sure to accept only valid input
    
    Input:
        user_prompt: Optional string to be printed as a prompt for user prior to reading in their input

    Output:
        Returns valid user input
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
            print('Please enter valid (non-empty) input!\n')
    
    # For consistency, if the input is a word, ensure it is in upper case
    if user_input.isalpha():
        user_input = user_input.upper()
    
    return user_input


def is_guess_valid(guess, allowed_guesses_excluding_answers=ALLOWED_GUESSES_EXCLUDING_ANSWERS, answers=ANSWERS):
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


def prepare_game_state(max_attempts=MAX_ATTEMPTS):
    """Prepare the variable that will store the state of the game at any point
    
    Input:
        max_attempts
        
    Output:
        attempts_list: Stores current game state (state of each attempt)
        game_circuit: Quantum circuit used to store info regarding each attempt's guesses
    """

    num_qubits = num_classical_bits = max_attempts
    game_circuit = QuantumCircuit(num_qubits, num_classical_bits)

    attempts_list = []
    for i in range(max_attempts):
        qubit_index = i
        attempt_num = i + 1
        attempts_list.append(Attempt(attempt_num, qubit_index))
    
    return attempts_list, game_circuit


# def print_same_line(output_string):
#     """Print output without automatically adding a newline at the end"""
#     print(foutput_string, end='')

def print_guess(guess_string):
    """Print a single guess word, letter by letter. Does not print a newline at the end."""
    for char in guess_string:
        # Pad each character of guess to be two spaces, to align with each character (coloured square) of the colour feedback string which seems to take up two spaces
        print(f'{char:>2}', end='')


def print_classical_attempt(attempt_num, guess_to_feedback_dict, space=' '):

    if attempt_num != 1:
        # Add three new lines before every attempt (except the first)
        print('\n\n\n', end='')

    # For reasonably consistent output across different platforms, only use spaces, not tabs (as tabs can be rendered differently on different platforms)!
    # Number of spaces in below commands determined experimentally
    print(f'Attempt {attempt_num}:{space*13}', end='')

    # Since this is a classical guess, we know there is only one guess in the dict
    guess, feedback = list(guess_to_feedback_dict.items())[0]
    print_guess(guess)
    # Print one new line
    # Same as: print('\n', end='')
    print()
    # Note that this automatically prints a newline at the end
    print(f'{space*23}{feedback}')


def print_game_state(attempts_list, game_circuit, max_attempts=MAX_ATTEMPTS):
    
    for index, attempt in enumerate(attempts_list):
        attempt_num = index + 1
        print(f'Attempt {index + 1}:', end='')

        # Print guesses
        for guess in attempt.guess_to_feedback_dict:
            # Tab indentation before each guess
            print('\t')
            for char in guess:
                # Pad each character of guess to be two spaces, to align with each character (coloured square) of the colour feedback string which seems to take up two spaces
                print(f'{char:>2}', end='')
        
        # New line
        print()

        # Print colour feedback corresponding to each guess




def check_guess_correctness(guess_str, answer_str, word_length=WORD_LENGTH):
    """Compares the guess with the answer and returns colour feedback indicating how close the guess was.

    Input:
        - guess_str: Guess word input by the user
        - answer_str: Answer word
        Note: 
            - Assumes both input strings are the same 'case', so they can be compared
            - Assumes both input strings consist of word_length characters

    Output:
        Returns a string consisting of word_length coloured boxes, where each box indicates the correctness of the corresponding letter of the guess word
    """

    # The guess is the same as the answer -- i.e. all the letters of the guess word are both the right letter and in the right position
    if guess_str == answer_str:
        # Assuming word_length = 5 and RIGHT_LETTER_RIGHT_SPOT_COLOUR = '🟩':
        # '🟩🟩🟩🟩🟩'
        colour_feedback_str = word_length * RIGHT_LETTER_RIGHT_SPOT_COLOUR
        return colour_feedback_str
    
    else:
        # Convert both guess and answer from string to list
        guess_char_list = list(guess_str)
        answer_char_list = list(answer_str)

        # This is technically a range object, not a list but, if it were converted to a list, if would look like this (assuming word_length = 5):
        # [0, 1, 2, 3, 4]
        word_index_list = range(word_length)

        # Each element of this list will be a coloured box character, where each box indicates the correctness of the corresponding letter of the guess word
        # Assuming word_length = 5:
        # [None, None, None, None, None]
        colour_feedback_list = [None for i in word_index_list]

        # NOTE: If there are repeated letters in either guess or answer, looking for a match (for each letter of guess) by iterating over the letters of answer from left to right is NOT guaranteed to work!
        # Eg. Let guess be 'CABAL' and 
        #        answer be 'ABBEY':
        #     In this case, if we do left to right evaluation of answer for each letter of guess, we will compare the 'B' in 'CABAL' to the 1st 'B' in 'ABBEY' and say that it is the right letter but the wrong position and then stop iterating over answer since we already found a match for that guess letter.
        #     However, the correct answer is to say that, since the 'B' in 'CABAL' matches the 2nd 'B' in 'ABBEY', it is actually both the right letter and the right position!

        # Check for right letter and right position matches by comparing each guess letter to the answer letter in the same position only
        # Note:
        #   - We are iterating over the guess and answer simultaneously, one time -- i.e. we are comparing 1st letter of guess to 1st letter of answer, 2nd letter of guess to 2nd letter of answer, etc.
        #   - We check this condition first, since this dominates in case of repeated guess letters (see example above)
        #   - Although not strictly necessary (since we're not changing the length of the answer_char_list, just its current element), to be safe, we iterate over a COPY of answer_char_list rather than the original answer_char_list itself (which is what we're changing during the iteration)
        for index, guess_char, answer_char in zip(word_index_list, guess_char_list, answer_char_list[:]):
            # Since we are only comparing guess and answer letters in the same position, if they match, then we already know that it's both the right letter and the right position
            if guess_char == answer_char:
                colour_feedback_list[index] = RIGHT_LETTER_RIGHT_SPOT_COLOUR
                # Now that a char in answer has been matched by a char in guess, remove that char from answer so that other chars in guess don't accidentally match it
                # Specifically, to avoid changing the length of answer_char_list, replace current char with None since that's guaranteed not to match any letter)
                answer_char_list[index] = None

        # At this point, we've identified all the letters of the guess that are both the right letter and in the right position.
        # The remaining letters are either the right letter but in the wrong position, or just the wrong letter.
        # At this point, for each guess letter, iterating over the answer letters from left to right WILL give us the right answer
        # Eg. Let guess be 'EERIE' and
        #        answer be 'TENET'
        #     In this case, assuming we previously found that the 2nd 'E' in 'EERIE' was both the right letter and in the right position, now we would expect to mark the 1st 'E' as being the right letter but in the wrong position (compared to the 2nd 'E' in 'TENET'), and the 3rd 'E' as being the wrong letter (no corresponding letter in 'TENET') -- i.e. after the 2nd 'E' in the guess is perfectly matched above, the LEFTMOST remaining 'E' in the guess is compared with the corresponding letter in the answer before the more rightward remaining 'E' in the guess.

        # Check for right letter but wrong position matches by comparing each guess letter to EVERY answer letter
        # For efficiency, only check the guess letters whose correctness is still unknown
        for guess_index, guess_char in enumerate(guess_char_list):
            # Correctness of this guess letter is still unknown
            if colour_feedback_list[guess_index] is None:
                guess_char_in_answer = False
                # Technically, we only need to compare each guess letter to all the answer letters that are NOT in the same position (since we already compared against the answer letter in the same position above), but it's simpler to just compare against every answer letter
                # Can safely compare guess letter against every answer letter without worrying about matching a previously matched answer letter, since the answer letters that were previously matched above have been replaced with None, which is guaranteed not to match any letter in guess
                for answer_index, answer_char in enumerate(answer_char_list[:]):
                    # Guess letter is the right letter but we already know it's in the wrong position (since otherwise we would have matched it above)
                    if guess_char == answer_char:
                        guess_char_in_answer = True
                        colour_feedback_list[guess_index] = RIGHT_LETTER_WRONG_SPOT_COLOUR
                        # Again, replace the matched answer letter with None so it doesn't accidentally get matched again later on by another (duplicate) guess letter
                        answer_char_list[answer_index] = None
                        # Now that we've found a match for the current guess letter, stop iterating through answer so that we don't wrongly match another (duplicate) answer letter and replace that with None as well!
                        # This ensures that one guess letter does not accidentally "use up" (match with) multiple duplicate answer letters
                        break
                # At this point, have checked guess_char against every letter in answer -- if we still haven't found a match, then guess_char is simply the wrong letter
                if not guess_char_in_answer:
                    colour_feedback_list[guess_index] = WRONG_LETTER_COLOUR

        # Now that we've assembled the colour feedback list for all the letters in the guess word, convert it from list to string and return it
        colour_feedback_str = ''.join(colour_feedback_list)
        return colour_feedback_str


def test_check_guess_correctness():
    """Used to quickly test check_guess_correctness()"""

    # Each tuple contains the input guess word, the answer word it will be compared against and the expected output colour feedback indicating how close/correct the guess was
    test_value_tuples = \
        [
            # Guess and answer are identical
            (
                'TWINS', 
                'TWINS', 
                f'{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}'
            ),

            # Guess and answer have no letters in common
            (
                'FRAUD', 
                'TWINS', 
                f'{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}'
            ),

            # Neither guess nor answer has repeated letters: Output contains all 3 match possibilities
            (
                'SWORE', 
                'WEARY', 
                f'{WRONG_LETTER_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}'
            ),


            # Guess has repeated letters, but answer doesn't: 1st repeated letter of guess matches and is in same position as answer letter
            (
                'WEEPY', 
                'WEARY', 
                f'{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}'
            ),
            # Guess has repeated letters, but answer doesn't: 2nd repeated letter of guess matches and is in same position as answer letter
            (
                'EERIE', 
                'WEARY', 
                f'{WRONG_LETTER_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}'
            ),


            # Both guess and answer have same repeated letters: 2nd repeated letter of guess matches and is in same position as 2nd of answer
            (
                'LEVER', 
                'EATEN', 
                f'{WRONG_LETTER_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{WRONG_LETTER_COLOUR}'),
            # Both guess and answer have same repeated letters: 1st repeated letter of guess matches and is in same position as 2nd of answer
            (
                'KEBAB', 
                'ABBEY', 
                f'{WRONG_LETTER_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}'
            ),
            # Both guess and answer have same repeated letters: Although they match, neither repeated letter of guess is in same position as corresponding repeated letters of answer
            (
                'PAPAL', 
                'ALARM', 
                f'{WRONG_LETTER_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}'
            ),


            # Both guess and answer have same repeated letters, but guess has more than 2: The 3 repeated letters of guess span all three match possibilities
            (
                'EERIE', 
                'TENET', 
                f'{RIGHT_LETTER_WRONG_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}'
            ),
            

            # Guess doesn't have repeated letters, but answer does: Guess letter matches and is in same position as 1st repeated letter of answer
            (
                'WEARY', 
                'WEEPY', 
                f'{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{WRONG_LETTER_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}'
            ),
            # Guess doesn't have repeated letters, but answer does: Guess letter matches and is in same position as 2nd repeated letter of answer
            (
                'WEARY', 
                'EERIE', 
                f'{WRONG_LETTER_COLOUR}{RIGHT_LETTER_RIGHT_SPOT_COLOUR}{WRONG_LETTER_COLOUR}{RIGHT_LETTER_WRONG_SPOT_COLOUR}{WRONG_LETTER_COLOUR}'
            )
        ]

    for guess_str, answer_str, expected_colour_feedback_str in test_value_tuples:
        actual_colour_feedback_str = check_guess_correctness(guess_str, answer_str)
        if actual_colour_feedback_str == expected_colour_feedback_str:
            print('Pass')
        else:
            print('Fail!')
            print('\tGuess:\t\t{}'.format('\t'.join(guess_str)))
            print('\tAnswer:\t\t{}'.format('\t'.join(answer_str)))
            print('\tExpected:\t{}'.format('\t'.join(expected_colour_feedback_str)))
            print('\tActual:\t\t{}'.format('\t'.join(actual_colour_feedback_str)))

# # Uncomment to run test suite
# test_check_guess_correctness()


def run_game(classical_guess_option=CLASSICAL_GUESS_OPTION, quantum_guess_option=QUANTUM_GUESS_OPTION, measure_option=MEASURE_OPTION, exit_option=EXIT_OPTION, max_attempts=MAX_ATTEMPTS):

    # Print only the first time
    print('Welcome to Quantum Wordle!')
    print('Can you guess the mystery five-letter word in six attempts or less?\n')

    attempts_list, game_circuit = prepare_game_state()
    print_game_state(attempts_list, game_circuit)

    keep_playing = True
    while keep_playing:
        
        keep_playing = False
        print('Select an option by entering the corresponding number:')
        print(f'{classical_guess_option}: Classical guess (1 word)')
        print(f'{quantum_guess_option}: Quantum guess (superposition of 2 words)')
        print(f'{measure_option}: Measure (collapse) all superpositions')
        print(f'{exit_option}: Exit')
        user_choice = safe_input('--> ')

        if user_choice == classical_guess_option:
            guess = safe_input('Enter guess: ')
            print(f'You entered "{guess}"')
            if is_guess_valid(guess):
                print('Guess is valid')
            else:
                print('Guess is invalid')

run_game()