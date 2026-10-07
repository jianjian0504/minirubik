#!/usr/bin/env python3
"""Measure all distance-11 cases with the user's verified Ripes CLI.
Standard library only. Safe to interrupt and resume with matching inputs/build.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

FIELDS = ['state', 'solution_length', 'retired_instructions',
          'model_execution_ms', 'process_wall_seconds', 'status',
          'host_exit_code', 'guest_exit_code']
NAMES = ['R', 'R2', "R'", 'B', 'B2', "B'", 'D', 'D2', "D'"]
SOURCE = [[1,4,2,0,3,5,6], [0,1,2,4,5,6,3], [0,2,5,3,1,4,6]]
TWIST = [[1,2,0,2,1,0,0], [0,0,0,1,2,1,2], [0,0,0,0,0,0,0]]

def replay(state, moves):
    p = [int(x)-1 for x in state[:7]]
    o = [int(x)-1 for x in state[7:]]
    for token in moves:
        move = NAMES.index(token)
        face = move // 3
        for _ in range(move % 3 + 1):
            p = [p[j] for j in SOURCE[face]]
            o = [(o[j] + TWIST[face][i]) % 3
                 for i, j in enumerate(SOURCE[face])]
    return p == list(range(7)) and o == [0]*7

def parse_output(output):
    # Qt/console output may contain ANSI sequences, carriage returns or NULs.
    output = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', output)
    output = re.sub(r'\x1b\][^\x07]*(?:\x07|\x1b\\)', '', output)
    output = ''.join(c if c in '\n\r\t' or not unicodedata.category(c).startswith('C')
                     else ' ' for c in output)
    output = output.replace('’', "'").replace('′', "'")
    def stat(header):
        m = re.search(r'^=+\s*' + header + r'\s*\r?\n\s*([\d,]+)',
                      output, re.M | re.I)
        return int(m.group(1).replace(',', '')) if m else None
    count = stat(r'instructions retired')
    model_ms = stat(r'wall-clock model execution time \(ms\)')
    # Extract bounded move tokens rather than requiring a whole line to contain
    # only moves. runinfo/statistics contain no such standalone tokens.
    moves = re.findall(r"(?<![A-Za-z0-9_])[RBD](?:2|')?(?![A-Za-z0-9_'])", output)
    return count, model_ms, moves or None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripes', required=True)
    ap.add_argument('--source', default='solver-cli-fixed.s')
    ap.add_argument('--states', default='tests/hard11.txt')
    ap.add_argument('--output', default='ripes-hard.csv')
    ap.add_argument('--timeout', type=int, default=180)
    ap.add_argument('--limit', type=int, help='Optional short pilot; not full validation')
    args = ap.parse_args()
    binary = Path(args.ripes).expanduser().resolve()
    source = Path(args.source).resolve()
    states_path = Path(args.states).resolve()
    for path in [binary, source, states_path]:
        if not path.is_file():
            raise SystemExit('File not found: ' + str(path))
    states = [s.strip() for s in states_path.read_text().splitlines() if s.strip()]
    if len(states) != 2644 or len(set(states)) != 2644:
        raise SystemExit('Expected exactly 2,644 distinct states in tests/hard11.txt.')
    for s in states:
        if (len(s) != 14 or sorted(s[:7]) != list('1234567')
            or any(c not in '123' for c in s[7:])
            or sum(int(c)-1 for c in s[7:]) % 3):
            raise SystemExit('Invalid state in list: ' + s)
    if args.limit is not None:
        if args.limit <= 0:
            raise SystemExit('--limit must be positive')
        selected = states[:args.limit]
    else:
        selected = states
    base = source.read_text()
    pattern = r'(input_state:\s*\.asciz\s*")[^"]+(\")'
    if len(re.findall(pattern, base)) != 1:
        raise SystemExit('Expected one input_state .asciz declaration.')
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    meta_file = output.with_suffix(output.suffix + '.meta.json')
    log_dir = output.parent / (output.stem + '-logs')
    log_dir.mkdir(exist_ok=True)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    metadata = {'binary_sha256': sha(binary), 'source_sha256': sha(source),
                'states_sha256': sha(states_path), 'processor': 'RV32_ISS',
                'iret_budget': 50000000, 'cli': '-t asm --iret --exectime --runinfo'}
    previous = {}
    if output.exists():
        if not meta_file.exists() or json.loads(meta_file.read_text()) != metadata:
            raise SystemExit('Build/source differs from existing CSV. Use a new --output filename.')
        with output.open(newline='') as f:
            for row in csv.DictReader(f):
                if row.get('status') == 'PASS' and row.get('state') in states:
                    previous[row['state']] = row
    meta_file.write_text(json.dumps(metadata, indent=2) + '\n')
    print('Processor: RV32_ISS; no renderer; budget: 50,000,000 instructions per state.', flush=True)
    print('Cases selected: %d; saved passing cases: %d.' % (len(selected), len(previous)), flush=True)
    current_source = log_dir / 'current.s'
    with output.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for state in states:
            if state in previous:
                writer.writerow(previous[state])
        f.flush()
        for index, state in enumerate(selected, 1):
            if state in previous:
                continue
            current_source.write_text(re.sub(pattern,
                lambda m: m.group(1) + state + m.group(2), base, count=1))
            command = [str(binary), '--mode', 'cli', '--src', str(current_source),
                       '-t', 'asm', '--proc', 'RV32_ISS', '--iret', '--exectime', '--runinfo']
            start = time.perf_counter()
            try:
                result = subprocess.run(command, capture_output=True, text=True,
                                        timeout=args.timeout)
                text = result.stdout + '\n' + result.stderr
                code = result.returncode
            except subprocess.TimeoutExpired as exc:
                text = 'TIMEOUT: ' + str(exc)
                code = -1
            elapsed = time.perf_counter() - start
            (log_dir / (state + '.txt')).write_text(text + '\nHost process exit code: ' + str(code) + '\n')
            count, model_ms, moves = parse_output(text)
            length = len(moves) if moves is not None else None
            guest_match = re.search(r'Program exited with code:\s*(-?\d+)', text)
            guest_code = int(guest_match.group(1)) if guest_match else None
            status = 'PASS'
            if (code < 0 or guest_code != 0 or 'PASS: path reaches solved state' not in text
                or count is None or model_ms is None or moves is None):
                status = 'CHECK_LOG'
            elif length != 11 or not replay(state, moves):
                status = 'BAD_SOLUTION'
            elif count > 50000000:
                status = 'OVER_BUDGET'
            row = dict(zip(FIELDS, [state, length, count, model_ms,
                                   '%.6f' % elapsed, status, code, guest_code]))
            writer.writerow(row)
            f.flush()
            print('%d/%d  %s  instructions=%s  model_ms=%s  %s' %
                  (index, len(selected), state, count, model_ms, status), flush=True)
            if status != 'PASS':
                raise SystemExit('Stopped: host_exit=%s guest_exit=%s moves=%r. Inspect log: %s' % (code, guest_code, moves, log_dir / (state + '.txt')))
            previous[state] = row
    worst = max(previous.values(), key=lambda row: int(row['retired_instructions']))
    print('\nSaved PASS cases: %d/2644' % len(previous), flush=True)
    print('Worst observed: %s; instructions=%s' %
          (worst['state'], worst['retired_instructions']), flush=True)
    print('CSV: ' + str(output), flush=True)
    if len(previous) == 2644:
        print('ALL 2644 CASES PASS: every shortest path replays correctly and is within budget.', flush=True)
    else:
        print('Partial run only. Run again without --limit for full validation.', flush=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted. Re-run the same command to resume saved PASS cases.', file=sys.stderr)
        sys.exit(130)
