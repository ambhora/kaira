---
title: Minimal command
description: The smallest valid Kaira declaration — a command with no options, no subcommands, and no positional arguments.
---

# Minimal command

This declaration describes a command with no options, no subcommands, and
no positional arguments. It is the smallest document the schema accepts.

## Declaration

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira

command:
  help: Minimal Kaira command. # (1)!
  tail:
    empty: {}
```

1.  `help` is metadata. Kaira does not generate `--help` from it; the
    application decides whether and how to show it.

## Verdicts

=== ":material-check-circle: Accepted"

    ```console
    $ kaira
    ```

    ```json
    {
      "program": "kaira",
      "command_path": [],
      "levels": [
        {"options": {}, "positionals": null}
      ]
    }
    ```

    Even with nothing to report, the root level is present and
    `positionals` is `null` because the tail is not `positionals`.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `kaira extra` | `unexpected_argument` at 0 | An `empty` tail accepts no bare words. |
    | `kaira --verbose` | `unknown_option` at 0 | No options are declared. |
    | `kaira --` | `unexpected_delimiter` at 0 | `--` is meaningful only on a `positionals` tail. |
