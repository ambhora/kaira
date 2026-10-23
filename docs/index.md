---
title: Kaira
description: A deterministic, language-independent specification for declaring and parsing command-line interfaces.
hide:
  - navigation
  - toc
---

<div class="kaira-intro" markdown>

# Kaira

Kaira is a specification for declaring command-line interfaces and for
interpreting argument vectors against such declarations. A declaration is
written in KORML and describes a program's command tree: its options,
subcommands, and positional arguments. The specification fixes the
declaration format, its validation rules, the interpretation procedure, and
a portable result representation, so that independent implementations in
different languages produce identical results and error codes for identical
inputs.

</div>

<div class="grid kaira-columns" markdown>

<div markdown>

### Properties

Determinism
:   The outcome depends on the declaration and the argument vector alone;
    there is no abbreviation, clustering, or implicit alias.
    ([Design goals](explanation/design-goals.md))

Value portability
:   `int` and `float` values are validated lexically and kept as text, so
    results do not depend on host numeric types.
    ([Results](reference/results.md))

Scoped command levels
:   Each subcommand opens a new level with its own options; nothing is
    inherited. ([Grammar](explanation/grammar.md))

Conformance
:   A shared vector file fixes the expected result or error for each case.
    ([Conformance suite](reference/results.md#conformance-suite))

</div>

<div markdown>

### Scope

**Specified:** the KORML declaration format and its validation; per-level
interpretation of options, subcommands, and positionals; the portable result
and error codes; four primitive value types with exact lexical grammars; a
language-neutral conformance suite.

**Out of scope:** implementation APIs; shell tokenization and quoting;
diagnostic messages and help output; application-level types such as paths
or dates; default values, environment variables, and configuration files.

</div>

</div>

## Overview

<figure class="kaira-figure" markdown>
![Using Kaira in a program: write a declaration once; at start-up load it with a Kaira library, pass argv, and receive either a typed result consumed by application logic or an error with a code and argv index.](assets/images/usage-flow.svg)
<figcaption>Using Kaira in a program. The declaration is written once; steps 2–4 are performed by the library and behave identically in every language.</figcaption>
</figure>

## Example

The tabs below show the four artefacts involved in one parse for a program
`example` that accepts a `--verbose` flag (short alias `-v`) and exactly
one positional argument: the declaration, the command line as the shell
tokenizes it, the portable result for a valid command line, and the
portable error for an invalid one.

=== ":material-file-code: Declaration"

    ```yaml title="example.korml"
    version: kaira.command-declaration/v1
    program: example
    command:
      options:
        verbose:
          flag:
            short: v # (1)!
      tail:
        positionals: # (2)!
          positionals:
            name: input
            value: string
            min: 1
            max: 1
    ```

    1.  Short aliases exist only when declared. Kaira never derives `-v` from `verbose` on its own.
    2.  Every command has exactly one tail mode. This one accepts a single positional value named `input`.

=== ":material-console: Command line"

    ```console
    $ example -v report.txt
    ```

    The shell has already split the line into words, so the parser receives:

    ```json
    ["-v", "report.txt"]
    ```

=== ":material-check-circle: Portable result"

    ```json
    {
      "program": "example",
      "command_path": [],
      "levels": [
        {
          "options": {"verbose": true},
          "positionals": {"input": ["report.txt"]}
        }
      ]
    }
    ```

    Result keys are the declared long option names, irrespective of the spelling used on the command line.

=== ":material-close-circle: Portable error"

    ```console
    $ example -v
    ```

    ```json
    {"code": "too_few_positionals", "index": 1}
    ```

    An error consists of a code from a closed set and a zero-based index into `argv`. Diagnostic text is implementation-defined.

!!! note "Status"

    This site documents version 1 of the specification, which is currently a
    draft. The normative text is the file `src/SPECIFICATION.md` in the
    repository, reproduced unchanged on the
    [Specification](reference/specification.md) page. All other pages are
    explanatory and do not add requirements. Once version 1 is declared
    stable, any change that affects results or error categories requires a
    new declaration version.
