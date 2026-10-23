---
title: Writing a declaration
description: An incremental guide to Kaira declarations, from an empty command to a nested command tree, with the argument vectors each step accepts and rejects.
---

# Writing a declaration

This page develops a declaration for a hypothetical build tool, `forge`,
from an empty command to a nested command tree. Each step shows the
declaration, accepted argument vectors with their results, and rejected
argument vectors with the resulting error code and index.

## Step 1 — The smallest possible program

A declaration always has three root fields. A command always has exactly
one tail mode. `empty` means "no further arguments".

```yaml title="forge.korml"
version: kaira.command-declaration/v1
program: forge
command:
  tail:
    empty: {}
```

=== ":material-check-circle: Accepted"

    ```console
    $ forge
    ```

    ```json
    {
      "program": "forge",
      "command_path": [],
      "levels": [{"options": {}, "positionals": null}]
    }
    ```

=== ":material-close-circle: Rejected"

    ```console
    $ forge now
    ```

    ```json
    {"code": "unexpected_argument", "index": 0}
    ```

    An `empty` tail accepts no bare words at all.

## Step 2 — Add a flag

Options live under `options`. A `flag` takes no value, and its short alias
exists only because we declared it.

```yaml title="forge.korml" hl_lines="4-7"
version: kaira.command-declaration/v1
program: forge
command:
  options:
    verbose:
      flag:
        short: v
  tail:
    empty: {}
```

=== ":material-check-circle: Accepted"

    ```console
    $ forge -v
    $ forge --verbose
    ```

    Both produce `"options": {"verbose": true}`. The result always uses the
    long name.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `forge --verbose=true` | `invalid_option_form` at 0 | A flag never takes a value. |
    | `forge -v --verbose` | `duplicate_option` at 1 | Long and short spellings count as the same option. |
    | `forge --verb` | `unknown_option` at 0 | There is no prefix matching. |

## Step 3 — Options that take a value

Every value-taking option declares **one** value style. `spaced` means the
value is the next word; `attached` means it follows `=` in the same word.
The two forms are never interchangeable.

```yaml title="forge.korml" hl_lines="8-16"
version: kaira.command-declaration/v1
program: forge
command:
  options:
    verbose:
      flag:
        short: v
    jobs:
      scalar:
        value: int
        value_style: attached
    include:
      repeatable:
        value: string
        value_style: spaced
  tail:
    empty: {}
```

=== ":material-check-circle: Accepted"

    ```console
    $ forge --jobs=8 --include src --include tests
    ```

    ```json
    {
      "program": "forge",
      "command_path": [],
      "levels": [
        {
          "options": {"jobs": "8", "include": ["src", "tests"]},
          "positionals": null
        }
      ]
    }
    ```

    Note that `jobs` is `"8"`, a string. Integers keep their original text so
    that no host language can round or overflow them.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `forge --jobs 8` | `invalid_option_form` at 0 | `jobs` is `attached`; the spaced form is refused. |
    | `forge --include=src` | `invalid_option_form` at 0 | `include` is `spaced`; the attached form is refused. |
    | `forge --jobs=08` | `invalid_value` at 0 | `int` has no leading zeros. |
    | `forge --jobs=4 --jobs=8` | `duplicate_option` at 1 | A `scalar` may appear at most once. |

## Step 4 — Positional values

Switch the tail to `positionals` to accept bare words. Options and
positionals may now be interleaved freely.

```yaml title="forge.korml" hl_lines="17-22"
version: kaira.command-declaration/v1
program: forge
command:
  options:
    verbose:
      flag:
        short: v
    jobs:
      scalar:
        value: int
        value_style: attached
    include:
      repeatable:
        value: string
        value_style: spaced
  tail:
    positionals:
      positionals:
        name: target
        value: string
        min: 1
        max: unbounded
```

=== ":material-check-circle: Accepted"

    ```console
    $ forge app -v docs --include src
    ```

    ```json
    {
      "program": "forge",
      "command_path": [],
      "levels": [
        {
          "options": {"verbose": true, "include": ["src"]},
          "positionals": {"target": ["app", "docs"]}
        }
      ]
    }
    ```

    Options that appear *after* a positional are still options.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `forge` | `too_few_positionals` at 0 | `min: 1` is checked at end of input. |
    | `forge app --clean` | `unknown_option` at 1 | Dash-leading words are always options unless `--` came first. |

## Step 5 — Pass arbitrary words through with `--`

The exact word `--` turns off option recognition for the rest of the level.
Everything after it is a positional value, even if it starts with a dash.

=== ":material-check-circle: Accepted"

    ```console
    $ forge app -- --clean -j8
    ```

    ```json
    {"options": {}, "positionals": {"target": ["app", "--clean", "-j8"]}}
    ```

=== ":material-close-circle: Rejected"

    ```console
    $ forge --include --
    ```

    ```json
    {"code": "missing_value", "index": 0}
    ```

    A spaced option never consumes `--` as its value. An option that must
    accept the literal value `--` is declared `attached` and written `--name=--`.

## Step 6 — Subcommands and scopes

A `subcommands` tail selects a child command. The child opens its **own**
level with its **own** option scope.

```yaml title="forge.korml"
version: kaira.command-declaration/v1
program: forge
command:
  options:
    verbose:
      flag:
        short: v
  tail:
    subcommands:
      required: true
      commands:
        build:
          options:
            release:
              flag: {}
          tail:
            positionals:
              positionals:
                name: target
                value: string
        clean:
          tail:
            empty: {}
```

=== ":material-check-circle: Accepted"

    ```console
    $ forge -v build --release app
    ```

    ```json
    {
      "program": "forge",
      "command_path": ["build"],
      "levels": [
        {"options": {"verbose": true}, "positionals": null},
        {"options": {"release": true}, "positionals": {"target": ["app"]}}
      ]
    }
    ```

    One entry in `levels` per command level, root first.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `forge build -v app` | `unknown_option` at 1 | `verbose` belongs to the root; it is unknown inside `build`. |
    | `forge --release build` | `unknown_option` at 0 | `release` belongs to `build`; it is unknown at the root. |
    | `forge` | `missing_subcommand` at 0 | The tail is `required: true`. |
    | `forge deploy` | `unknown_subcommand` at 0 | Only declared children are accepted. |

## Further reading

- [Command-line grammar](../explanation/grammar.md) describes levels,
  scopes, and tail modes.
- The [KORML schema](../reference/schema.md) and
  [parser rules](../reference/parser-rules.md) summarize the
  [normative specification](../reference/specification.md).
- Each [example](../examples/index.md) is a complete declaration with
  accepted and rejected argument vectors.
