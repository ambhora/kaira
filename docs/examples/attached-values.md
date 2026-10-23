---
title: Attached values
description: Options declared with style attached - single, multiple, and separator - and the shell quoting they sometimes need.
---

# Attached values

Every option here uses `style: attached`: the value follows the first `=`
in the same `argv` word. `--name value` is refused with
`invalid_option_form`.

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira
commands:
  __main__:
    shape: positionals
    options:
      output:   {style: attached}
      define:   {style: attached, multiplicity: multiple}                  # (1)!
      features: {style: attached, multiplicity: multiple, separator: ";"}
    positionals:
      - target: {alignment: center, multiplicity: multiple, required: false}
```

1.  Kaira delivers `USE_MPI=1` as one string. Only the **first** `=` in a
    word separates the option name from its value; the rest is the value.

| Command line | Outcome |
| --- | --- |
| `kaira --output=build.log target` | accepted |
| `kaira --define=USE_MPI=1 --define=USE_CUDA=1 target` | accepted — `"define": ["USE_MPI=1", "USE_CUDA=1"]` |
| `kaira --features='mpi;cuda;openmp' target` | accepted — the quotes are for the shell; the word that reaches Kaira is `--features=mpi;cuda;openmp` |
| `kaira --output= target` | accepted — `"output": ""`; an empty value is valid for `string` |
| `kaira --output build.log target` | `invalid_option_form` at 0 — `output` is `attached` |
| `kaira --define USE_MPI=1 target` | `invalid_option_form` at 0 — same rule for `define` |
| `kaira --features "mpi;cuda;openmp" target` | `invalid_option_form` at 0 — same rule for `features` |
| `kaira --features=mpi --features=cuda target` | `duplicate_option` at 1 — a separator option occurs at most once; pass one separated value |

For `kaira --output=build.log --define=USE_MPI=1 --define=USE_CUDA=1 --features='mpi;cuda' target`
the record for `__main__` is:

```json
{
  "flags": [],
  "options": {
    "output": "build.log",
    "define": ["USE_MPI=1", "USE_CUDA=1"],
    "features": ["mpi", "cuda"]
  },
  "positionals": {"target": ["target"]}
}
```

An attached option can carry the literal delimiter (`--output=--`), which a
spaced option never can, and it expresses an empty value (`--output=`)
without relying on the shell to pass an empty word.
