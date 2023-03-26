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

        # Assuming word_length = 5:
        # [None, None, None, None, None]
        colour_feedback_list = [None for i in range(word_length)]

        # NOTE: If there are repeated letters in either guess or answer, looking for a match (for each letter of guess) by iterating over answer from left to right is NOT guaranteed to work!
        # Eg. Let guess be 'CABAL' and 
        #        answer be 'ABBEY':
        #     In this case, if we do left to right evaluation of answer, we will compare the 'B' in 'CABAL' to the 1st 'B' in 'ABBEY' and say that it is the right letter but the wrong position.
        #     However, the correct answer is to say that, since the 'B' in 'CABAL' matches the 2nd 'B' in 'ABBEY', it is actually both the right letter and the right position!

        # Check for right letter and right position matches
        # Note: 
        #   - We check this condition first, since this dominates in case of repeated guess letters (see example above)
        #   - Although not strictly necessary (since we're not changing the length of the answer_char_list, just its current element), to be safe, we iterate over a COPY of answer_char_list rather than the original answer_char_list itself (which is what we're changing during the iteration)
        for index, guess_char, answer_char in zip(range(word_length), guess_char_list, answer_char_list[:]):
            if guess_char == answer_char:
                colour_feedback_list[index] = RIGHT_LETTER_RIGHT_SPOT_COLOUR
                # Now that a char in answer has been matched by a char in guess, remove that char from answer (specifically, to avoid changing the length of answer_char_list, replace it with None since that's guaranteed not to match any letter) so that other chars in guess don't accidentally match it
                answer_char_list[index] = None

        # At this point, we've identified all the letters of the guess that are both the right letter and in the right position
        # The remaining letters are either the right letter but in the wrong position, or just the wrong letter
        # At this point, iterating over answer from left to right WILL give us the right answer
        # Eg. Let guess be 'EERIE' and
        #        answer be 'TENET'
        #     In this case, assuming we previously found that the 2nd 'E' in 'EERIE' was both the right letter and in the right position, now we would expect to mark the 1st 'E' as being the right letter but in the wrong position (compared to the 2nd 'E' in 'TENET'), and the 3rd 'E' as being the wrong letter (no corresponding letter in 'TENET') -- i.e. after the 2nd 'E' in the guess is perfectly matched above, the LEFTMOST remaining 'E' in the guess is compared with the corresponding letter in the answer before the more rightward remaining 'E' in the guess.

        # For efficiency, only check the guess letters whose correctness is still unknown
        for guess_index, guess_char in enumerate(guess_char_list):
            # Correctness of this guess letter is still unknown
            if colour_feedback_list[guess_index] is None:
                guess_char_in_answer = False
                # Can safely compare against every letter in answer, since the answer letters that were previously matched above have been replaced with None, which is guaranteed not to match any letter in guess
                for answer_index, answer_char in enumerate(answer_char_list[:]):
                    # Guess letter is in the answer, but we already know it's in the wrong position (since otherwise we would have matched it above)
                    if guess_char == answer_char:
                        guess_char_in_answer = True
                        colour_feedback_list[guess_index] = RIGHT_LETTER_WRONG_SPOT_COLOUR
                        # Again, replace the matched answer_char with None so it doesn't accidentally get matched again by another (duplicate) guess letter
                        answer_char_list[answer_index] = None
                # At this point, have checked guess_char against every letter in answer -- if we still haven't found a match, then guess_char is simply the wrong letter
                if not guess_char_in_answer:
                    colour_feedback_list[guess_index] = WRONG_LETTER_COLOUR




        # # Compare each char of guess against each char in answer
        # for guess_index, guess_char in enumerate(guess_char_list):
        #     guess_char_in_answer = False
        #     for answer_index, answer_char in enumerate(answer_char_list):
        #         # Guess char is in answer, but don't yet know if it's also in the right position or not
        #         if guess_char == answer_char:
        #             guess_char_in_answer = True
        #             # Guess char is in the correct position
        #             if guess_index == answer_index:
        #                 colour_feedback_list.append(RIGHT_LETTER_RIGHT_SPOT_COLOUR)
        #             # Guess char is in the wrong position
        #             else:
        #                 colour_feedback_list.append(RIGHT_LETTER_WRONG_SPOT_COLOUR) 
                    
        #             #! TODO: Figure out how to deal with repeat letters
        #             # Now that one of the chars in answer has been matched by a char in guess, remove that answer char so that it can't get wrongly matched again by another (duplicate) guess char
                    

        #             # Now that we found a match for guess_char, stop searching answer
        #             break

        #         else:
        #             next_answer_char_list.append(answer_char)
            
        #     # After iterating through all the letters in answer, if we still haven't found a match, then we know guess_char is not in the answer and, thus, is the wrong letter
        #     if not guess_char_in_answer:
        #         colour_feedback_list.append(WRONG_LETTER_COLOUR)

        # Now that we've assembled the colour feedback list for all the letters in the guess word, convert it from list to string
        colour_feedback_str = ''.join(colour_feedback_list)
    
    return colour_feedback_str