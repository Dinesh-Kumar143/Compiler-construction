import re

class Token:
    def __init__(self, Class_Part, Value_Part, Line_No):
        self.Class_Part = Class_Part
        self.Value_Part = Value_Part
        self.Line_No = Line_No

    def format_token(self):
        return f"{self.Value_Part}[{self.Class_Part}] "
    
    def lex_output(self, file):
        output = f"({self.Class_Part}, {self.Value_Part}, {self.Line_No})"
        # with open(file, "w") as file: 
        file.write(output + "\n")


class Lexical_Analyzer:
    def __init__(self):
        self.tokens = []
        self.input = ''
        self.line = 1
        self.temp = ""

        # List of Keywords
        self.keywords = [
            {'Keyword (DT)': ['num', 'text', 'bool']},
            {'Keyword (BOOL)': ['True', 'False']},
            {'Keyword (CS)': ['if', 'elif']},
            {'Keyword (LS)': ['and', 'or']},
            {'Keyword (AM)': ['public', 'private', 'protected']},
            {'Keyword' : ['None', 'stop', 'skip', 'def', 'load', 'back', 'else', 'loop', 'not',
            'attempt', 'handle', 'ensure', 'trigger', 'triggers', 'class', 'new', 'from', 'this', 'super',
            'abstract', 'final', 'static', 'Main']}
        ]

        # List of punctuators
        self.punctuators = [',', ':', '.', '{', '}', '[', ']', '(', ')']

        # Dictionary of constants
        self.constants = {
            'num_const': r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$',
            'text_const': r'^"([^"\\]|\\.)*"$'
        }

    def check_constant(self):
        # Check for numeric constants
        for item in self.constants:
            if isinstance(item, dict):  # Check if item is a dictionary
                for key, pattern in item.items():
                    if re.fullmatch(pattern, self.temp):
                        return key

        # Check for character constants
        if self.temp.startswith("'") and not (self.temp.endswith("'")):
            return 'invalid'
        elif (self.temp.startswith("'") and self.temp.endswith("'")):
            if 2 <= len(self.temp) <= 4:
                # Remove the enclosing single quotes
                inner = self.temp[1:-1]

                if len(inner) == 2 and inner[0] == '\\':
                    if len(inner) == 2:  # e.g., '\a'
                        self.temp = inner
                        return 'text'
                elif len(inner) == 1:  # e.g., 'a'
                    self.temp = inner
                    return 'text'

                return 'invalid'  # Return "invalid" if word does not match any pattern

        # Check for numeric constants
        if re.fullmatch(self.constants['num_const'], self.temp):
            return 'num_const'
        return "invalid"  # Return "invalid" if word does not match any pattern

    def check_identifier(self):
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        if re.match(pattern, self.temp):
            return "ID"
        return 'invalid'  # Return "invalid" if word does not match the pattern

    def find_keyword(self):
        for item in self.keywords:
            if isinstance(item, dict):  # Check if item is a dictionary
                for key, values in item.items():
                    if self.temp in values:
                        return key
            elif self.temp == item:  # Check if item is a string and matches the self.temp
                return self.temp

        return self.check_identifier()  # Return "invalid" if word is not found

    def Read_source_file(self):
        with open("LA_input.txt", 'r') as file:
            self.input = file.read()

    def LA(self):
        inputIndex = 0
        while inputIndex < len(self.input):
            char = self.input[inputIndex]
            
            # Handling single-line comments
            if char == '#':
                while inputIndex < len(self.input) and self.input[inputIndex] != '\n':
                    inputIndex += 1
                self.line += 1
                inputIndex += 1  # Move to the next character after the newline
                continue

            # Handling multi-line comments
            elif self.input[inputIndex:inputIndex+2] == '/*':
                inputIndex += 2
                while inputIndex < len(self.input) and self.input[inputIndex:inputIndex+2] != '*/':
                    if self.input[inputIndex] == '\n':
                        self.line += 1
                    inputIndex += 1
                inputIndex += 2
                if inputIndex < len(self.input) and self.input[inputIndex] == '\n':
                    self.line += 1
                    inputIndex += 1
                continue

            # Handling semi-colon for line change
            elif char == ';':
                # self.line += 1
                inputIndex += 1
                continue

            # Handling whitespace
            elif char.isspace():
                if char == '\n':
                    self.line += 1
                inputIndex += 1
                continue

            # Handling punctuators
            elif char in self.punctuators:
                self.tokens.append(Token('Punctuator', char, self.line))
                inputIndex += 1
                continue

            # Handling operators and multi-character operators
            elif char in ['+', '-', '*', '/', '%', '>', '<', '!', '=', '^']:
                if inputIndex + 1 < len(self.input) and self.input[inputIndex + 1] == '=':
                    op = char + '='
                    if op in ['<=', '>=', '!=', '==']:
                        self.tokens.append(Token('Operator (ROP)', op, self.line))
                    elif op in ['+=', '-=', '*=', '/=', '%=']:
                        self.tokens.append(Token('ASS', op, self.line))
                    inputIndex += 2
                else:
                    if char in ['+', '-']:
                        self.tokens.append(Token('Operator (PM)', char, self.line))
                    elif char in ['*', '/', '%']:
                        self.tokens.append(Token('Operator (MDM)', char, self.line))
                    elif char in ['>', '<', '!']:
                        self.tokens.append(Token('Operator (ROP)', char, self.line))
                    elif char == '=':
                        self.tokens.append(Token('Operator', '=', self.line))
                    elif char == '^':
                        self.tokens.append(Token('Operator', '^', self.line))
                    inputIndex += 1
                continue

            # Handle string literals
            elif char == '"':
                self.temp = char
                inputIndex += 1
                while inputIndex < len(self.input) and self.input[inputIndex] != '"':
                    if self.input[inputIndex] == '\\':
                        # Append escape character
                        self.temp += self.input[inputIndex]
                        inputIndex += 1
                    self.temp += self.input[inputIndex]
                    inputIndex += 1
                if inputIndex < len(self.input):
                    # Append the closing quote
                    self.temp += self.input[inputIndex]
                    inputIndex += 1
                self.tokens.append(Token('text', self.temp, self.line))
                self.temp = ""
                continue

            # Handle other characters
            else:
                self.temp += char
                inputIndex += 1

                if (inputIndex == len(self.input) or
                    self.input[inputIndex].isspace() or
                    self.input[inputIndex] in self.punctuators or
                        self.input[inputIndex] in ['+', '-', '*', '/', '%', '>', '<', '!', '=', '^', ';', ':', "&"]):

                    result = self.check_constant()
                    if result != "invalid":
                        self.tokens.append(Token(result, self.temp, self.line))
                        self.temp = ""
                    else:
                        result = self.find_keyword()
                        if result != "invalid":
                            self.tokens.append(
                                Token(result, self.temp, self.line))
                        else:
                            self.tokens.append(
                                Token(result, self.temp, self.line))
                        self.temp = ""

        # Append any remaining tokens after loop ends
        if self.temp:
            result = self.check_constant()
            if result != "invalid":
                self.tokens.append(Token(result, self.temp, self.line))
            else:
                result = self.find_keyword()
                if result != "invalid":
                    self.tokens.append(Token(result, self.temp, self.line))


# Usage
lexical_analyzer = Lexical_Analyzer()
lexical_analyzer.Read_source_file()
lexical_analyzer.LA()
    
# Group tokens by line number and print them line by line
from itertools import groupby

# Group tokens by line number
tokens_grouped_by_line = groupby(sorted(lexical_analyzer.tokens, key=lambda t: t.Line_No), key=lambda t: t.Line_No)

# Print each line's tokens on the same line
for line_no, tokens in tokens_grouped_by_line:
    token_strs = [token.format_token() for token in tokens]
    print(f"Line {line_no}: {' '.join(token_strs)}")

file = open("LA_Output.txt" ,'w')    
for token in lexical_analyzer.tokens:
    token.lex_output(file)
file.close()