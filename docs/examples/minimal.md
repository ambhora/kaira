---
title: Minimal command
description: The smallest valid Kaira declaration - one root command that accepts nothing.
---

# Minimal command

The smallest document the schema accepts: a root command that accepts no
flags, options, subcommands, or positional words.

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira
commands:
  __main__:
    shape: none
```

| Command line | Outcome |
| --- | --- |
| `kaira` | accepted — `{"flags": [], "options": {}, "positionals": {}}` |
| `kaira extra` | `unexpected_argument` at 0 — `shape: none` accepts no bare words. |
| `kaira --verbose` | `unknown_option` at 0 — nothing is declared. |
| `kaira --` | `unexpected_delimiter` at 0 — `--` is meaningful only for `shape: positionals`. |

The full result for `kaira`:

```json
{
  "program": "kaira",
  "command": "__main__",
  "path": ["__main__"],
  "commands": {
    "__main__": {"flags": [], "options": {}, "positionals": {}}
  }
}
```
