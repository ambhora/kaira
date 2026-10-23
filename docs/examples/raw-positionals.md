---
title: Raw positionals
description: Using the -- delimiter to pass dash-leading words through as positional values, and how to pass the literal value --.
---

# Raw positionals

The exact word `--` ends option recognition at the current command level.
Every remaining word is a raw positional value of that command — even words
that look like options, subcommands, or further delimiters.

## Declaration

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira

command:
  help: Run another command.
  options:
    dry-run:
      flag:
        help: Show what would be run.

    output:
      scalar:
        value: string
        value_style: attached # (1)!
        help: Output file.

  tail:
    positionals:
      positionals:
        name: argument
        value: string
        min: 0
        max: unbounded
```

1.  Attached style is what allows this option to receive the literal value
    `--` later on this page.

## Verdicts

=== ":material-check-circle: Accepted"

    ```console
    $ kaira --dry-run -- --not-a-kaira-option build --help
    ```

    ```json
    {
      "program": "kaira",
      "command_path": [],
      "levels": [
        {
          "options": {"dry-run": true},
          "positionals": {"argument": ["--not-a-kaira-option", "build", "--help"]}
        }
      ]
    }
    ```

    Kaira does not read `--not-a-kaira-option` as an option, `build` as a
    subcommand, or `--help` as anything special.

    The delimiter may also follow earlier positional values, and a second
    `--` after the first is just another positional:

    ```console
    $ kaira input --dry-run -- --literal -- -2
    ```

    ```json
    {"options": {"dry-run": true}, "positionals": {"argument": ["input", "--literal", "--", "-2"]}}
    ```

    `dry-run` is parsed as a flag even though it appears after `input`.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `kaira --not-a-kaira-option` | `unknown_option` at 0 | Without `--`, a dash-leading word must be a declared option. |
    | `kaira build --dry-run --help` | `unknown_option` at 2 | `--help` is not declared; `build` is just a positional here. |
    | `kaira --output --` | `invalid_option_form` at 0 | `output` is `attached`; `--output` without `=` is the wrong form. |

## The literal value `--`

Because `output` uses `value_style: attached`, it can receive the literal
value `--`:

```console
$ kaira --output=--
```

```json
{"options": {"output": "--"}, "positionals": {"argument": []}}
```

A *spaced* option can never receive `--`: the delimiter check runs before
the value is consumed, so `--some-spaced-option --` is `missing_value` at
the option's index.

## `--` on a non-positional tail

If the current command has a `subcommands` (or `empty`) tail, `--` is an
error rather than a way to select a child. For this declaration:

```yaml
command:
  tail:
    subcommands:
      required: true
      commands:
        build:
          tail:
            empty: {}
```

this command line fails:

```console
$ kaira -- build        # unexpected_delimiter at 0
```

`--` tries to start raw positionals at the root, but the root accepts
subcommands, not positionals.
