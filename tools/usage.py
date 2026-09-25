"""Tokens and time the rebuild took, read from Claude Code session transcripts.
  .venv/bin/python tools/usage.py <session.jsonl> [more.jsonl ...]  ->  analysis/usage.json
Each API response is counted once (a response is logged once per content block, so dedupe by message id)."""
import json, pathlib, sys
from datetime import datetime

R = pathlib.Path(__file__).resolve().parent.parent
seen, tok = set(), dict(input=0, cache_write=0, cache_read=0, output=0)
tools, prompts = 0, set()
stamps, models = [], {}
for path in sys.argv[1:]:
    for line in open(path):
        try: e = json.loads(line)
        except ValueError: continue
        ts = e.get('timestamp')
        if ts: stamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone())
        m = e.get('message') or {}
        # prompts: typed messages (plain or with images), plus ones sent mid-turn (logged as queued commands);
        # the summary written when the conversation is compacted is not a prompt
        c = m.get('content')
        if e.get('type') == 'user' and not e.get('isMeta'):
            if isinstance(c, list) and not any(isinstance(x, dict) and x.get('type') == 'tool_result' for x in c):
                c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
            if isinstance(c, str) and c.strip() and not c.startswith('This session is being continued'):
                prompts.add(c.strip()[:300])
        a = e.get('attachment') or {}
        if e.get('type') == 'attachment' and a.get('type') == 'queued_command' and isinstance(a.get('prompt'), str) \
                and not a['prompt'].lstrip().startswith('<task-notification'):          # background-task notices aren't prompts
            prompts.add(a['prompt'].strip()[:300])
        if e.get('type') != 'assistant' or not isinstance(m, dict): continue
        tools += sum(1 for c in m.get('content') or [] if isinstance(c, dict) and c.get('type') == 'tool_use')
        mid = m.get('id')
        if not mid or mid in seen or not m.get('usage'): continue
        seen.add(mid)
        u = m['usage']
        tok['input'] += u.get('input_tokens', 0) or 0
        tok['cache_write'] += u.get('cache_creation_input_tokens', 0) or 0
        tok['cache_read'] += u.get('cache_read_input_tokens', 0) or 0
        tok['output'] += u.get('output_tokens', 0) or 0
        models[m.get('model', '?')] = models.get(m.get('model', '?'), 0) + 1

stamps.sort()
gaps = [(b - a).total_seconds() for a, b in zip(stamps, stamps[1:])]
active = sum(g for g in gaps if g < 600)                 # time spent working; pauses over 10 min don't count
out = dict(
    day=stamps[0].strftime('%Y-%m-%d'), start=stamps[0].strftime('%H:%M'), end=stamps[-1].strftime('%H:%M'),
    wall_min=round((stamps[-1] - stamps[0]).total_seconds() / 60), active_min=round(active / 60),
    responses=len(seen), tool_calls=tools, prompts=len(prompts), models=models,
    tokens=dict(tok, total=sum(tok.values())),
)
(R / 'analysis' / 'usage.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps(out, indent=1))
