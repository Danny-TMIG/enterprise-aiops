"""Emit concrete code from a CAPProgram."""

from __future__ import annotations

from app.reconfig.codeal import CAProgram


def emit_python(prog: CAProgram) -> str:
    lines = [f"# code-al → python: {prog.name}",
             f"# hash: {prog.hash()}",
             ""]
    lines.append("def run(env):")
    lines.append("    state = {}")
    for ins in prog.instructions:
        slots = ins.slots
        match ins.op:
            case "COUNT":
                src = slots.get("in0", "input")
                out = slots.get("out0", "count")
                lines.append(f"    state['{out}'] = len(env['{src}'].split())")
            case "STORE":
                src = slots.get("in0", "count")
                tgt = slots.get("target", "memory")
                lines.append(f"    env.get('store_{tgt}', env.setdefault)('{src}', state.get('{src}'))")
            case "TRAIN":
                lines.append("    state['model'] = env['trainer'].fit(env.get('data', []))")
            case "EVALUATE":
                lines.append("    state['metrics'] = env['evaluator'](state['model'])")
            case "SCHEDULE":
                every = slots.get("every", "daily")
                lines.append(f"    state['schedule'] = '{every}'")
            case "FETCH":
                lines.append("    state['events'] = env['source'].read()")
            case "FILTER":
                by = slots.get("by", "key")
                lines.append(f"    state['matched'] = [e for e in state['events'] if e.get('{by}')]")
            case "ROUTE":
                to = slots.get("to", "slack")
                lines.append(f"    state['routed'] = env['router'].send('{to}', state['matched'])")
            case "RECORD":
                lines.append("    env['evidence'].record(state.get('routed', state))")
            case _:
                lines.append(f"    # op {ins.op} slots={slots}")
    lines.append("    return state")
    if prog.residue:
        lines.append("")
        lines.append("# residue (carried, not claimed):")
        for r in prog.residue:
            lines.append(f"#   ⊘ {r}")
    return "\n".join(lines)


def emit_sql(prog: CAProgram) -> str:
    lines = [f"-- code-al → sql: {prog.name}",
             f"-- hash: {prog.hash()}",
             ""]
    for ins in prog.instructions:
        s = ins.slots
        match ins.op:
            case "STORE":
                tgt = s.get("target", "memory")
                lines.append(f"CREATE TABLE IF NOT EXISTS {tgt}_records (")
                lines.append("  id SERIAL PRIMARY KEY,")
                lines.append("  payload JSONB NOT NULL,")
                lines.append("  recorded_at TIMESTAMPTZ DEFAULT now()")
                lines.append(");")
            case "COUNT":
                lines.append("-- COUNT: computed in application layer")
            case "FETCH":
                lines.append("SELECT * FROM source_events;")
            case "FILTER":
                by = s.get("by", "key")
                lines.append(f"SELECT * FROM source_events WHERE payload ? '{by}';")
            case _:
                lines.append(f"-- op {ins.op}: {s}")
    return "\n".join(lines)


def emit_mql(prog: CAProgram) -> str:
    lines = [f"// code-al → mql: {prog.name}",
             f"// hash: {prog.hash()}",
             ""]
    for ins in prog.instructions:
        s = ins.slots
        match ins.op:
            case "STORE":
                lines.append(f'db.{s.get("target","memory")}.insertOne(payload);')
            case "FETCH":
                lines.append("const events = await db.events.find({}).toArray();")
            case "FILTER":
                by = s.get("by", "key")
                lines.append(f'const matched = events.filter(e => e["{by}"]);')
            case "ROUTE":
                to = s.get("to", "slack")
                lines.append(f'await router.send("{to}", matched);')
            case "RECORD":
                lines.append("await db.evidence.insertOne({ matched, ts: new Date() });")
            case _:
                lines.append(f"// op {ins.op}: {s}")
    return "\n".join(lines)


def emit_rl(prog: CAProgram) -> str:
    """Reward spec derived from the evidence_required slots."""
    return (
        f"# code-al → rl spec: {prog.name}\n"
        f"# hash: {prog.hash()}\n"
        "\n"
        "reward_spec = {\n"
        '  "terms": [\n'
        '    {"name": "task_success", "weight": 1, "source": "env.done"},\n'
        '    {"name": "evidence", "weight": 1, "source": "env.evidence_count"},\n'
        '    {"name": "cost", "weight": -0.1, "source": "env.cost"},\n'
        "  ],\n"
        '  "terminal": "env.done",\n'
        "}\n"
    )


def emit_all(prog: CAProgram) -> dict[str, str]:
    return {
        "python": emit_python(prog),
        "sql":    emit_sql(prog),
        "mql":    emit_mql(prog),
        "rl":     emit_rl(prog),
    }
