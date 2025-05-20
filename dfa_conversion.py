from nfa import State, NFA

def epsilon_closure(states):
    closure = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        for next_state in state.transitions.get('', []):  # ε-transição
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure

def move(states, symbol):
    result = set()
    for state in states:
        for next_state in state.transitions.get(symbol, []):
            result.add(next_state)
    return result

def nfa_to_dfa(nfa):
    from collections import deque

    dfa_states = {}
    dfa_transitions = {}
    queue = deque()

    start_closure = frozenset(epsilon_closure([nfa.start_state]))
    dfa_states[start_closure] = State("D0")
    queue.append(start_closure)
    state_id = 1

    while queue:
        current_set = queue.popleft()
        current_state = dfa_states[current_set]

        symbols = set()
        for s in current_set:
            symbols.update(sym for sym in s.transitions if sym != '')

        for sym in symbols:
            next_set = frozenset(epsilon_closure(move(current_set, sym)))
            if next_set not in dfa_states:
                dfa_states[next_set] = State(f"D{state_id}")
                state_id += 1
                queue.append(next_set)

            current_state.add_transition(sym, dfa_states[next_set])

    # Marcar estados finais
    for nfa_set, dfa_state in dfa_states.items():
        if any(s.is_final for s in nfa_set):
            dfa_state.is_final = True
            # Atribuir o tipo de token do primeiro estado final encontrado
            for s in nfa_set:
                if s.is_final and s.token_type:
                    dfa_state.token_type = s.token_type
                    break
            # Tratamento adicional para evitar token_type = None
            if dfa_state.token_type is None:
                dfa_state.token_type = "UNKNOWN"

    start_state = dfa_states[start_closure]
    return NFA(start_state)
