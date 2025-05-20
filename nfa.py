import re
from graphviz import Digraph

# Representa o NFA, com estado inicial e (opcional) final, e métodos para coletar todos os estados.
class NFA:
    def __init__(self, start_state, final_state=None):
        self.start_state = start_state
        self.final_state = final_state
        self.states = self.get_all_states()

    # Retorna uma lista de todos os estados do NFA.
    def get_all_states(self):
        visited = set()
        states = []
        stack = [self.start_state]
        while stack:
            current = stack.pop()
            if not isinstance(current, State):
                continue
            if current.name not in visited:
                visited.add(current.name)
                states.append(current)
                for targets in current.transitions.values():
                    for target in targets:
                        if isinstance(target, State):
                            stack.append(target)
        return states

# Representa um estado do NFA, com transições e propriedades (se é final e tipo de token).
class State:
    _id_counter = 0

    def __init__(self, name=None):
        if name is None:
            name = f"q{State._id_counter}"
            State._id_counter += 1
        self.name = name
        self.transitions = {}      # dict: símbolo → lista de estados
        self.is_final = False
        self.token_type = None     # Quando for estado final, armazena o token

    def add_transition(self, symbol, next_state):
        if symbol in self.transitions:
            self.transitions[symbol].append(next_state)
        else:
            self.transitions[symbol] = [next_state]

# Cria um NFA para um único símbolo literal.
def basic_nfa(symbol):
    start = State()
    end = State()
    end.is_final = True
    start.add_transition(symbol, end)
    return NFA(start, end)

# Concatena dois NFAs (η·β): conecta o final de nfa1 ao início de nfa2 usando ε-transição.
def concatenate_nfa(nfa1, nfa2):
    nfa1.final_state.add_transition('', nfa2.start_state)
    nfa1.final_state.is_final = False
    return NFA(nfa1.start_state, nfa2.final_state)

# União de dois NFAs (η ∪ β).
def union_nfa(nfa1, nfa2):
    start = State()
    end = State()

    start.add_transition('', nfa1.start_state)
    start.add_transition('', nfa2.start_state)

    nfa1.final_state.add_transition('', end)
    nfa2.final_state.add_transition('', end)

    nfa1.final_state.is_final = False
    nfa2.final_state.is_final = False

    end.is_final = True
    return NFA(start, end)

# União de uma lista de NFAs
def multi_union_nfa(nfa_list):
    if not nfa_list:
        raise ValueError("Lista de NFAs vazia.")

    # Novo estado inicial e final
    start_state = State()
    final_state = State()
    final_state.is_final = True

    for nfa in nfa_list:
        start_state.add_transition('', nfa.start_state)
        nfa.final_state.add_transition('', final_state)
        nfa.final_state.is_final = False

    return NFA(start_state, final_state)

# Estrela de Kleene em um NFA
def star_nfa(nfa):
    start = State()
    end = State()

    start.add_transition('', end)
    end.add_transition('', nfa.start_state)
    nfa.final_state.add_transition('', end)

    nfa.final_state.is_final = False
    end.is_final = True

    return NFA(start, end)

# Cria um NFA para uma literal inteira (palavra-chave ou operador), usando basic_nfa + concatenações.
def build_literal_nfa(token_name, literal):
    # literal é uma string sem escapes (e.g. "show", "+", ";", etc.)
    nfa = basic_nfa(literal[0])
    for c in literal[1:]:
        nfa = concatenate_nfa(nfa, basic_nfa(c))
    nfa.final_state.name = f"q{token_name}"
    nfa.final_state.token_type = token_name
    return nfa

# Cria um NFA para números inteiros ([0-9]+).
def build_num_nfa():
    # Primeiro dígito: '0' ou '1'..'9'
    digit = basic_nfa('0')
    for d in '123456789':
        digit = union_nfa(digit, basic_nfa(d))
    # Permite repetições
    nfa = concatenate_nfa(digit, star_nfa(digit))
    nfa.final_state.name = "qNUM"
    nfa.final_state.token_type = "NUM"
    return nfa

# Cria um NFA para strings literais: " [qualquer-char-exceto-"]* "
def build_string_nfa():
    start = State()
    open_quote = State()
    string_content = State()
    close_quote = State()
    close_quote.is_final = True

    # Abre aspas
    start.add_transition('"', open_quote)

    # Qualquer caractere ASCII exceto aspas = conteúdo da string
    for c in range(32, 127):
        ch = chr(c)
        if ch != '"':
            open_quote.add_transition(ch, string_content)
            string_content.add_transition(ch, string_content)

    # Fechamento de aspas
    string_content.add_transition('"', close_quote)
    open_quote.add_transition('"', close_quote)  # Caso a string seja "" (vazia)

    nfa = NFA(start, close_quote)
    nfa.final_state.name = "qSTRING"
    nfa.final_state.token_type = "STRING"
    return nfa

# Cria um NFA para identificadores/variáveis: [a-zA-Z_][a-zA-Z0-9_]*
def build_var_nfa():
    # Primeiro caractere: letra ou '_'
    first_chars = [basic_nfa(c) for c in (list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["_"])]
    start_nfa = multi_union_nfa(first_chars)

    # Caracteres subsequentes: letra, dígito ou '_'
    body_chars = [basic_nfa(c) for c in (list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") + ["_"])]
    body_nfa = multi_union_nfa(body_chars)

    # Concatena: primeiro caractere + (body)* 
    nfa = concatenate_nfa(start_nfa, star_nfa(body_nfa))
    nfa.final_state.name = "qVAR"
    nfa.final_state.token_type = "VAR"
    return nfa

# === AQUI: lista apenas com tokens literais de LangB ===
palavras_reservadas = (
    # Palavras-chave (literal exato)
    r"num", r"text", r"true", r"false", r"show",
    # Operadores e delimitadores (literais com escape onde necessário)
    r"\+", r"-", r"\*", r"/", r">", r"<", r"=", r";"
)

# Constrói um NFA combinado, unindo todos os NFAs de cada token-list.
def build_combined_nfa(tokens):
    global_start = State("q_start")
    all_states = [global_start]

    for token_name, regex in tokens:
        if regex in palavras_reservadas:
            # Trata token literal exato
            literal = re.sub(r"\\", "", regex)  # e.g. r"\+" → "+"
            nfa = build_literal_nfa(token_name, literal)

        else:
            # Número inteiro
            if regex == "[0-9]+":
                nfa = build_num_nfa()
                nfa.final_state.name = f"q{token_name}"
                nfa.final_state.token_type = token_name

            # String literal
            elif regex == r"\"[^\"]*\"":
                nfa = build_string_nfa()
                nfa.final_state.name = f"q{token_name}"
                nfa.final_state.token_type = token_name

            # Identificador/variável
            elif regex == "[a-zA-Z_][a-zA-Z0-9_]*":
                nfa = build_var_nfa()
                nfa.final_state.name = f"q{token_name}"
                nfa.final_state.token_type = token_name

            else:
                # Qualquer outro regex não compreendido → ignora
                continue

        # Conecta o NFA recém-criado ao global por ε-transição
        global_start.add_transition('', nfa.start_state)
        all_states.extend(nfa.states)

    return NFA(global_start, None)

# ===================================================
# (Opcional) Funções para desenhar o NFA via Graphviz
def draw_nfa(nfa, filename):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')

    try:
        # Estado inicial “fantasma”
        dot.node('start', shape='none', label='')
        dot.edge('start', nfa.start_state.name)

        visited = set()
        queue = [nfa.start_state]

        while queue:
            state = queue.pop(0)
            if state in visited:
                continue
            visited.add(state)

            shape = 'doublecircle' if state.is_final else 'circle'
            label = state.name
            if state.is_final and state.token_type:
                label += f'\n{state.token_type}'
            dot.node(state.name, label=label, shape=shape)

            for symbol, next_states in state.transitions.items():
                for next_state in next_states:
                    lbl = 'ε' if symbol == '' else escape_symbol(symbol)
                    dot.edge(state.name, next_state.name, label=lbl)
                    if next_state not in visited:
                        queue.append(next_state)

        dot.save(f'{filename}.dot')
        output = dot.render(filename, view=True, cleanup=True)
        print(f"Visualização gerada em: {output}")
        return True

    except Exception as e:
        print(f"Erro ao gerar visualização: {str(e)}")
        return False

def escape_symbol(symbol):
    if symbol == '\\':
        return '\\\\'
    return symbol.replace('"', '\\"').replace('\n', '\\n')