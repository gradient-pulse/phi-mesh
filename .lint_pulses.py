import sys, re, glob, yaml, os
bad = 0
fname_re = re.compile(r'^\d{4}-\d{2}-\d{2}_')
date_re  = re.compile(r'^\d{4}-\d{2}-\d{2}$')
for path in sorted(glob.glob('pulse/_buildview/*.yml')):
    base = os.path.basename(path)
    if not fname_re.match(base):
        print(f"Bad filename '{base}' (must start YYYY-MM-DD_)")
        bad += 1
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f'YAML parse error in {base}: {e}')
        bad += 1
        continue
    # required minimal fields
    for k in ('title','tags'):
        if k not in data:
            print(f"Missing '{k}' in {base}")
            bad += 1
    # if a YAML 'date' exists, it must be valid, but it's optional
    d = str(data.get('date','')).strip()
    if d and not date_re.match(d):
        print(f"Bad YAML date '{d}' in {base} (YYYY-MM-DD expected)")
        bad += 1
if bad:
    print(f'FAILED: {bad} problems.')
    sys.exit(2)
print('Pulses validated (filename date strategy).')
