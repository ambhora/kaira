---
title: Options
description: All four Kaira option kinds — flag, scalar, repeatable, and separated — in one build command, with mixed value styles.
---

# Options

This example shows all four option kinds: `flag`, `scalar`, `repeatable`,
and `separated`. It also shows that value-taking options choose exactly one
value style: `output` uses the attached style, while `include` and
`features` use the spaced style. For a page devoted to the attached style,
see [Attached values](attached-values.md).

## Declaration

```yaml title="kaira.korml"
version: kaira.command-declaration/v1
program: kaira

command:
  help: Build command.

  options:
    verbose:
      flag:
        short: v
        help: Print more information.

    output:
      scalar:
        short: o
        value: string
        value_style: attached # (1)!
        help: Output file.

    include:
      repeatable:
        value: string
        value_style: spaced # (2)!
        help: Include path.

    features:
      separated:
        value: string
        value_style: spaced
        separator: ";" # (3)!
        help: Semicolon-separated feature list.

  tail:
    positionals:
      positionals:
        name: target
        value: string
        min: 0
        max: unbounded
```

1.  `--output=FILE` and `-o=FILE` are accepted; `--output FILE` is not.
2.  `--include DIR` is accepted; `--include=DIR` is not.
3.  One occurrence, split on `;`. The shell must deliver the semicolons
    inside a single word, so quote the value.

## Verdicts

=== ":material-check-circle: Accepted"

    ```console
    $ kaira --verbose --output=build.log target
    $ kaira -v -o=build.log target
    $ kaira --include src --include include target
    $ kaira --features "mpi;cuda;openmp" target
    $ kaira target1 --verbose target2 --include src
    ```

    In the last line the positional values are `target1` and `target2`;
    `verbose` and `include` are recognized even though they follow a
    positional.

=== ":material-close-circle: Rejected"

    | Command line | Error | Why |
    | --- | --- | --- |
    | `kaira --verbose=true` | `invalid_option_form` at 0 | A flag never takes a value. |
    | `kaira --output build.log target` | `invalid_option_form` at 0 | `output` is `attached`; the spaced form is refused. |
    | `kaira --output=a.log --output=b.log` | `duplicate_option` at 1 | A scalar may appear at most once. |
    | `kaira --include=src target` | `invalid_option_form` at 0 | `include` is `spaced`; the attached form is refused. |
    | `kaira --features=mpi;cuda target` | `invalid_option_form` at 0 | `features` is `spaced`; the attached form is refused. |
    | `kaira --features mpi --features cuda` | `duplicate_option` at 2 | A separated option may appear at most once. |
    | `kaira -vo` | `unknown_option` at 0 | There is no short-option clustering. |
    | `kaira target --unknown-option` | `unknown_option` at 1 | Undeclared dash-leading words are errors anywhere in the level. |

=== ":material-code-json: Portable result"

    For

    ```console
    $ kaira --verbose --output=build.log --include src --include include --features "mpi;cuda" target
    ```

    a conformant parser produces:

    ```json
    {
      "program": "kaira",
      "command_path": [],
      "levels": [
        {
          "options": {
            "verbose": true,
            "output": "build.log",
            "include": ["src", "include"],
            "features": ["mpi", "cuda"]
          },
          "positionals": {"target": ["target"]}
        }
      ]
    }
    ```

!!! tip "Passing a dash-leading word as a positional"

    `kaira target --unknown-option` fails because `--unknown-option` is read
    as an option. Put `--` before it to pass it through literally:
    `kaira target -- --unknown-option`. See [Raw positionals](raw-positionals.md).
