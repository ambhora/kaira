---
title: Options
description: A flag and the three option multiplicities - single, multiple, and multiple with separator - in one command, with mixed value styles.
---

# Options

One flag and three options, one per multiplicity. The options deliberately
mix value styles: `output` is `attached`, `include` and `features` are
`spaced`. [Attached values](attached-values.md) shows the attached style
throughout.

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira
commands:
  __main__:
    shape: positionals
    flags:
      verbose: {short: v}
    options:
      output:   {short: o, value: string, style: attached}                              # (1)!
      include:  {value: string, style: spaced, multiplicity: multiple}                  # (2)!
      features: {value: string, style: spaced, multiplicity: multiple, separator: ";"}  # (3)!
    positionals:
      - target: {alignment: center, value: string, multiplicity: multiple, required: false}
```

1.  `--output=FILE` and `-o=FILE` are accepted; `--output FILE` is not.
2.  `--include DIR` may be repeated; `--include=DIR` is not accepted.
3.  One occurrence, split on `;`. The shell must deliver the semicolons
    inside a single word, so quote the value.

| Command line | Outcome |
| --- | --- |
| `kaira --verbose --output=build.log target` | accepted |
| `kaira -v -o=build.log target` | accepted — same as the previous line |
| `kaira --include src --include include target` | accepted — `"include": ["src", "include"]` |
| `kaira --features "mpi;cuda;openmp" target` | accepted — `"features": ["mpi", "cuda", "openmp"]` |
| `kaira target1 --verbose target2 --include src` | accepted — `"positionals": {"target": ["target1", "target2"]}`; flags and options may follow positional words |
| `kaira --verbose=true` | `invalid_option_form` at 0 — a flag never takes a value |
| `kaira --output build.log target` | `invalid_option_form` at 0 — `output` is `attached` |
| `kaira --output=a.log --output=b.log` | `duplicate_option` at 1 — a `single` option occurs at most once |
| `kaira --include=src target` | `invalid_option_form` at 0 — `include` is `spaced` |
| `kaira --features=mpi;cuda target` | `invalid_option_form` at 0 — `features` is `spaced` |
| `kaira --features mpi --features cuda` | `duplicate_option` at 2 — a separator option occurs at most once |
| `kaira -vo` | `unknown_option` at 0 — no short-option clustering |
| `kaira target --unknown-option` | `unknown_option` at 1 — undeclared dash-leading words are errors anywhere in the level; put `--` before such a word to pass it through |

For `kaira --verbose --output=build.log --include src --include include --features "mpi;cuda" target`:

```json
{
  "program": "kaira",
  "command": "__main__",
  "path": ["__main__"],
  "commands": {
    "__main__": {
      "flags": ["verbose"],
      "options": {
        "output": "build.log",
        "include": ["src", "include"],
        "features": ["mpi", "cuda"]
      },
      "positionals": {"target": ["target"]}
    }
  }
}
```
