import re
from nfa import build_combined_nfa
from dfa_conversion import nfa_to_dfa
import time

# ================================================
# LISTA DOS TOKENS DA LANGB
# ================================================
# Palavras‐chave aparecem antes de "VAR".

TOKENS = [
    # 1) Palavras‐chave
    ("SHOW",  r"show"), 
    ("TEXT",  r"text"), # palavra‐chave "text" (não confundir com literal string)
    ("NUM",   r"num"),  # palavra‐chave "num" (não confundir com literal numérico)
    ("TRUE",  r"true"),
    ("FALSE", r"false"),

    # 2) Operadores e delimitadores
    ("ADD",       r"\+"),   
    ("SUB",       r"-"),
    ("MUL",       r"\*"),
    ("DIV",       r"/"),
    ("GT",        r">"),
    ("LT",        r"<"),
    ("EQ",        r"="),
    ("SEMICOLON", r";"),

    # 3) Literais
    ("STRING", r"\"[^\"]*\""),            # ex: "teSte"
    ("NUMBER",    r"[0-9]+"),                # ex: 0, 123, 42
    ("VAR",    r"[a-zA-Z_][a-zA-Z0-9_]*") # ex: a, var123, _nome
]

# ================================================
# Constrói NFA combinado e converte para DFA
# ================================================
nfa = build_combined_nfa(TOKENS)
dfa = nfa_to_dfa(nfa)

# ================================================
# Mapeamento rápido de lexema → token de palavra‐chave
# (somente para garantir que "show", "true", "false", "num" e "text"
#  jamais caiam em VAR)
# ================================================
keyword_map = {
    "show":  "SHOW",
    "num":   "NUM",
    "text":  "TEXT",
    "true":  "TRUE",
    "false": "FALSE"
}

# ================================================
# FUNÇÃO DE ANÁLISE LÉXICA (baseada no DFA)
# ================================================
def lexical_analysis(code, dfa):
    index = 0
    length = len(code)
    all_lines = []        # Lista de instruções (cada instrução é uma lista de tokens)
    current_line = []     # Tokens acumulados até encontrar um SEMICOLON

    while index < length:
        state = dfa.start_state
        last_accepting = None
        last_token_name = None
        last_match_end = index
        current_lexeme = ""
        i = index

        # Tenta consumir o máximo possível (maximal munch)
        while i < length:
            ch = code[i]
            if state.transitions.get(ch) is None:
                break
            state = state.transitions[ch][0]
            current_lexeme += ch
            if state.is_final:
                last_accepting = state
                last_token_name = state.token_type
                last_match_end = i + 1
            i += 1

        if last_accepting:
            lex_val = current_lexeme    # ex: "num", "5", "\"teSte\"", "true", "a" etc.
            tok     = last_token_name   # ex: "NUM", "ADD", "STRING", "VAR" etc.

            # ======> AQUI: forçamos palavras‐chave exatas, caso existam no lexema
            if lex_val in keyword_map:
                tok = keyword_map[lex_val]

            # 1) Se for VAR, verifica comprimento ≤ 30
            if tok == "VAR":
                if len(lex_val) > 30:
                    raise SyntaxError(f"Erro léxico: nome de variável '{lex_val}' excede 30 caracteres.")
                current_line.append("VAR")

            # 2) Se for STRING, converte para CONST
            elif tok == "STRING":
                current_line.append("STRING")

            # 3) Se for TRUE ou FALSE (palavras‐chave)
            elif tok == "TRUE":
                current_line.append("TRUE")
            elif tok == "FALSE":
                current_line.append("FALSE")

            # 4) Se for SHOW ou TEXT ou NUM ou NUMBER
            elif tok == "SHOW":
                current_line.append("SHOW")
            elif tok == "TEXT":
                current_line.append("TEXT")
            elif tok == "NUM":
                current_line.append("NUM")
            elif tok == "NUMBER":
                current_line.append("NUMBER")

            # 5) Operadores e delimitadores: ADD, SUB, MUL, DIV, GT, LT, EQ, SEMICOLON
            elif tok in {"ADD","SUB","MUL","DIV","GT","LT","EQ"}:
                current_line.append(tok)

            # 6) Se for ponto e vírgula, fecha a linha atual
            elif tok == "SEMICOLON":
                current_line.append("SEMICOLON")
                all_lines.append(current_line)
                current_line = []

            # 7) Caso algum outro token não previsto?
            else:
                # Em teoria, não cairá aqui, pois listamos todos os casos acima.
                # Mas, caso caia, lança erro para sinalizar algo inesperado:
                raise SyntaxError(f"Erro léxico: token inesperado '{tok}' (lexema='{lex_val}').")

            index = last_match_end

        else:
            # Se não reconheceu token: talvez seja espaço em branco => avança
            if code[index].isspace():
                index += 1
                continue
            # Senão, caractere inválido → erro léxico
            else:
                raise SyntaxError(f"Erro léxico: caractere inesperado '{code[index]}' na posição {index}.")

    # No fim, se ainda houver tokens sem ;, gera erro
    if current_line:
        raise SyntaxError("Erro léxico: falta ';' ao final de alguma instrução.")

    return all_lines


# ================================================
# Ao executar diretamente, imprime cada instrução
# ================================================

if __name__ == "__main__":
    try:
        while True:
            print("\n===============================")
            print("   ANÁLISE LÉXICA - LANGB")
            print("===============================")
            print("Escolha o arquivo de teste:")
            print("  1 - teste1.txt")
            print("  2 - teste2.txt")
            print("  3 - teste3.txt")
            print("  4 - Sair")
            escolha = input("Digite sua opção (1, 2, 3 ou 4): ")

            if escolha not in ["1", "2", "3", "4"]:
                print("\n[!] Escolha inválida. Tente novamente.")
                time.sleep(1.2)
                continue

            if escolha == "4":
                print("\nSaindo... Até logo!")
                time.sleep(1)
                break

            arquivo = f"ArquivosTeste/teste{escolha}.txt"
            print(f"\nAbrindo arquivo '{arquivo}'...")
            time.sleep(1)
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    source_code = f.read()
                print("Arquivo carregado com sucesso!")
                time.sleep(0.8)
                print("\n=========================================")
                print(f"Análise léxica do arquivo '{arquivo}':")
                print("=========================================")
                linhas_de_tokens = lexical_analysis(source_code, dfa)
                for linha in linhas_de_tokens:
                    print("  >", " ".join(linha))
                print("=========================================\n")
                time.sleep(1.5)
            except FileNotFoundError:
                print("\n[!] Arquivo de teste não encontrado.")
                time.sleep(1.5)
    except SyntaxError as e:
        print(f"\n[ERRO] {str(e)}")
        time.sleep(2)