import re
from graphviz import Digraph

# Representa o NFA, com estado inicial e final, e métodos para coletar todos os estados.
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

# Representa um estado do NFA, com transições e propriedades como se é final e o tipo de token.
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

# Cria um NFA para um único símbolo.
def basic_nfa(symbol):
    start = State()
    end = State()
    end.is_final = True
    start.add_transition(symbol, end)
    return NFA(start, end)

# Concatena dois NFAs, conectando seus estados finais e iniciais.
def concatenate_nfa(nfa1, nfa2):
    nfa1.final_state.add_transition('', nfa2.start_state)
    nfa1.final_state.is_final = False  
    return NFA(nfa1.start_state, nfa2.final_state)

# Cria um NFA que é a união de dois outros NFAs.
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

# Cria um NFA que é a união de uma lista de NFAs.
def multi_union_nfa(nfa_list):
    if not nfa_list:
        raise ValueError("Lista de NFAs vazia.")
    
    # Cria um novo estado inicial único
    start_state = State()
    final_state = State()
    final_state.is_final = True
    
    # Conecta o estado inicial a todos os NFAs
    for nfa in nfa_list:
        start_state.add_transition('', nfa.start_state)
        nfa.final_state.add_transition('', final_state)
        nfa.final_state.is_final = False
    
    return NFA(start_state, final_state)

# Aplica a operação de Kleene Star em um NFA.
def star_nfa(nfa):
    start = State()
    end = State()

    start.add_transition('', end)
    end.add_transition('', nfa.start_state)
    nfa.final_state.add_transition('', end)

    end.is_final = True
    nfa.final_state.is_final = False

    return NFA(start, end)

# Cria um NFA a partir de um literal (sequência de caracteres).
def build_literal_nfa(token_name, literal):
    nfa = basic_nfa(literal[0])
    for c in literal[1:]:
        nfa = concatenate_nfa(nfa, basic_nfa(c))
    nfa.final_state.name = f"q{token_name}"
    return nfa

# Cria um NFA para strings, permitindo qualquer caractere exceto aspas.
def build_string_nfa():

    start = State()
    open_quote = State()
    string_content = State()
    close_quote = State()
    close_quote.is_final = True
    
    start.add_transition('"', open_quote)
    
    for c in range(32, 127):
        char = chr(c)
        if char != '"':
            open_quote.add_transition(char, string_content)
            string_content.add_transition(char, string_content)
    
    string_content.add_transition('"', close_quote)
    open_quote.add_transition('"', close_quote) 
    
    nfa = NFA(start, close_quote)
    nfa.final_state.name = "qSTRING"
    return nfa

# Cria um NFA para números, permitindo dígitos de 0 a 9.
def build_num_nfa():
    digit = basic_nfa('0')
    for d in '123456789':
        digit = union_nfa(digit, basic_nfa(d))
    nfa = concatenate_nfa(digit, star_nfa(digit))
    nfa.final_state.name = "qNUM"
    return nfa

# Cria um NFA para variáveis, permitindo letras, números e o caractere '_'
def build_var_nfa():
    # Primeiro caractere: letra ou _
    first_chars = [basic_nfa(c) for c in (list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["_"])]
    start_nfa = multi_union_nfa(first_chars) 

    # Caracteres seguintes: letras, números ou _
    body_chars = [basic_nfa(c) for c in (list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") + ["_"])]
    body_nfa = multi_union_nfa(body_chars)  # Usando multi_union_nfa aqui

    # Permitir qualquer quantidade de repetições (inclusive 0)
    nfa = concatenate_nfa(start_nfa, star_nfa(body_nfa))  # Aqui o "*" é usado
    nfa.final_state.name = "qVAR"
    return nfa

#regex para palavras reservadas
palavras_reservadas = (
    r"text", r"number", r"string", r"true", r"false", r"show",
    r"\+", r"-", r"\*", r"/", r">", r"<", r"=", r"!", r"@", r"#", r"\$",
    r"%", r"&", r"\?", r"_", r"\|", r";"
)

def build_combined_nfa(tokens):
    global_start = State("q_start")
    all_states = [global_start]  # Lista com todos os estados do NFA

    for token_name, regex in tokens:
        
        # Verifica se o regex é uma palavra reservada ou um padrão específico
        if regex in palavras_reservadas:
            literal = re.sub(r"\\", "", regex) # Remove barras invertidas do regex
            nfa = build_literal_nfa(token_name, literal)
        else :
            # se for um número
            if regex == "[0-9]+": 
               nfa = build_num_nfa();

            # se for uma string
            elif regex == r"\"[^\"]*\"": 
                nfa = build_string_nfa();

            # se for uma variável
            elif regex == "[a-zA-Z_][a-zA-Z0-9_]*":
                nfa = build_var_nfa();  

        # Adiciona transições e estados ao NFA global
        global_start.add_transition('', nfa.start_state)
        all_states.extend(nfa.states)
   
    return NFA(global_start, None)


#Funcoes para printar o nfa
#=====================================================================================================
def draw_nfa(nfa, filename):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')
 
    try:
        # Adiciona estado inicial especial
        dot.node('start', shape='none', label='')
        dot.edge('start', nfa.start_state.name)
        
        visited = set()
        queue = [nfa.start_state]
        
        while queue:
            state = queue.pop(0)
            if state in visited:
                continue
            visited.add(state)
            
            # Configura aparência do estado
            shape = 'doublecircle' if state.is_final else 'circle'
            label = state.name
            if state.is_final and state.token_type:
                label += f'\n{state.token_type}'
            
            dot.node(state.name, label=label, shape=shape)
            
            # Adiciona transições
            for symbol, next_states in state.transitions.items():
                for next_state in next_states:
                    label = 'ε' if symbol == '' else escape_symbol(symbol)
                    dot.edge(state.name, next_state.name, label=label)
                    
                    if next_state not in visited:
                        queue.append(next_state)
        
        # Salva e renderiza
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

#=====================================================================================================