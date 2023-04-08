- Quantum Tic Tac Toe design, for reference:
    - Each of the 9 squares is represented by a qubit
    - Qubit in state `|0>` represents letter `O`, qubit in state `|1>` represents letter `X`
        - Looks like this is the case even if a classical move is used (which technically doesn't *need* to be stored on a qubit)
    - When player chooses to entangle two spots, the underlying qubits are entangled
        -In this case, they are both in superposition of `|0>`/`|1>`, but entangled in such a way that they always disagree with each other
    - When player chooses to measure board, all qubits are measured (only 1 shot)
        - For each qubit that was in superposition, its spot in board is designated `O` or `X` depending on whether the measurement collapsed it to `|0>` or `|1>`
        - If game gets to the end (board is filled up) and there are still un-measured superpositions, they are automatically measured
        - Regardless of whether user chooses to measure or board automatically measures because game got to the end, it doesn't print any message that it's doing so -- at least, none that is visible before the output is cleared and the measured game board is displayed
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
        - Number of qubits needed depends on the number of choices we're randomly choosing between -- specifically, it is the number of bits required to encode a binary number from 0 to (num_choices - 1) -- i.e. it is ~log_2(num_choices)  
        Eg. If we need to randomly pick one of 8 choices, we can represent their zero-based indexes (0 - 7) in binary as 000 - 111, which requires 3 bits. Thus, we create a circuit containing 3 qubits, put each qubit in a superposition of `|0>` and `|1>`, and then measure all the qubits -- depending on how each of the three qubits collapses to either `|0>` and `|1>`, we'll get a binary number from 000 - 111, which tells us which of the 8 choices has been chosen.
        - Alternatively, see if there is an existing Qiskit library that does this for us
            - Surprisingly, looks like there isn't!
    
    - Printing out colour feedback for superposition of 2 words:
        - Put words vertically on top of each other
            - Each letter separated by a tab, to ensure we can put two colours below its "column" if necessary?
        - Print out colours horizontally, such that all the colours on the left correspond to *one* of the words (randomly selected) and the colours on the right correpsond to the other one
            - The different orientation should already convey that there isn't a guaranteed correspondence between word on top and colours on left but, to make it even clearer, maybe have the left and right colours swap places a few times before settling down?
    - Printing colour feedback:
        - Easiest approach is not to try and create custom images, but instead just print existing Unicode emojis for green square and yellow square. Unfortunately, there doesn't appear to be a grey square (which would match classical Wordle's colour scheme for wrong letter) so use red square instead.

    - Answer selection:
        - Classical Wordle takes answer from answer list in order
            - Actually, since Nov 7, 2022, there is no hardcoded answer list -- the NYT manually picks an answer every day. There is still a guess list though
        - Classical Wordle only selects 1 answer per day
        - Since mine is a demonstration, it should NOT be tied to the same word per day. Also, since my answer list (unlike original one from Wordle) is in alphabetical order, no fun if I go in order -- thus, pick a new answer at random every time the game is executed

    - Exiting game:
        We stop running game only under following circumstances:
            - It's a CLASSICAL attempt and the guess is right (i.e. guess = answer)
            - User chose to measure all quantum attempts made so far and one of them collapsed to classical attempt with the right guess
            - All 6 attempts have been used up
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

        - Wordle shows not only which letters are left (available), but also which are right/wrong. Since I have less space in my Jupyter notebook output, consider only showing the letters that are left. This is because then we only have to display letters -- if we also want to indicate which letters are right/wrong, we need extra rows of colour squares below each row of letters
            - Note: I have browser zoom set to 125% for IBM Quantum Lab -- try with default 100%, since that is what average person will probably be using

- Jupyter input prompt bug:
    - One trigger seems to be combination of `clear_output()` and `input()`, which I resolved by flushing previous output before calling input
    - However, there appear to be other triggers that are not fixed:
        - Adding a delay (via `sleep()`)
        - Some combination of the kernel exiting improperly (including me calling `sys.exit()`) and having the input prompt be off-screen when I run cell
            - Restarting kernel seems to temporarily resolve this trigger
    - Assuming that above reoslution (flush) did not fully fix issue, also added delay of 0.2s in addition to flush -- big improvement
    - Instead of delaying every input, focusing on the user choice input since that's where the issue consistently triggers, not the other inputs
        - Difference is that this input has a lot of output printed before it
            - Try replacing multiple small print() with one big print()
                - If anything, made it worse :(
            - Remove flush and delay from input function
                - Put only flush after big output block (before user choice input)
                    - Didn't seem to have much effect
                - Removed flush and put sleep after big output block
                    - Big improvement, but not perfect -- can still trigger bug by repeatedly inputting 3 in user choice input, for example
                        - In retrospect, this might not be the best test, since it seems like this is more testing whether the browser can render input prompt faster than I can hit Enter + 3, rather than testing whether it renders an input prompt at all
                        - Instead, just run the program a few times and, each time, use the program normally and see if the input prompt vanishes, since that's what the average user will be doing
                        - Alternatively, scrolling up so that code cell is at bottom of screen and output is off screen and THEN running code cell, pressing 4 to exit and then scrolling up again to start over seems to also be a good way to trigger missing input prompt bug
                            - Doing this ~30 times in a row seems fairly reliable at seeing if the bug will arise or not
                - Remove flush and sleep, and instead modify all the print statements in big output block to flush
                    - Like when we added only sleep after big output block, big improvement. However:
                        - Visually looks very choppy -- cell below keeps briefly coming up then going back down
                        - Still able to eventually trigger bug by choosing measure option over and over again
                            - Again, seems like this is testing the wrong thing in retrospect
                    - Try only flushing last print of output block?
                        - Terrible, no effect
                - Try both sleep and then flush after big output block
                    - Really good! Could not trigger bug, even when scrolling so that cell output is off screen!!
                    - Visually, the 0.2s delay seems notiecable though -- experiment with shorter delays to find sweet spot (?)
