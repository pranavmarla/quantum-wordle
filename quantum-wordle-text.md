# Capstone Project: Quantum Wordle

By **Pranav Marla** (`4181_Marla`)

## Overview

This is a fully functioning, playable implementation of a quantum game.
Inspired by the Quantum Tic Tac Toe game introduced in semester 1 lab 11, this is also a quantum spin on a classical game -- specifically, a quantum spin on the game Wordle.

### **Wordle**
Developed by Josh Wardle as a gift for his partner before going viral upon its public release in Oct 2021 and eventually being bought by the New York Times, [Wordle](https://www.nytimes.com/games/wordle/index.html) is a word game that challenges you to guess a mystery five-letter word in six attempts.

Each time you make a guess, you receive a clue in the form of five coloured squares, one per letter, indicating how close/correct each corresponding letter of the guess was.  
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
What I described above is the regular ("classical") Wordle, where your only option is to make what I call a classical attempt: i.e. For each attempt, you can make one guess and one clue corresponding to that guess.

In addition to the classical attempt, I have introduced two more options with some added quantum ✨flair✨:
- Quantum Attempt: For each attempt, you can make a superposition of *two* guesses. However, just like a real superposition, the cost of having access to extra states (here, guesses) is that you lose the certainty of a classical state -- in other words, after you make your two guesses, you will receive two clues, but you will *not* know which clue corresponds to which guess!  
Eg. Let's say you choose the quantum attempt option and, in that attempt, you make two guesses: *WEEPY* and *EERIE*. You might receive two clues that look like this:
    ```
    W E E P Y  |  E E R I E
        🟥🟥🟥🟥🟩
        -----------
        🟥🟨🟥🟨🟥
    ```
    Without further information, you *cannot* tell, for example, whether the first clue (🟥🟥🟥🟥🟩) corresponds to *WEEPY* or *EERIE* -- the ordering of the clues is completely random.
- Measure all quantum attempts: Just like with a real superposition, if you want full certainty as to its state, all you need to do is measure it. Here, at any point in the game, you can choose to measure all the quantum states have been created so far -- once you do so, each quantum attempt will randomly collapse to a classical attempt. This means that, when you measure your quantum attempt, the game will randomly pick one of those two guesses to collapse to, and will only display that guess and its associated clue.  
Eg. If you chose to measure the above quantum attempt, it might randomly collapse to the following classical attempt:
    ```
     E E R I E
    🟥🟥🟥🟥🟩
    ```
    Now you know with full certainty that the clue 🟥🟥🟥🟥🟩 corresponds to *EERIE* but, of course, you no longer have access to the extra information regarding the guess *WEEPY*.

### **Implementation**
Under the hood, Quantum Wordle is implemented using two separate quantum circuits:
- Game Circuit: This is the main circuit underpinning the game, used to encode the attempts. There are six qubits, one per attempt. Each attempt has a *guess list*, storing the various guesses made in that attempt. The state of each qubit is interpreted as a list index, indicating which guess in the corresponding attempt's guess list should be used.  
Eg.
    - A classical attempt has only one guess, so its guess list will consist of only one guess at index `0`. Thus, the corresponding qubit will be in the `|0>` state, indicating that we should use the guess located at index 0 of the clasical attempt's guess list.
    - A quantum attempt has two guesses, so its guess list will consist of two guesses, at indices `0` and `1` respectively. Thus, the corresponding qubit will be in a *superposition* of the `|0>` and `|1>` states (specifically, the `|+>` state), indicating that we should use the guess located at index 0 *and* the guess located at index 1 of the quantum attempt's guess list.
    - When you choose the *measure all quantum attempts* option, the entire game circuit is measured. The qubits corresponding to classical attempts will of course be unchanged (will remain in the `|0>` state), but the qubits corresponding to quantum attempts, which were in superposition, will collapse. We interpret this as the quantum attempt collapsing to a classical attempt, and, depending on whether the qubit collapsed to either `|0>` or `|1>`, randomly selecting either the guess at index `0` or the guess at index `1` of the formerly quantum attempt's guess list to use going forward -- the other guess is discarded.

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



## Disclaimer