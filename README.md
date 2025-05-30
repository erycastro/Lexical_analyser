﻿# Analisador Léxico: Projeto de compiladores- README

## 📌 Visão Geral
Este projeto implementa um **analisador léxico** para processamento de linguagens de programação. O analisador lêxico é a primeira etapa do processo de compilação de uma linguagem e transforma código-fonte em uma sequência de tokens, que são a base para análises sintáticas posteriores.

## ▶️ Como executar

### 1. Instale as dependências

Este projeto utiliza a biblioteca `graphviz`, instale via pip:

```
pip install graphviz
```
### 2. Execute o analisador

No terminal, execute o arquivo principal:

```
python lex_analiser.py
```

## 🔍 Aprofundamento Técnico
 Nossa linguagem é simplificada, mas segue a estrutura de um analisador léxico real. O processo de análise léxica segue estas etapas fundamentais:

1. **Código Fonte**  
   Entrada bruta do programa a ser compilado  
   Exemplo: `show "Result: ", x + 42;`

2. **Expressões Regulares/regex**  
   Cada tipo de token é definido por um padrão:  
   ```python
   tokens = [
       ('SHOW', r'show'),
       ('STRING', r'"[^"]*"'),
       ('NUMBER', r'[0-9]+'),
   ]
   ```

3. **Construção de NFAs**  
   Cada regex é convertido em um Autômato Finito Não-Determinístico:  

4. **Unificação de NFAs**  
   Todos os NFAs são combinados em um autômato único:  
![alt text](imgNfa/example.png)
5. **Conversão para DFA**  
   O NFA unificado é transformado em Autômato Finito Determinístico para eficiência.

6. **Análise Léxica**  
   O DFA processa o código fonte, identificando tokens:  
   ```
   SHOW STRING VAR PLUS NUM SEMICOLON
   ```

## 🛠️ Tecnologias
- **Python 3.8+**
- **Graphviz** (para visualização)
- **Regex** (para padrões lexicais)

### Visualização de NFAs
```python
from nfa import build_combined_nfa, draw_nfa

# Define seus padrões léxicos
tokens = [
    ('NUMBER', r'[0-9]+')
]

nfa = build_combined_nfa(tokens)
draw_nfa(nfa, "meu_nfa")  # Gera meu_nfa.png
```

## 📂 Estrutura do Projeto
```
analisador-lexico/
├── imgNfa              #Imagem gerada do nfa
│   ├── nfa.png
│   ├── nfa.doc    
├── ArquivosTeste       #Arquivos para testar o analisador
│   ├── teste1.txt
│   ├── teste2.txt
│   ├── teste3.txt
├── lex_analiser.py      #Arquivo a ser executado
├── nfa.py               #Arquivo para crianção de nfas
├── dfa_consersion.py    #Arquivo para converter nfa em dfa
└── README.md            #Arquivo de apresentação
```

---

## 🧩 Tabela de Tokens
| Tipo      | Regex        | Exemplo   |
| --------- | ------------ | --------- |
| SHOW      | `show`       | `show`    |
| TEXT      | `text`       | `text`    |
| NUM       | `num`        | `num`     |
| TRUE      | `true`       | `true`    |
| FALSE     | `false`      | `false`   |
| ADD       | `\+`         | `+`       |
| SUB       | `-`          | `-`       |
| MUL       | `\*`         | `*`       |
| DIV       | `/`          | `/`       |
| GT        | `>`          | `>`       |
| LT        | `<`          | `<`       |
| EQ        | `=`          | `=`       |
| SEMICOLON | `;`          | `;`       |
| STRING    | `\"[^\"]*\"` | `"texto"` |
| NUMBER    | `[0-9]+`     | `42`      |


---
