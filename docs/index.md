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

## Command-line model

<figure class="kaira-figure kaira-figure--narrow" markdown>
![Three forms of a command line: a command with a subcommand; a command with positional arguments (fixed, variable, fixed) among which flags and options may appear; nested subcommands of any depth, each with its own flags, options and arguments.](assets/images/command-line-model.svg)
<figcaption>A command has flags and options and either a subcommand or positional arguments. Subcommands nest to any depth, each level with its own flags, options and arguments; a fixed number of arguments at each end and one variable group in the middle give every word exactly one place.</figcaption>
</figure>

## Using Kaira in a program

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
          - input: {alignment: left}                  # (4)!
    ```

    1.  Every command is an entry of `commands`; `__main__` is the root.
    2.  `shape` states what bare words mean at this level: `none`,
        `subcommands`, or `positionals`.
    3.  A flag takes no value. Its short alias exists only because it is
        declared here.
    4.  One positional slot, `single` and `required` by default, so it
        accepts exactly one word. Values have no types: every word is
        delivered as a string.

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

<div class="grid kaira-columns" markdown>

<div markdown>

### Properties

**Determinism:** the outcome depends on the declaration and the argument
vector alone; there is no abbreviation, clustering, or implicit alias
([design goals](explanation/design-goals.md)).

**Opaque values:** every value is carried as the original string; the parser
neither interprets nor converts it, so results do not depend on host types
([results](reference/results.md)).

**Scoped commands:** each selected subcommand opens a new level with its own
flags and options; nothing is inherited ([grammar](explanation/grammar.md)).

**Conformance:** a shared vector file fixes the expected result or error for
each case ([conformance suite](reference/results.md#conformance-suite)).

</div>

<div markdown>

### Scope

**This specification:** the declaration format, its interpretation, the
portable result and error codes, and the conformance suite.

**Libraries** (`pykaira`, `kaira-rs`, `kaira-cpp`): the language API,
typed access to the result, diagnostics, and help output — specified and
documented per library.

**Applications:** the meaning of values (paths, numbers, enumerations),
defaults, environment variables, configuration files.

**The shell:** tokenization, quoting, and escaping; Kaira receives words.

</div>

</div>

!!! note "Status"

    This site documents version 1 of the specification, which is currently a
    draft. The normative text is the file `src/SPECIFICATION.md` in the
    repository, reproduced unchanged on the
    [Specification](reference/specification.md) page. All other pages are
    explanatory and do not add requirements. Once version 1 is declared
    stable, any change that affects results or error categories requires a
    new declaration version.
