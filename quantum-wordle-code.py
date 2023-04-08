# Note: For some reason, just importing the Qiskit libraries seems to take ~2 seconds and importing the IPython libraries seems to take ~1 second. Thus, to avoid delays when re-running the game, move the code to actually run the game to a separate cell
from enum import auto, Enum
from IPython.display import clear_output
from math import floor, log2
from qiskit import Aer, execute, QuantumCircuit
from time import sleep


# Every answer and guess has to contain this many letters/characters
WORD_LENGTH = 5

# Number of chances that user has to guess the answer
MAX_ATTEMPTS = 6

# Max number of guesses user can make in one attempt
MAX_GUESSES_PER_ATTEMPT = 2

# List (technically, tuple) of all possible answers
# Source: https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee
#! DEBUG: Replace with actual list
ANSWERS = ('APPLE',)
# List of all valid (allowed) guesses, excluding the words already in the answers list
# Source: https://gist.github.com/cfreshman/d5fb56316158a1575898bba1eed3b5da
#! DEBUG: Replace with actual list
ALLOWED_GUESSES_EXCLUDING_ANSWERS = ('WEARY', 'KEBAB', 'GRAZE', 'WEEPY', 'PIETY', 'PAPAL')

# The strings that the user needs to enter to select these options
CLASSICAL_ATTEMPT_OPTION = '1'
QUANTUM_ATTEMPT_OPTION = '2'
MEASURE_OPTION = '3'
EXIT_OPTION = '4'

# Colour feedback chars: Indicate correctness of corresponding letter in guess word
RIGHT_LETTER_RIGHT_SPOT_COLOUR = '🟩'
RIGHT_LETTER_WRONG_SPOT_COLOUR = '🟨'
WRONG_LETTER_COLOUR = '🟥'
# Used to indicate lack of feedback
NO_FEEDBACK_COLOUR = '⬜'

# Colour feedback string when the guess is correct (i.e. matches the answer)
# Eg. Assuming word_length = 5 and RIGHT_LETTER_RIGHT_SPOT_COLOUR = '🟩': 
#   '🟩🟩🟩🟩🟩'
RIGHT_GUESS_FEEDBACK_STRING = WORD_LENGTH * RIGHT_LETTER_RIGHT_SPOT_COLOUR

# Used as a placeholder for when the user hasn't made a guess yet
NO_GUESS_STRING = WORD_LENGTH * '_'
# "Blank" colour feedback string used to convey that we don't have any feedback yet
NO_FEEDBACK_STRING = WORD_LENGTH * NO_FEEDBACK_COLOUR

# Char representing one space
SPACE_CHAR = ' '

NUM_GUESSES_IN_SUPERPOSITION = 2

# Backend used to execute quantum circuits
QUANTUM_BACKEND = Aer.get_backend('qasm_simulator')

# When this character is printed, it moves the cursor back to the beginning of the current line, which allows us to potentially overwrite any previous output on the current line
RESET_CURSOR_CHAR = '\r'


class AttemptType(Enum):
    """Used to indicate type of an attempt (i.e. classical or quantum)"""
    CLASSICAL = auto()
    QUANTUM = auto()


class Attempt:
    """Stores attempt data"""

    def __init__(self, qubit_index: int, attempt_type: AttemptType = None):
        # Keeps track of which qubit is used to encode which of this attempt's guesses should be used (starting at 0)
        self.qubit_index: int = qubit_index
        # Tells us whether this is a classical attempt or a quantum attempt
        self.type: AttemptType = attempt_type
        # Dictionary mapping each guess to colour feedback string indicating its correctness
        # Contains the words guessed by the user in this attempt, in the order that they guessed them in
        self.guess_to_feedback_dict = {}
        # For quantum attempts (multiple guesses), we intentionally display the guess feedback strings in a random order, so it's not clear which guess each feedback string corresponds to. This list stores the feedback strings in the random order that they will be displayed in
        self.feedback_display_list = None


def safe_input(user_prompt: str = '') -> str:
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
            print('Please enter valid (non-empty) input!')
    
    # For consistency, if the input is a word, ensure it is in upper case
    if user_input.isalpha():
        user_input = user_input.upper()
    
    return user_input


def safe_guess_input(user_prompt='', allowed_word_length=WORD_LENGTH):
    """Safely take in guess supplied by user, returning only when the user has entered a valid guess"""
    
    received_valid_guess = False
    while not received_valid_guess:
        guess = safe_input(user_prompt)
        if (len(guess) == allowed_word_length) and is_guess_valid(guess):
            received_valid_guess = True
        else:
            print('Guess is invalid!')
    
    return guess


def is_guess_valid(guess, allowed_guesses_excluding_answers=ALLOWED_GUESSES_EXCLUDING_ANSWERS, answers=ANSWERS):
    """Check if guess input by user is valid (allowed)
    
    Input:
        guess: Guess word entered by user
        allowed_guesses_excluding_answers: List of allowed guesses, excluding words that are already in the answers list
        answers: List of possible answers

    Output:
        True/False, depending on whether or not the guess is considered valid
    """
    if (guess in allowed_guesses_excluding_answers) or (guess in answers):
        return True
    else:
        return False


def choose_answer(answer_list=ANSWERS) -> str:
    """Randomly chooses a word from the list of all possible answers to be the answer for this run of the game"""
    answer_index = random_number_generator(max=(len(answer_list) - 1))
    answer = answer_list[answer_index]
    return answer


def create_circuit(num_qubits: int, num_classical_bits: int = None) -> QuantumCircuit:
    """Creates a quantum circuit
    
    Input:
        num_qubits: Number of qubits
        num_classical_bits: Number of classical bits. Defaults to num_qubits

    Output:
        Quantum circuit
    """

    if num_classical_bits is None:
        num_classical_bits = num_qubits
    
    return QuantumCircuit(num_qubits, num_classical_bits)


def setup_game(max_attempts: int = MAX_ATTEMPTS):
    """Perform required setup for the game
    
    Input:
        max_attempts: Number of chances that user has to guess the answer
        
    Output:
        answer: Randomly-selected answer for this run of the game
        attempts_list: Stores current game state (state of each attempt)
        game_circuit: Quantum circuit used to encode info regarding each attempt's guesses
    """

    # Randomly select answer
    answer = choose_answer()

    # Store info about each attempt
    attempts_list = []
    for i in range(max_attempts):
        qubit_index = i
        attempts_list.append(Attempt(qubit_index))

    # Setup quantum circuit to encode info regarding the attempts -- specifically, for each attempt, which of its guesses should be used
    game_circuit = create_circuit(max_attempts)

    return answer, attempts_list, game_circuit


# def print_same_line(output_string):
#     """Print output without automatically adding a newline at the end"""
#     print(foutput_string, end='')


def print_guess(guess_string):
    """Print a single guess word, letter by letter. Does not print a newline at the end."""
    for char in guess_string:
        # Pad each character of guess to be two spaces, to align with each character (coloured square) of the colour feedback string which seems to take up two spaces
        print(f'{char:>2}', end='')


def print_guess_feedback(feedback_string, space=SPACE_CHAR, output_prefix=''):
    """Print string of coloured squares, where each coloured square indicates the correctness of the corresponding letter of the guess. Does not print a newline at the end."""
    print(f'{output_prefix}{space*23}{feedback_string}', end='')


def print_unused_attempt(attempt_num, no_guess_string=NO_GUESS_STRING, no_feedback_string=NO_FEEDBACK_STRING, space=SPACE_CHAR):
    """Prints unused attempt (i.e. attempt that user has not got to yet)"""

    # For reasonably consistent output across different platforms, only use spaces, not tabs (as tabs can be rendered differently on different platforms)!
    # Number of spaces in below commands determined experimentally
    print(f'Attempt {attempt_num}:{space*13}', end='')

    # Print placeholder to indicate no guess yet
    print_guess(no_guess_string)
    print()
    # Print placehodler to indicate no guess feedback yet
    print_guess_feedback(no_feedback_string)
    print()


def print_classical_attempt(attempt_num, guess_to_feedback_dict, space=SPACE_CHAR):
    """Prints classical attempt. Assumed to have only one guess"""

    # Number of spaces in below commands determined experimentally
    print(f'Attempt {attempt_num}:{space*13}', end='')

    # Since this is a classical attempt, we know there is only one guess in the dict
    guess, feedback = list(guess_to_feedback_dict.items())[0]
    # Print guess
    print_guess(guess)
    # Print one new line
    # Same as: print('\n', end='')
    print()
    # Print feedback
    print_guess_feedback(feedback)
    print()


def random_number_generator(max, quantum_backend=QUANTUM_BACKEND):
    """Generates a random number from 0 to max (inclusive)"""

    # Number of bits (here, qubits) needed to represent a decimal number (here, max) in binary = floor(log_2(max)) + 1
    # Source: https://www.exploringbinary.com/number-of-bits-in-a-decimal-integer/
    # Note that this formula does NOT work if max = 0, since log_2(0) is not defined!
    #
    # Eg. Let max = 5
    #       5 (in decimal) = 101 (in binary) -> needs 3 bits to represent it
    #       log_2(5) = ~2.32
    #       floor(log_2(5)) = 2
    #       floor(log_2(5)) + 1 = 2 + 1 = 3
    #
    # Eg. Let max = 8
    #       8 (in decimal) = 1000 (in binary) -> needs 4 bits to represent it
    #       log_2(8) = 3
    #       floor(log_2(8)) = 3
    #       floor(log_2(8)) + 1 = 3 + 1 = 4
    if max == 0:
        num_qubits = num_classical_bits = 1
    else:
        num_qubits = num_classical_bits = floor(log2(max)) + 1
    
    random_num_circuit = QuantumCircuit(num_qubits, num_classical_bits)

    # Put all qubits into superposition
    random_num_circuit.h(range(num_qubits))
    
    # Measure all qubits
    random_num_circuit.measure_all(add_bits=False)

    # NOTE: The above circuit will NOT necessarily respect max!
    # Eg. If max = 4, it needs 3 qubits to be represented. However, a 3-qubit circuit with all qubits in superposition can produce ANY number from 0 to ((2^3) - 1) = from 0 to 7!
    # Thus, even though max is 4, our circuit may generate a number greater than 4!
    # Thus, need to check if that has happened and, if so, keep re-running the circuit until we get a number <= max
    
    random_decimal_num = max + 1
    while random_decimal_num > max:
        # Execute circuit
        job = execute(random_num_circuit, backend=quantum_backend, shots=1)
        result = job.result()
        counts = result.get_counts(random_num_circuit)
        # Since we only ran one shot above, we already know that we only have one measured value
        # Eg. '101'
        random_binary_num_string = list(counts.keys())[0]
        # Eg. 5
        random_decimal_num = int(random_binary_num_string, base=2)
    
    return random_decimal_num


def print_quantum_attempt(attempt_num, guess_to_feedback_dict, feedback_display_list, space=SPACE_CHAR, reset_cursor_char=RESET_CURSOR_CHAR):
    """Prints quantum attempt. Assumed to have two guesses"""

    # Number of spaces in below commands determined experimentally
    print(f'Attempt {attempt_num}:{space*6}', end='')

    # Since this is a quantum attempt, we know there are multiple guesses in the dict
    guesses = guess_to_feedback_dict.keys()
    feedback_list = list(guess_to_feedback_dict.values())

    # Print guesses
    for guess_index, guess in enumerate(guesses):
        # Print separator before every guess, except the first (0th index)
        if guess_index != 0:
            print(f'{"|":>3} ', end='')
        print_guess(guess)
    
    # After all guesses have been printed on the same line, go to the next line
    print()

    # Print feedback strings

    # Unlike guesses, which are always displayed in order of entry, feedback for a superposition of guesses is intentionally displayed in a RANDOM order

    # For efficiency, only generate this random order once per quantum attempt -- i.e. if we've already come up with a random display order for a quantum attempt, don't bother doing so again
    if feedback_display_list is None:

        # A separate list consisting of the same feedback strings as feedback_list, but in random order -- this list will be used only for DISPLAYING the feedback
        feedback_display_list = []

        # Randomly select first feedback from feedback_list
        #! NOTE: We assume here that the superposition consists of only 2 guesses, which implies that there are only 2 feedback strings in feedback_list, which implies that the only valid list indices are 0 and 1
        #! TODO: Ideally, this code should be able to handle feedback_list of any size
        random_feedback_list_index = random_number_generator(max=1)

        feedback_display_list.append(feedback_list[random_feedback_list_index])
        # If: 
        #   random_feedback_list_index = 0 -> remaining_feedback_list_index = 1
        #   random_feedback_list_index = 1 -> remaining_feedback_list_index = 0
        remaining_feedback_list_index = 1 - random_feedback_list_index
        feedback_display_list.append(feedback_list[remaining_feedback_list_index])

    # Finally, print the feedback strings once separately, above each other
    # This is a static way of conveying that the feedback strings are in superposition
    for feedback_index, feedback in enumerate(feedback_display_list):
        # Print separator above every feedback string, except the first (0th index)
        if feedback_index != 0:
            print(f'{space*23}-----------')
        print_guess_feedback(feedback)
        print()

    return feedback_display_list


def print_game_state(attempts_list: list[Attempt], word_length: int = WORD_LENGTH, max_attempts: int = MAX_ATTEMPTS, attempt_types: AttemptType = AttemptType) -> None:
    """Print out all the attempts, including any guesses the user might have made in those attempts and their associated feedback
    
    Input:
        attempts_list: List of all attempts, both used and unused
        word_length: Number of letters that the answer contains and, thus, that every guess has to contain
        max_attempts: Number of chances that user has to guess the answer
        attempt_types: Enum containing the various attempt types

    Output:
        None
    """
    
    # Clear previous output
    # Experimentally, setting 'wait' to True (which delays clearing old output till new output is available to replace it) seems to be a little smoother visually, since you're less likely to see the flash of blank screen between old output being cleared and new output being printed
    clear_output(wait=True)

    print('Welcome to Quantum Wordle!')
    print(f'Can you guess the mystery {word_length}-letter word in {max_attempts} attempts or less?')

    for attempt_index, attempt in enumerate(attempts_list):
        
        attempt_num = attempt_index + 1
        guess_to_feedback_dict = attempt.guess_to_feedback_dict
        attempt_type = attempt.type

        # Add new line before every attempt
        print()

        # User hasn't gotten to this attempt yet
        if attempt_type is None:
            print_unused_attempt(attempt_num)

        # Classical attempt
        elif attempt_type is attempt_types.CLASSICAL:
            print_classical_attempt(attempt_num,guess_to_feedback_dict)
        
        # Quantum attempt
        else:
            attempt.feedback_display_list = print_quantum_attempt(attempt_num, guess_to_feedback_dict, attempt.feedback_display_list)


def get_guess_feedback(guess_str: str, answer_str: str, word_length: int = WORD_LENGTH, right_guess_feedback_string: str = RIGHT_GUESS_FEEDBACK_STRING) -> str:
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
        return right_guess_feedback_string
    
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


def test_get_guess_feedback():
    """Used to quickly test get_guess_feedback()"""

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
        actual_colour_feedback_str = get_guess_feedback(guess_str, answer_str)
        if actual_colour_feedback_str == expected_colour_feedback_str:
            print('Pass')
        else:
            print('Fail!')
            print('\tGuess:\t\t{}'.format('\t'.join(guess_str)))
            print('\tAnswer:\t\t{}'.format('\t'.join(answer_str)))
            print('\tExpected:\t{}'.format('\t'.join(expected_colour_feedback_str)))
            print('\tActual:\t\t{}'.format('\t'.join(actual_colour_feedback_str)))

# # Uncomment to run test suite
# test_get_guess_feedback()


def encode_quantum_attempt(current_attempt: Attempt, game_circuit: QuantumCircuit) -> None:
    """Encode quantum attempt on underlying quantum circuit. Assumes that the quantum attempt consists of only 2 guesses"""

    #! Note: This assumes that the quantum attempt consists of only 2 guesses!
    # To indicate that we are using two guesses (guess #0 and guess #1) at the same time in this quantum attempt, put the corresponding qubit into a superposition of the |0> and |1> states
    game_circuit.h(current_attempt.qubit_index)


def measure_circuit(game_circuit: QuantumCircuit, attempts_list: list[Attempt], num_attempts: int = MAX_ATTEMPTS, attempt_types: AttemptType = AttemptType) -> QuantumCircuit:
    """Measure all qubits, collapsing any that are in superposition to a classical value. Update any of the corresponding attempts that are quantum to classical
    
    Input:

    
    Output:
        New game circuit, reflecting game state post-measurement
    """
    
    # Add measurement
    game_circuit.measure_all(add_bits=False)

    # Execute circuit
    backend = Aer.get_backend('qasm_simulator')
    job = execute(game_circuit, backend=backend, shots=1)
    result = job.result()
    counts = result.get_counts(game_circuit)
    # Since we only ran one shot above, we already know that we only have one measured value. Specifically, that value is a single string containing the values (0/1) of every qubit in the circuit after measurement
    # Eg. '001101', where the the rightmost char ('1') refers to qubit 0 (attempt 1) and the leftmost char ('0') refers to qubit 5 (attempt 6)
    measured_qubit_values_string = list(counts.keys())[0]

    # Although we measured all qubits, we really only care about the qubits that were in superposition (i.e. the qubits that correspond to quantum attempts)
    # The qubits corresponding to classical attempts had no gates applied to them and, thus, should still be in their default |0> state
    for attempt in attempts_list:
        if attempt.type is attempt_types.QUANTUM:

            # Get value that corresponding qubit collapsed to after measurement
            # Note that, for example, qubit 0 will correspond to the last (rightmost) char in measured_qubit_values_string -- i.e. the char at index `-(0 + 1)` = `-1`
            qubit_value = int(measured_qubit_values_string[-(attempt.qubit_index + 1)])
            
            # Given a list of multiple guesses currently associated with this attempt, qubit_value gives us the index of the single guess that we should use going forward (discarding the others)
            current_guess_list = list(attempt.guess_to_feedback_dict.keys())
            # Randomly chosen (via superposition collapse) guess that, going forward, will be the ONLY guess associated with this attempt
            chosen_guess: str = current_guess_list[qubit_value]
            # Feedback associated with randomly chosen guess
            # Note that chosen_guess_feedback is NOT independently chosen -- it is always the feedback associated with chosen_guess!
            chosen_guess_feedback: str = attempt.guess_to_feedback_dict[chosen_guess]
            # Overwrite existing guess_to_feedback dict for this attempt to consist of just this new guess
            attempt.guess_to_feedback_dict = {chosen_guess: chosen_guess_feedback}

            # Finally, update the attempt type, now that:
            #   The corresponding qubit's superposition has been collapsed to a single classical value
            #   The list of multiple guesses associated with this attempt has been reduced to a single guess
            attempt.type = attempt_types.CLASSICAL

    # At this point, all quantum attempts have been converted to classical attempts and each of their associated guess lists has been reduced to a single guess

    # There doesn't seem to be a way to just continue a previous circuit execution -- instead, every execution starts over from the very beginning. This means that, if we continue reusing the same circuit for all executions, it will have multiple measurements (where all but the latest are redundant), we will be putting qubits that represent FORMERLY quantum attempts back into superposition needlessly and we will have to worry about potential complications caused by those unnecessary superpositions (that we already measured in a previous circuit execution) collapsing to a different value this time.
    # Thus, instead, for simplicity, we just create a brand new circuit for execution next time -- formerly quantum attempts that are now classical attempts will remain classical in this new circuit (their qubits will not have any gates applied to them)
    new_game_circuit = create_circuit(num_attempts)
    return new_game_circuit


def did_user_guess_answer(classical_attempts_list: list[Attempt], answer):
    """Given a list of classical attempts, check if any of the guesses made by the user in those attempts was correct (i.e. matched the answer)
    
    Input:
        classical_attempts_list: List of attempts made by the user. Assumes all attempts in the list are classical

    Output:
        True/False, depending on whether any of the user's guesses was correct or not
    """

    for attempt in classical_attempts_list:
        # Since all attempts in the list are assumed to be classical, we can also assume that they only have 1 guess each
        guess = list(attempt.guess_to_feedback_dict.keys())[0]
        if guess == answer:
            return True
        
    # If we get to this point, it means none of the attempts were successful
    return False


def print_success_message(answer: str) -> None:
    """Print success message
    
    Input:
        answer: The correct answer
    """
    print(f'\nCongratulations!! You correctly guessed that the mystery word was "{answer}"!')


def print_game_result(user_guessed_answer: bool, answer: str) -> None:
    """Print either a success or failure message, depending on whether the user correctly guessed the answer or not
    
    Input:
        user_guessed_answer: Boolean (True/False) indicating whether the user correctly guessed the answer or not
        answer: The correct answer

    Output:
        None
    """
    if user_guessed_answer:
        print_success_message(answer)
    else:
        print(f'\nThe mystery word was "{answer}" -- better luck next time!')


def run_game(classical_attempt_option=CLASSICAL_ATTEMPT_OPTION, quantum_attempt_option=QUANTUM_ATTEMPT_OPTION, measure_option=MEASURE_OPTION, exit_option=EXIT_OPTION, num_guesses_in_superposition=NUM_GUESSES_IN_SUPERPOSITION, max_attempts: int = MAX_ATTEMPTS, attempt_types: AttemptType = AttemptType) -> None:
    """Run game
    
    Input:
        max_attempts: Maximum number of attempts that user has to guess the answer
    
    Output:
        None
    """

    answer, attempts_list, game_circuit = setup_game()
    
    # Keeps track of whether the user entered an invalid choice in the previous iteration of the below loop
    user_entered_invalid_choice = False

    # Index of the final attempt
    final_attempt_index = max_attempts - 1
    # Index of next/first available attempt
    # Eg. Attempt 1 is located at index 0
    next_available_attempt_index = 0

    while True:

        print_game_state(attempts_list)
        
        if next_available_attempt_index <= final_attempt_index:
            # There is still at least one attempt available to use, so retrieve it
            next_available_attempt = attempts_list[next_available_attempt_index]
            # User can choose what to do as long as they haven't run out of attempts
            print('\nSelect an option by entering the corresponding number:')
            print(f'{classical_attempt_option}: Classical attempt (1 guess)')
            print(f'{quantum_attempt_option}: Quantum attempt (superposition of 2 guesses)')
            print(f'{measure_option}: Measure all quantum attempts (collapse to classical)')
            print(f'{exit_option}: Exit')

            # There appears to be a longstanding Jupyter notebook bug where input prompt occasionally does not appear (seemingly because previous output is printed out of order and overwrites it), which means that the code is stuck waiting for input that user cannot provide. In particular, appears to only occur at this point in code, possibly because of large quantity of output being printed above right before asking for input below, repeatedly (in a loop)
            # After lot of research and experimentation, the combination of adding a delay and flushing pending output before asking for input seems to prevent that bug from being triggered
            # This delay was experimentally determined to be pretty reliable
            sleep(0.16)
            print(end='', flush=True)
            
            # After printing above options, print error message if user previously made an invalid choice
            if user_entered_invalid_choice:
                user_entered_invalid_choice = False
                print('\nInvalid choice! Please choose one of the available options')
            user_choice = safe_input('--> ')

        else:
            # At this point, user has used up all attempts
            # Reset to avoid confusion from previous value of user choice
            user_choice = None
            # If any of the attempts are still quantum (i.e. are still in superposition), measure them automatically
            for attempt in attempts_list:
                if attempt.type is attempt_types.QUANTUM:
                    user_choice = measure_option
                    break
            # None of the attempts are still quantum
            if user_choice is None:
                # Check if the user guessed the answer in any of the attempts
                # This includes the following scenarios, for each attempt:
                #   - The user originally made a classical attempt, containing one guess, and that guess was correct
                #   - The user originally made a qauntum attempt, containing 2 guesses, one of which was correct, and after we measured the quantum attempt, the single guess it collapsed to happened to be the correct one
                user_guessed_answer = did_user_guess_answer(attempts_list, answer)
                # Print either success or failure message
                print_game_result(user_guessed_answer, answer)
                break
        
        if user_choice == classical_attempt_option:

            # Take next available attempt off the list and use it up -- will not be available for next iteration
            current_attempt = next_available_attempt
            next_available_attempt_index += 1

            current_attempt.type = attempt_types.CLASSICAL

            guess = safe_guess_input('Enter guess: ')
            # Even if the guess is correct, we want to get and store its feedback so we can display it
            current_attempt.guess_to_feedback_dict[guess] = get_guess_feedback(guess, answer)
            # Stop game if the guess is correct
            if guess == answer:
                # Print game state showing correct answer
                print_game_state(attempts_list)
                # Print message
                print_game_result(True, answer)
                break
        
        elif user_choice == quantum_attempt_option:

            # Take next available attempt off the list and use it up -- will not be available for next iteration
            current_attempt = next_available_attempt
            next_available_attempt_index += 1

            current_attempt.type = attempt_types.QUANTUM

            # guess_num goes from 1 to num_guesses_in_superposition
            for guess_num in range(1, num_guesses_in_superposition + 1):
                # If user guesses the same word multiple times in their quantum attempt, that causes issues since the rest of the code reasonably assumes that a quantum attempt always has num_guesses_in_superposition DIFFERENT guesses -- thus, do not accept duplicate guesses (in the same quantum attempt -- it's okay if different attempts have the same guess)
                while True:
                    guess = safe_guess_input(f'Enter guess {guess_num}: ')
                    if guess in current_attempt.guess_to_feedback_dict:
                        print('Duplicate guess! Please enter a different word')
                    else:
                        current_attempt.guess_to_feedback_dict[guess] = get_guess_feedback(guess, answer)
                        break
                # Note: Even if one of the guesses is correct, since it's in a superposition (and thus the user has uncertainty as to exactly WHICH guess is correct), we do NOT stop the game
            
            encode_quantum_attempt(current_attempt, game_circuit)

        elif user_choice == measure_option:

            # Note that this choice does NOT use up an attempt!

            # Measure all attempts
            game_circuit = measure_circuit(game_circuit, attempts_list)
            
            # Now that all quantum attempts made so far have been collapsed to classical attempts, check to see if any of them happened to have collapsed to the right answer
            # Since game isn't over yet, only print game result and exit if one of the user's quantum attempts collapsed to the correct answer (i.e. if user guessed correct answer early) -- if not, continue game
            previous_attempt_index = next_available_attempt_index - 1
            # Only check the list of attempts made SO FAR (index 0 to previous_attempt_index) -- no point in checking unused attempts. Also, did_user_guess_answer() only accepts classical attempts, not unused attempts
            if did_user_guess_answer(attempts_list[:(previous_attempt_index+1)], answer):
                # Show game state after measurement/collapse
                print_game_state(attempts_list)
                # Print success message
                print_success_message(answer)
                # Exit early
                break

        elif user_choice == exit_option:
            print('Exiting ...')
            # Note: Neither `sys.exit()` nor `exit()` appears to gracefully exit the Jupyter notebook -- instead, they both crash the kernel, so do not use them here!
            break

        # Invalid choice
        else:
            user_entered_invalid_choice = True

# ! DEBUG
# run_game()