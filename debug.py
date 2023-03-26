# Every answer and guess has to contain this many letters
WORD_LENGTH = 5

# Colour Feedback chars
RIGHT_LETTER_RIGHT_SPOT_COLOUR = '🟩'
RIGHT_LETTER_WRONG_SPOT_COLOUR = '🟨'
WRONG_LETTER_COLOUR = '🟥'

def get_colour_feedback(guess_str, answer_str, word_length=WORD_LENGTH):
    """ Compares the guess with the answer and returns colour feedback indicating how close the guess was.

    Input:
        - guess_str: Guess word input by the user
        - answer_str: Answer word
        Note: 
            - Assumes both input strings are the same 'case', so they can be compared
            - Assumes both input strings consist of word_length characters

    Output:
        Returns a string consisting of five coloured boxes, where each box indicates the correctness of the corresponding letter of the guess word
    """
    if guess_str == answer_str:
        # Assuming word_length = 5 and RIGHT_LETTER_RIGHT_SPOT_COLOUR = '🟩':
        # '🟩🟩🟩🟩🟩'
        colour_feedback_str = word_length * RIGHT_LETTER_RIGHT_SPOT_COLOUR
    
    else:

        # Convert both guess and answer from string to list
        guess_char_list = list(guess_str)
        answer_char_list = list(answer_str)
        
        #! DEBUG
        # # Assuming word_length = 5 and WRONG_LETTER_COLOUR = '🟥':
        # # ['🟥', '🟥', '🟥', '🟥', '🟥']
        # colour_feedback_list = [word_length * WRONG_LETTER_COLOUR]
        #
        # Assuming word_length = 5:
        # [None, None, None, None, None]
        colour_feedback_list = [None for i in range(word_length)]

        # NOTE: If there are repeated letters in either guess or answer, looking for a match (for each letter of guess) by iterating over answer from left to right is NOT guaranteed to work! 
        # Eg. Let guess be 'CABAL' and 
        #        answer be 'ABBEY':
        #     In this case, if we do left to right evaluation of answer, we will compare the 'B' in 'CABAL' to the 1st 'B' in 'ABBEY' and say that it is the right letter but the wrong position.
        #     However, the correct answer is to say that, since the 'B' in 'CABAL' matches the 2nd 'B' in 'ABBEY', it is actually both the right letter and the right position!

        # Check for right letter and right position matches
        # Note that we iterate over a COPY of answer_char_list, rather than the actual answer_char_list itself, so that we can safely modify answer_char_list during the iteration
        for index, guess_char, answer_char in zip(range(word_length), guess_char_list, answer_char_list[:]):
            if guess_char == answer_char:
                colour_feedback_list[index] = RIGHT_LETTER_RIGHT_SPOT_COLOUR
                # Now that a char in answer has been matched by a char in guess, remove that char from answer so that other chars in guess don't accidentally match it
                answer_char_list.pop(index)

        # At this point, the elements of colour_feedback_list are either None or RIGHT_LETTER_RIGHT_SPOT_COLOUR
        # For efficiency, only check the guess letters whose correctness is still unknown
        

        # Compare each char of guess against each char in answer
        for guess_index, guess_char in enumerate(guess_char_list):
            guess_char_in_answer = False
            for answer_index, answer_char in enumerate(answer_char_list):
                # Guess char is in answer, but don't yet know if it's also in the right position or not
                if guess_char == answer_char:
                    guess_char_in_answer = True
                    # Guess char is in the correct position
                    if guess_index == answer_index:
                        colour_feedback_list.append(RIGHT_LETTER_RIGHT_SPOT_COLOUR)
                    # Guess char is in the wrong position
                    else:
                        colour_feedback_list.append(RIGHT_LETTER_WRONG_SPOT_COLOUR) 
                    
                    #! TODO: Figure out how to deal with repeat letters
                    # Now that one of the chars in answer has been matched by a char in guess, remove that answer char so that it can't get wrongly matched again by another (duplicate) guess char
                    

                    # Now that we found a match for guess_char, stop searching answer
                    break

                else:
                    next_answer_char_list.append(answer_char)
            
            # After iterating through all the letters in answer, if we still haven't found a match, then we know guess_char is not in the answer and, thus, is the wrong letter
            if not guess_char_in_answer:
                colour_feedback_list.append(WRONG_LETTER_COLOUR)

        # Now that we've assembled the colout feedback for all the letters in the guess word, convert it from list to string
        colour_feedback_str = ''.join(colour_feedback_list)
    
    return colour_feedback_str