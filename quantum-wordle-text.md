# **Capstone Project: Quantum Wordle**

By **Pranav Marla** (`4181_Marla`)

## **Overview**

This is a fully functioning, playable implementation of a quantum game.
Inspired by the Quantum Tic Tac Toe game introduced in semester 1 lab 11, this is also a quantum spin on a classical game -- specifically, as the name implies, a quantum spin on the game Wordle.

### **(Classical) Wordle**
Developed by Josh Wardle as a gift for his partner before going viral upon its public release in Oct 2021 and eventually being bought by the New York Times for more than $1 million, [Wordle](https://www.nytimes.com/games/wordle/index.html) is a word game that challenges you to guess a mystery five-letter word in six attempts.

Every time you make a guess, you receive a clue in the form of five coloured squares, one per letter, indicating how close/correct each corresponding letter of the guess was.  
Eg. Let's say the answer is *WEARY*.   
If you guess the word *SWORE*, you will receive a clue that looks like this:
```
 S W O R E  
🟥🟨🟥🟩🟨
```

This means:
- *S* is the wrong letter (it's not in the answer)
- *W* is the right letter (it's in the answer), but it's in the wrong spot
- *O* is the wrong letter
- *R* is the right letter *and* it's in the right spot
- *E* is the right letter, but it's in the wrong spot

### **Quantum Wordle**
What I described above is the regular ("classical") Wordle, where your only option is to make what I call a classical attempt: i.e. For each attempt, you can make one guess and you receive one clue corresponding to that guess.

In addition to the classical attempt, I have introduced two more options with some added quantum ✨flair✨:
- **Quantum Attempt:** For each attempt, you can make a superposition of *two* guesses. However, just like a real superposition, the cost of having access to extra states (here, guesses) is that you lose the certainty of a classical state -- in other words, after you make your two guesses, you will receive two clues, but you will *not* know which clue corresponds to which guess!  
Eg. Let's say you choose the quantum attempt option and, in that attempt, you make two guesses: *WEEPY* and *EERIE*. You might receive two clues that look like this:
    ```
    W E E P Y  |  E E R I E
          🟥🟥🟥🟥🟩
          -----------
          🟥🟨🟥🟨🟥
    ```
    Without further information, you *cannot* tell, for example, whether the first clue (🟥🟥🟥🟥🟩) corresponds to *WEEPY* or *EERIE* -- the ordering of the clues is completely random.

- **Measure all quantum attempts:** Just like with a real superposition, if you want full certainty as to its state, all you need to do is measure it. Here, at any point in the game, you can choose to measure all the quantum states have been created so far -- once you do so, each quantum attempt will randomly collapse to a classical attempt. This means that, when you measure your quantum attempt, the game will randomly pick one of its two guesses to collapse to, and will only display that guess and its associated clue.  
Eg. If you chose to measure the above quantum attempt, it might randomly collapse to the following classical attempt:
    ```
     E E R I E
    🟥🟥🟥🟥🟩
    ```
    Now you know with full certainty that the clue 🟥🟥🟥🟥🟩 corresponds to *EERIE* but, of course, you no longer have access to the extra information regarding the guess *WEEPY*.

### **Implementation**
Under the hood, Quantum Wordle is implemented using two separate quantum circuits:

- **Game Circuit:** This is the main circuit underpinning the game, used to encode the attempts. There are six qubits, one per attempt. Each attempt has a *guess list*, storing the various guesses made in that attempt. The state of each qubit is interpreted as a list index, indicating which guess in the corresponding attempt's guess list should be used.  
Specifically:
    - A classical attempt has only one guess, so its guess list will consist of only one guess at index `0`. Thus, the corresponding qubit will be in the `|0>` state, indicating that we should use the guess located at index 0 of the clasical attempt's guess list.
    - A quantum attempt has two guesses, so its guess list will consist of two guesses, at indices `0` and `1` respectively. Thus, the corresponding qubit will be in a *superposition* of the `|0>` and `|1>` states (specifically, the `|+>` state), indicating that we should use the guess located at index 0 *and* the guess located at index 1 of the quantum attempt's guess list.
    - When you choose the *measure all quantum attempts* option, the entire game circuit will be measured. The qubits corresponding to classical attempts will of course be unchanged (will remain in the `|0>` state), but the qubits corresponding to quantum attempts, which were in superposition, will randomly collapse to either `|0>` or `|1>`. We interpret this as the quantum attempt collapsing to a classical attempt, and, depending on whether the qubit collapsed to either `|0>` or `|1>`, select either the guess at index `0` or the guess at index `1` of the formerly quantum attempt's guess list to use going forward -- the other guess is discarded.

    Eg. Let's say, out of the six possible attempts, your second and fifth attempts are quantum attempts. The quantum circuit encoding that information will look like this:
    ```
                ░ ┌─┐               
    q_0: |0>──────░─┤M├───────────────
            ┌───┐ ░ └╥┘┌─┐            
    q_1: |0>┤ H ├─░──╫─┤M├────────────
            └───┘ ░  ║ └╥┘┌─┐         
    q_2: |0>──────░──╫──╫─┤M├─────────
                ░  ║  ║ └╥┘┌─┐      
    q_3: |0>──────░──╫──╫──╫─┤M├──────
            ┌───┐ ░  ║  ║  ║ └╥┘┌─┐   
    q_4: |0>┤ H ├─░──╫──╫──╫──╫─┤M├───
            └───┘ ░  ║  ║  ║  ║ └╥┘┌─┐
    q_5: |0>──────░──╫──╫──╫──╫──╫─┤M├
                ░  ║  ║  ║  ║  ║ └╥┘
    c: 0 6/═════════╩══╩══╩══╩══╩══╩═
                    0  1  2  3  4  5 
    ```


- **Random Number Generator Circuit:** Completely separate from the main game circuit, this circuit is used whenever we need to randomly select one item out of a list of items.  
Specifically:
    - When displaying the two clues for the two guesses in a quantum attempt, this circuit is used to randomly generate a list index that tells us which of the two guesses' clues should be displayed first (on top).
    - At the start of the game, when randomly selecting an answer from the list of possible answers in my code, this circuit is used to randomly generate a corresponding list index.
    
    As you might have guessed from the above examples, the function implementing this circuit (`random_number_generator()`) is able to accommodate different list sizes -- depending on the list size, it dynamically determines how many qubits the circuit requires. Once the circuit has been created, the function puts all the qubits into superposition (`|+>` state), measures all the qubits, interprets the resulting qubit values as a single binary value, converts that binary value to a decimal value and finally interprets that decimal value as a list index telling us which item to pick.  
    Eg.
    - When choosing between two guesses' clues, there are only two options, which means the circuit needs to generate either a 0 or a 1. If we want to represent an arbitrary decimal value (`decimal`) as a binary number, we need `floor(log_2(decimal)) + 1` bits. Thus, to generate a number between 0 and `1`, it is sufficient to create a circuit with  `floor(log_2(1)) + 1 = 1` qubit.
    - When choosing an answer though, since the answer list currently consists of 2309 words, the circuit needs to randomly generate an integer between 0 and `2308`, which means it requires `floor(log_2(2308)) + 1 = 12` qubits.

Now, strictly speaking, this ancillary circuit is not *required* to implement Quantum Wordle but, since I knew I needed a random number generator and I was already on a quantum platform, I decided there was no point in settling for classical *pseudo-randomness* when my quantum resources afforded me access to *true* randomness.  
(That being said, since this code is being run on the *qasm_simulator* backend (a classical simulation of a quantum computer), it is technically still classical and pseudo-random under the hood, but, in theory, the backend can be swapped out to have it run on a real quantum computer).

## **Platform Limitations**
Before running the game, there are a few things to keep in mind:
- This code has only been tested on the IBM Quantum Lab platform -- in particular, it has not been tested on Google Colab.
- There appears to be a longstanding Jupyter notebook bug (see the following links: [1](https://github.com/jupyter/notebook/issues/3159#issuecomment-430085174) [2](https://stackoverflow.com/questions/50439035/jupyter-notebook-input-line-executed-before-print-statement) [3](https://stackoverflow.com/questions/71628971/jupyter-is-busy-stuck-randomly-when-input-is-executed-inside-while-statement) [4](https://stackoverflow.com/questions/69695030/jupyter-notebook-input-not-showing-after-using-ipython-displaymarkdown) [5](https://stackoverflow.com/questions/48198676/jupyter-input-display-print-execution-order-is-chaotic) [6](https://stackoverflow.com/questions/34968112/how-to-give-jupyter-cell-standard-input-in-python/55011504#55011504)) where, under certain conditions, the input prompt does not appear on screen, which means that the program is permanently stuck waiting for input that the user cannot provide. In this code, I noticed the bug occasionally being triggered when asking the user to choose an option (classical attempt, quantum attempt, etc.). While I have done my best to mitigate this bug by adding a delay and flushing any pending output before asking the user for input, unfortunately I cannot gaurantee it will not appear when you run it -- if it does, I'm afraid you will need to stop and restart the notebook kernel.
- Since the game prints a lot of output on screen, for the best user experience, I suggest (if possible) reducing the browser zoom and using a larger monitor so that you can fit as much of the output as possible on screen without having to scroll. Otherwise, the IBM Quantum Lab platform might automatically scroll your screen up/down as the output size changes, which can be annoying.

## **Setup Game**
Run the following code cell to do the one-time setup for the game.

## **Play Game**
To actually play the game, run the following code cell. Note that, if you want to play the game again later, this is the only code cell you will need to re-run.  
Have fun! 😀

## **Sources**

- Wordle: 
    - Game: https://www.nytimes.com/games/wordle/index.html
    - Backstory:
        - https://www.nytimes.com/2022/01/03/technology/wordle-word-game-creator.html
        - https://time.com/6143832/new-york-times-buys-wordle/
- Wordle word lists:
    - Solutions: https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee
    - Allowed guesses (excluding solutions): https://gist.github.com/cfreshman/d5fb56316158a1575898bba1eed3b5da
- Quantum Tic Tac Toe: Semester 1 Lab 11 of Qubit by Qubit's *Introduction to Quantum Computing* course
- Printing emojis (eg. 🟩) with Python:
    - https://unicode.org/emoji/charts/full-emoji-list.html#geometric
- Calculating number of bits needed to represent a number in binary:
    - https://www.exploringbinary.com/number-of-bits-in-a-decimal-integer/
    - https://www.quora.com/How-many-bits-does-it-take-to-represent-a-number/answer/Cool-Cat-334?ch=10&oid=361012982&share=4d755cc6&srid=RuIR&target_type=answer
- Printing bold text with Python, using ANSI escape sequences:
    - https://stackoverflow.com/questions/24834876/how-can-i-make-text-bold-in-python/24835018#24835018
    - https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters