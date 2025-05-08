import re
from nfa import build_combined_nfa, draw_nfa

# Tokens criados para o analisador léxico
TOKENS = [
    ("SHOW", r"show"), 
    ("TEXT", r"text"), 
    ("FALSE", r"false"), 
    ("TRUE", r"true"), 
    ("number", r"number"),  
    ("string", r"string"), 
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
    ("NUM", r"[0-9]+"), #
    ("STRING", r"\"[^\"]*\""), #
    ("VAR", r"[a-zA-Z_][a-zA-Z0-9_]*")
]

nfa = build_combined_nfa(TOKENS)

draw_nfa(nfa, "img_nfa/nfa")