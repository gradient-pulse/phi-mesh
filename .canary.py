import pathlib,sys
p=pathlib.Path('generate_graph_data.py').read_text(encoding='utf-8')
ok='def canon_tag(' in p
print('[GEN] canon_tag present:', ok)
raise SystemExit(0 if ok else 3)
