- Quantum Tic Tac Toe design, for reference:
    - Each of the 9 squares is represented by a qubit
    - Qubit in state `|0>` represents letter `O`, qubit in state `|1>` represents letter `X`
    - When player chooses to entangle two spots, the underlying qubits are entangled
        -In this case, they are both in superposition of `|0>`/`|1>`, but entangled in such a way that they always disagree with each other)
    - When player chooses to measure board, all qubits are measured.
        - For each qubit that was in superposition, its spot in board is designated `O` or `X` depending on whether the measurement collapsed it to `|0>` or `|1>`

- Wordle:
    - Need to guess a 5-letter word in 6 tries

- Quantum Wordle design:
    - Each row/turn has (in this quantum version) up to *two* words associated with it
    - Each row is represented by 1 qubit -- thus, number of qubits needed is 6
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