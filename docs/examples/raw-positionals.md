---
title: Raw positionals
description: Using the -- delimiter to pass dash-leading words through as positional values, and how to pass the literal value --.
---

# Raw positionals

The exact word `--` ends option recognition at the current command level.
Every remaining word is a positional word of that command — even words
that look like options, subcommands, or further delimiters.

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira
commands:
  __main__:
    shape: positionals
    flags:
      dry-run: {}
    options:
      output: {style: attached}    # (1)!
    positionals:
      - argument: {alignment: center, multiplicity: multiple, required: false}
```

1.  The attached style is what allows this option to receive the literal
    value `--` below.

| Command line | Outcome |
| --- | --- |
| `kaira --dry-run -- --not-a-kaira-option build --help` | accepted — see below; nothing after `--` is read as an option or subcommand |
| `kaira input --dry-run -- --literal -- -2` | accepted — `"argument": ["input", "--literal", "--", "-2"]`; the flag is parsed although it follows `input`, and a second `--` is just a word |
| `kaira --output=--` | accepted — `"output": "--"` |
| `kaira --not-a-kaira-option` | `unknown_option` at 1 — without `--`, a dash-leading word must be declared |
| `kaira build --dry-run --help` | `unknown_option` at 3 — `--help` is not declared; `build` is just a positional word here |
| `kaira --output --` | `invalid_option_form` at 1 — `output` is `attached`; `--output` without `=` is the wrong form |

For the first line:

```json
{
  "flags": ["dry-run"],
  "options": {},
  "positionals": {"argument": ["--not-a-kaira-option", "build", "--help"]}
}
```

A *spaced* option can never receive `--`: the delimiter check runs before
the value is consumed, so `--some-spaced-option --` is `missing_value` at
the option's index.

If the current command has `shape: subcommands` or `none`, `--` is
`unexpected_delimiter`; it never selects a child. In particular
`kaira -- build` fails for a root whose shape is `subcommands`.
