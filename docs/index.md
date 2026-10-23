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
written in KORML and lists a program's commands, each with its flags,
options, subcommands, and positional slots. The specification fixes the
declaration format, its validation rules, the interpretation procedure, and
a portable result representation, so that independent implementations in
different languages produce identical results and error codes for identical
inputs.

</div>

<div class="grid kaira-columns" markdown>

<div markdown>

### Properties

**Determinism:** the outcome depends on the declaration and the argument
vector alone; there is no abbreviation, clustering, or implicit alias
([design goals](explanation/design-goals.md)).

**Value portability:** `int` and `float` values are validated lexically and
kept as text, so results do not depend on host numeric types
([results](reference/results.md)).

**Scoped commands:** each selected subcommand opens a new level with its own
flags and options; nothing is inherited ([grammar](explanation/grammar.md)).

**Conformance:** a shared vector file fixes the expected result or error for
each case ([conformance suite](reference/results.md#conformance-suite)).

</div>

<div markdown>

### Scope

**Specified:** the KORML declaration format and its validation; per-level
interpretation of flags, options, subcommands, and positional slots; the
portable result and error codes; four primitive value types with exact
lexical grammars; a language-neutral conformance suite.

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

A program `example` with one flag, `--verbose` (short `-v`), and one
required positional argument, `input`. The tabs show the declaration, a
command line as the shell tokenizes it, the portable result, and the
portable error for a command line that omits the argument.

=== "Declaration"

    ```yaml title="example.korml"
    version: kaira.command-declaration/v1
    program: example
    commands:
      __main__:                      # (1)!
        shape: positionals           # (2)!
        flags:
          verbose: {short: v}        # (3)!
        positionals:
          - input: {alignment: left, value: string}   # (4)!
    ```

    1.  Every command is an entry of `commands`; `__main__` is the root.
    2.  `shape` states what bare words mean at this level: `none`,
        `subcommands`, or `positionals`.
    3.  A flag takes no value. Its short alias exists only because it is
        declared here.
    4.  One positional slot, `single` and `required` by default, so it
        accepts exactly one word.

=== "Command line"

    ```console
    $ example -v report.txt
    ```

    The shell has already split the line into words, so the parser receives
    `["-v", "report.txt"]`.

=== "Portable result"

    ```json
    {
      "program": "example",
      "command": "__main__",
      "path": ["__main__"],
      "commands": {
        "__main__": {
          "flags": ["verbose"],
          "options": {},
          "positionals": {"input": "report.txt"}
        }
      }
    }
    ```

    The result is keyed by the same command names as the declaration.
    Flags are listed by long name; a `single` slot yields one value.

=== "Portable error"

    ```console
    $ example -v
    ```

    ```json
    {"code": "too_few_positionals", "index": 1}
    ```

    An error consists of a code from a closed set and a zero-based index
    into `argv` (here the end of input). Diagnostic text is
    implementation-defined.

!!! note "Status"

    This site documents version 1 of the specification, which is currently a
    draft. The normative text is the file `src/SPECIFICATION.md` in the
    repository, reproduced unchanged on the
    [Specification](reference/specification.md) page. All other pages are
    explanatory and do not add requirements. Once version 1 is declared
    stable, any change that affects results or error categories requires a
    new declaration version.
