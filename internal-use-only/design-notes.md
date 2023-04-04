- Quantum Tic Tac Toe design, for reference:
    - Each of the 9 squares is represented by a qubit
    - Qubit in state `|0>` represents letter `O`, qubit in state `|1>` represents letter `X`
        - Looks like this is the case even if a classical move is used (which technically doesn't *need* to be stored on a qubit)
    - When player chooses to entangle two spots, the underlying qubits are entangled
        -In this case, they are both in superposition of `|0>`/`|1>`, but entangled in such a way that they always disagree with each other
    - When player chooses to measure board, all qubits are measured (only 1 shot)
        - For each qubit that was in superposition, its spot in board is designated `O` or `X` depending on whether the measurement collapsed it to `|0>` or `|1>`
        - If game gets to the end (board is filled up) and there are still un-measured superpositions, they are automatically measured
    - Note: Uses `from IPython.display import clear_output; clear_output(wait=False)` to replace previous output!

- Wordle:
    - Need to guess a 5-letter word in 6 tries

- Quantum Wordle design:
    - Each row/turn/attempt has (in this quantum version) up to *two* words associated with it
    - Each row is represented by 1 qubit -- thus, number of qubits needed is 6
        - Reminder: When quantum circuit has multiple qubits, when they're measured, the values are not reported separately! Instead, they are measured as one big binary string (eg. `010001`) -- thus, I would need to precisely keep track of which char/bit refers to which attempt when retrieveing measurement result
            - Having separate 1-qubit circuit for each attempt would make this simpler
            - However, conceptually might make sense to group all the qubits that are serving same purpose in same circuit
                - Also, measuring all qubits becomes a pain with multiple circuits since need to measure each 1-qubit circuit individually
    - The "classic" case is when the row has only one guess associated with it, represented by the qubit being in state `|0>`
    - The "quantum" case is when the row has two guesses associated with it, repesented by the qubit being in a superposition of `|0>` and `|1>` (eg. `|+>`). As long as the qubit is in superposition, the colour feedback is displayed for both guesses/words simultaneously, although it's unknown which word each feedback is for.
        - When the board is measured, which can be done by user at any time, all superpositions created so far (rows with two words each) are measured, and each row now only displays 1 word and the feedback for that word -- however, *which* of the two words gets chosen to be the final word for that row is determined by whether the qubit for that row collapsed to either `|0>` (first word) or `|1>` (second word)

    - Separately, every time our code needs to make a random choice (randomly pick a solution from the solutions list, randomly choose which of the two words' colour feedback gets displayed first), we make that choice using a separate quantum circuit
        - Number of qubits needed dependes on the number of choices we're randomly choosing between -- specifcally, it is the number of bits required to encode a binary number from 0 to (num_choices - 1) -- i.e. it is ~log_2(num_choices)  
        Eg. If we need to randomly pick one of 8 choices, we can represent their zero-based indexes (0 - 7) in binary as 000 - 111, which requires 3 bits. Thus, we create a circuit containing 3 qubits, put each qubit in a superposition of `|0>` and `|1>`, and then measure all the qubits -- depending on how each of the three qubits collapses to either `|0>` and `|1>`, we'll get a binary number from 000 - 111, which tells us which of the 8 choices has been chosen.
        - ALternatively, see if there is an existing Qiskit library that does this for us
    
    - Printing out colour feedback for superposition of 2 words:
        - Put words vertically on top of each other
            - Each letter separated by a tab, to ensure we can put two colours below its "column" if necessary?
        - Print out colours horizontally, such that all the colours on the left correspond to *one* of the words (randomly selected) and the colours on the right correpsond to the other one
            - The different orientation should already convey that there isn't a guaranteed correspondence between word on top and colours on left but, to make it even clearer, maybe have the left and right colours swap places a few times before settling down?
    - Printing colour feedback:
        - Easiest approach is not to try and create custom images, but instead just print existing Unicode emojis for green square and yellow square. Unfortunately, there doesn't appear to be a grey square (which would match classical Wordle's colour scheme for wrong letter) so use red square instead.

    - Answer selection:
        - Classical Wordle takes answer from answer list in order
        - Classical Wordle only selects 1 answer per day
        - Since mine is a demonstration, it should NOT be tied to the same word per day. Also, since my answer list (unlike original one from Wordle) is in alphabetical order, no fun if I go in order -- thus, pick a new answer at random every time the game is executed

    - Exiting game:
        We stop running game only under following circumstances:
            - It's a CLASSICAL attempt and the guess is right (i.e. guess = answer)
            - User chose to measure all quantum attempts and one of them collapsed to classical attempt with the right guess
            - All 6 attempts have been used up, any quantum attempts have been measured and resulting classical attempts did not have right guess
            - User chose to exit
    
    - Displaying available letters
        - Goal is to reproduce Wordle's feature where it shows, at bottom of page, which letters you've used and which are left
        - Initial idea was to use Unicode strikthrough combining character, but effect is not that clear
        - Instead, perhaps best to just have gap replacing used-up letter
        
        - What logic does Wordle use when changing it?
            - Looks like Wordle always changes letter colours to reflect the most certainty we have about it
                - All letter backgrounds start off grey
                - If you try a letter and:
                    - It's wrong: Letter background turns black -- never changes again
                    - It's right letter and position: Letter background turns green -- never changes again
                    - It's right letter, but wrong position: Letter background turns yellow. This is the only case where it CAN change again -- if you guess the right position of that letter in a subsequent word, the background colour will change again from yellow to green
