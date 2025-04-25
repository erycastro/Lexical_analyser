import re

# Tokenization rules :
TOKENS = [
    ("NUM", r"[0-9]+"),
    ("STRING", r"\"[^\"]*\""),
    ("TEXT", r"text"),
    ("VAR", r"[a-zA-Z_][a-zA-Z0-9_]{0,29}"),
    ("FALSE", r"false"),
    ("TRUE", r"true"),
    ("SHOW", r"show"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MPY", r"\*"),
    ("DIV", r"/"),
    ("GT", r">"),
    ("LT", r"<"),
    ("EQ", r"="),
    ("EXC", r"!"),
    ("AT", r"@"),
    ("HASH", r"#"),
    ("DOLLAR", r"\$"),
    ("PCT", r"%"),
    ("AMPERSAND", r"&"),
    ("QUESTION", r"\?"),
    ("UNDERSCORE", r"_"),
    ("PIPE", r"\|"),
    ("SEMICOLON", r";"),
]

# After the tokenization and definition of the regex patterns, we will start the regex to NFA process.
# First, let's define a State class to represent the states of the NFA.

class State:
    def __init__(self, name):
        self.name = name
        self.transitions = {}
        self.is_final = False
    
    def add_transition(self, symbol, next_state):
        if symbol in self.transitions:
            self.transitions[symbol].append(next_state)
        else:
            self.transitions[symbol] = [next_state]

# Now let's define the NFA class. The NFA will be constructed from the regex patterns defined above.
class NFA:
    def __init__(self, start_state, final_state):
        self.start_state = start_state
        self.final_state = final_state
        self.states = [start_state, final_state]    

# Now let's define a function to build a basic one character NFA.
def basic_nfa(symbol):
    start = State(f"q{symbol}_start")
    final = State(f"q{symbol}_final")
    start.add_transition(symbol, final)
    nfa = NFA(start, final)
    return nfa
