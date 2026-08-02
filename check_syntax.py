import io
import pathlib
import tokenize

src = pathlib.Path('app_complete.py').read_text(encoding='utf-8')
for token in tokenize.generate_tokens(io.StringIO(src).readline):
    if token.type == tokenize.NAME:
        pass
print('tokenize ok')
