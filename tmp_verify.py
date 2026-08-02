import pathlib, tokenize, io
src = pathlib.Path('app_complete.py').read_text(encoding='utf-8')
list(tokenize.generate_tokens(io.StringIO(src).readline))
print('tokenize ok')
