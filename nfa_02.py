import re
from graphviz import Digraph

# After the tokenization and definition of the regex patterns, we will start the regex to NFA process.
# First, let's define a State class to represent the states of the NFA.

class State:
    _id_counter = 0

    def __init__(self, name=None):
        if name is None:
            name = f"q{State._id_counter}"
            State._id_counter += 1
        self.name = name
        self.transitions = {}
        self.is_final = False
        self.token_type = None

    def add_transition(self, symbol, next_state):
        if symbol in self.transitions:
            self.transitions[symbol].append(next_state)
        else:
            self.transitions[symbol] = [next_state]


# Representa o NFA, com estado inicial e final, e métodos para coletar todos os estados.
class NFA:
    def __init__(self, start_state, final_state):
        self.start_state = start_state
        self.final_state = final_state
        self.states = self.get_all_states()

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

# Cria um NFA para um único símbolo.
def basic_nfa(symbol):
    start = State()
    end = State()
    start.add_transition(symbol, end)
    return NFA(start, end)

# Concatena dois NFAs, conectando seus estados finais e iniciais.
def concatenate_nfa(nfa1, nfa2):
    nfa1.final_state.add_transition('', nfa2.start_state)
    return NFA(nfa1.start_state, nfa2.final_state)

# Cria um NFA que é a união de dois outros NFAs.
def union_nfa(nfa1, nfa2):
    start = State()
    end = State()
    start.add_transition('', nfa1.start_state)
    start.add_transition('', nfa2.start_state)
    nfa1.final_state.add_transition('', end)
    nfa2.final_state.add_transition('', end)
    return NFA(start, end)

# Aplica a operação de Kleene Star em um NFA.
def star_nfa(nfa):
    start = State()
    end = State()
    start.add_transition('', nfa.start_state)
    start.add_transition('', end)
    nfa.final_state.add_transition('', nfa.start_state)
    nfa.final_state.add_transition('', end)
    return NFA(start, end)

# Cria um NFA a partir de um literal (sequência de caracteres).
def literal_nfa(literal):
    nfa = basic_nfa(literal[0])
    for c in literal[1:]:
        nfa = concatenate_nfa(nfa, basic_nfa(c))
    return nfa

#  Constrói um NFA para múltiplos padrões de tokens fornecidos.
def build_combined_nfa(token_patterns):
    global_start = State("q_start")
    all_states = [global_start]
    for token_name, pattern in token_patterns:
        try:
            if pattern.isalpha() or re.fullmatch(r"[\\\\\\[\\]\\+\\*a-zA-Z0-9]+", pattern):
                literal = re.sub(r"\\", "", pattern)
                nfa = literal_nfa(literal)
            else:
                if pattern == "[0-9]+":
                    digit = basic_nfa('0')
                    for d in '123456789':
                        digit = union_nfa(digit, basic_nfa(d))
                    nfa = concatenate_nfa(digit, star_nfa(digit))
                elif pattern == "\"[^\"]*\"":
                    start_quote = basic_nfa('"')
                    end_quote = basic_nfa('"')
                    mid = star_nfa(basic_nfa('a'))
                    nfa = concatenate_nfa(start_quote, concatenate_nfa(mid, end_quote))
                else:
                    continue
            nfa.final_state.is_final = True
            nfa.final_state.token_type = token_name
            global_start.add_transition('', nfa.start_state)
            all_states.extend(nfa.states)
        except Exception as e:
            print(f"Erro ao criar NFA para token {token_name}: {e}")
    return global_start, all_states

# Gera um diagrama visual do NFA usando Graphviz e salva como uma imagem.
def draw_nfa(start_state, all_states, filename="nfa_langb"):
    dot = Digraph(comment='NFA', format='png')
    dot.attr(rankdir='LR', dpi='300', size='15,10', margin='0.3', nodesep='0.8', ranksep='0.6')
    dot.attr('node', shape='circle', fixedsize='true', width='1.2', fontsize='16')

    for state in all_states:
        shape = 'doublecircle' if state.is_final else 'circle'
        label = f"{state.name}"
        if state.token_type:
            label += f"\n[{state.token_type}]"
        dot.node(state.name, label=label, shape=shape)

    dot.node('start', shape='plaintext', label='')
    dot.edge('start', start_state.name, label='start')

    # Transições
    for state in all_states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                label = symbol if symbol else 'ε'
                dot.edge(state.name, target.name, label=label)

    # Geração de arquivos em PNG
    output_png = dot.render(filename=filename, format='png', cleanup=True)
    print(f"✅ Diagrama salvo como {output_png}")
    