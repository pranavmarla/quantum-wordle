import sys

# Read in original word list from file, convert each word to uppercase, and then write all the words out as a tuple, that can be directly copied and pasted into the main code

input_file_name = sys.argv[1]

word_list = []
with open(input_file_name) as input_file:
    # Assume input file has one word per line
    for word in input_file:
        word = word.strip()
        word = word.upper()
        word_list.append(f'\'{word}\'')

word_list_string = ', '.join(word_list)
with open('output.txt', 'w') as output_file:
    # Looks like this: ('APPLE', 'BANANA', ...)
    output_file.write(f'({word_list_string})')