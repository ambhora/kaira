---
title: Attached values
description: Options declared with value_style attached — scalar, repeatable, and separated — and the shell quoting they sometimes need.
---

# Attached value style

This example declares every value-taking option with
`value_style: attached`. The attached style accepts a value only in the same
`argv` word as the option name:

```text
--name=value     ✓
--name value     ✗  invalid_option_form
```

## Declaration

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira

command:
  help: Build command using attached option values.

  options:
    output:
      scalar:
        value: string
        value_style: attached
        help: Output file.

    define:
      repeatable:
        value: string
        value_style: attached
        help: Compile-time definition interpreted by the application. # (1)!

    features:
      separated:
        value: string
        value_style: attached
        separator: ";"
        help: Semicolon-separated feature list.

  tail:
    positionals:
      positionals:
        name: target
        value: string
        min: 0
        max: unbounded
```

1.  Kaira delivers `USE_MPI=1` as one string. Only the **first** `=` in a
    word separates the option name from its value; the rest is the value.

## Verdicts

=== ":material-check-circle: Accepted"

    ```console
    $ kaira --output=build.log target
    $ kaira --define=USE_MPI=1 --define=USE_CUDA=1 target
    $ kaira --features='mpi;cuda;openmp' target
    $ kaira --output= target
    ```

    The third line is quoted for the shell's benefit only. The word that
    reaches Kaira is `--features=mpi;cuda;openmp`. The fourth line passes
    an **empty** string as `output`, which is valid for a `string` value.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `kaira --output build.log target` | `invalid_option_form` at 0 | `output` is `attached`; the spaced form is refused. |
    | `kaira --define USE_MPI=1 target` | `invalid_option_form` at 0 | Same rule for `define`. |
    | `kaira --features "mpi;cuda;openmp" target` | `invalid_option_form` at 0 | Same rule for `features`. |
    | `kaira --features=mpi --features=cuda target` | `duplicate_option` at 1 | A separated option may appear at most once; pass one separated value. |

=== ":material-code-json: Portable result"

    For

    ```console
    $ kaira --output=build.log --define=USE_MPI=1 --define=USE_CUDA=1 --features='mpi;cuda' target
    ```

    a conformant parser produces:

    ```json
    {
      "program": "kaira",
      "command_path": [],
      "levels": [
        {
          "options": {
            "output": "build.log",
            "define": ["USE_MPI=1", "USE_CUDA=1"],
            "features": ["mpi", "cuda"]
          },
          "positionals": {"target": ["target"]}
        }
      ]
    }
    ```

!!! note "Why the attached style exists"

    An attached option can carry the literal delimiter (`--output=--`),
    which a spaced option never can, and it expresses an empty value
    (`--output=`) without relying on the shell to pass an empty word. It
    also keeps the binding visible in scripts and shell history, since the
    value can never be mistaken for a separate positional word.
