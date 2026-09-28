import ast
import importlib
import json
import sys

class Python:
    ast_transformers = []


with open('pres.ipynb') as f:
    doc = json.load(f)

cells = [cell['source'] for cell in doc['cells'] if cell['cell_type'] == 'code']
ipython = Python()

with open('run.py', 'w') as f:
    if len(sys.argv) > 1 and sys.argv[1] == '--no-input':
        print('input = lambda *a, **k: None', file=f)

    for cell in cells:
        writefile = None
        content = []
        for line in cell:
            if line.startswith('%load_ext '):
                module_name = line.removeprefix('%load_ext ').strip()
                module = importlib.import_module(module_name)
                module.load_ipython_extension(ipython)
            elif line.startswith('%%writefile '):
                writefile = line.removeprefix('%%writefile ').strip()
            else:
                content.append(line)

        print('print("===")', file=f)
        print('print("""', file=f)
        print(''.join(cell), file=f)
        print('""".strip())', file=f)
        print('print("===")', file=f)

        print('input()', file=f)

        if writefile:
            print(f'with open({writefile!r}, "w") as f:', file=f)
            print(f'    print({''.join(content)!r}, file=f)', file=f)
        else:
            tree = ast.parse(''.join(content))
            for transformer in ipython.ast_transformers:
                tree = transformer.visit(tree)
            print(ast.unparse(tree), file=f)
