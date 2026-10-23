---
title: Positional slots
description: Two positional slots - a variable centre slot and a fixed right slot - and how words are assigned to them.
---

# Positional slots

A copy-like command: one or more sources followed by exactly one
destination. The sources vary in number, so that slot is aligned `center`;
the destination has a fixed count, so it may be aligned `right`.

```yaml title="cp.korml"
version: kaira.command-declaration/v1
program: cp
commands:
  __main__:
    shape: positionals
    flags:
      recursive: {short: r}
    positionals:
      - source:      {alignment: center, multiplicity: multiple}   # (1)!
      - destination: {alignment: right}                           # (2)!
```

1.  `multiple` and `required` (the default): one or more words.
2.  `single` and `required`: exactly one word, taken from the right end.

Assignment happens at end of input: the fixed slot takes its one word from
the right, and the centre slot takes everything else.

| Command line | Outcome |
| --- | --- |
| `cp a.txt b.txt dist/` | accepted — `"source": ["a.txt", "b.txt"], "destination": "dist/"` |
| `cp -r src dist/` | accepted — `"flags": ["recursive"]`, `"source": ["src"]`, `"destination": "dist/"` |
| `cp a.txt -- -x dist/` | accepted — `"source": ["a.txt", "-x"]`; `--` lets a dash-leading word be a source |
| `cp dist/` | `too_few_positionals` at 1 — one word fills `destination`; `source` needs at least one |
| `cp src -r` | `too_few_positionals` at 2 — `-r` is a flag, so only one positional word was seen |

For the first line:

```json
{
  "flags": [],
  "options": {},
  "positionals": {"source": ["a.txt", "b.txt"], "destination": "dist/"}
}
```

Why the restriction to one variable slot: if both `source` and
`destination` could vary, `cp a b c` would have two valid readings. With
`left` and `right` slots fixed, the centre count is determined by the
number of words, and a declaration that breaks this rule — a `left` or
`right` slot with `multiplicity: multiple` but no fixed `cardinality`, or
two `center` slots — is rejected as `invalid_declaration`.
