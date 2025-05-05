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

def tokenize(code):
    tokens = []
    line_number = 1
    position = 0
    while position < len(code):
        match = None
        for token_type, token_regex in TOKENS:
            regex = re.compile(token_regex)
            match = regex.match(code, position)
            if match:
                value = match.group(0)
                tokens.append((token_type, value))
                position = match.end()
                break
        if not match:
            if code[position] in ['\n', ' ', '\t']:  # Ignorar espaços e quebras de linha
                position += 1
            else:
                print(f"Erro ao tokenizar linha: {code}")
                print(f"Caractere não reconhecido: '{code[position]}' em posição {position}")
                position += 1
    return tokens