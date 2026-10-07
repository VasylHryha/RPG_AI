"""Exactly three coupled resource-ceiling replacements on reproduced RD3."""
CEILINGS = {'CAP96': 96, 'CAP128': 128}
CONTEXTS = (
    "if sum(e[3]!='output' for e in elements)+1>64:return 'cap'",
    "return 'cost' if n+.1*pairs>64 else None",
    "while self.cost()>64:",
)

def apply_variant(source, variant):
    ceiling = CEILINGS[variant]
    for context in CONTEXTS:
        if source.count(context) != 1:
            raise ValueError('resource ceiling context mismatch: ' + context)
    import ast
    if sum(isinstance(n, ast.Constant) and type(n.value) is int and n.value == 64
           for n in ast.walk(ast.parse(source))) != 3:
        raise ValueError('RD3 does not contain exactly three 64 policy literals')
    for context in CONTEXTS:
        source = source.replace(context, context.replace('64', str(ceiling)))
    return source
