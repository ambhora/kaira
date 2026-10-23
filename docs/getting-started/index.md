---
title: Getting started
description: Using Kaira in a program - write a KORML declaration, load it with a Kaira library, and consume the parse result; how to read a declaration and a result.
hide:
  - navigation
---

# Getting started

A program uses Kaira in three steps: write a declaration file in KORML that
lists the program's commands with their flags, options, and positional
arguments; load the declaration with a Kaira library for the host language
and pass it the process's argument vector; read the parse result, or handle
the error, in application code. The declaration format and the parsing
behaviour are identical across languages; only the loading step is
library-specific.

## Reading a declaration

A declaration is a flat document. Every command of the program — the root
and every subcommand at any depth — is one entry of the `commands` mapping,
and the tree is expressed by listing child keys under a parent.

```yaml title="greet.korml"
version: kaira.command-declaration/v1
program: greet
commands:
  __main__:                                    # (1)!
    shape: positionals                         # (2)!
    flags:                                     # (3)!
      loud: {short: l}
    options:                                   # (4)!
      times: {short: n, style: attached}
    positionals:                               # (5)!
      - name: {alignment: left}
```

1.  The root command is always keyed `__main__`. Other keys are free-form;
    by convention they are dotted paths such as `__main__.build`, and the
    word typed on the command line is the last segment.
2.  `shape` says what a bare word means at this command: `none` (not
    accepted), `subcommands` (selects a child), or `positionals` (a value for
    one of the slots below).
3.  Flags take no value. `--loud` and `-l` set the flag `loud`.
4.  Options take one value per occurrence, always as a string.
    `style: attached` means `--times=3`; `style: spaced` would mean
    `--times 3`. An option is `single` unless declared
    `multiplicity: multiple`.
5.  Positional slots are an ordered list. Each slot is `single` and
    `required` unless declared otherwise, so this one accepts exactly one
    word.

The fields of each construct are listed in the
[KORML schema](../reference/schema.md); [Writing a declaration](writing-a-declaration.md)
builds a complete declaration step by step.

## Reading a result

For `greet -l --times=3 Ada`, every conforming library produces:

```json
{
  "program": "greet",
  "command": "__main__",
  "path": ["__main__"],
  "commands": {
    "__main__": {
      "flags": ["loud"],
      "options": {"times": "3"},
      "positionals": {"name": "Ada"}
    }
  }
}
```

- `command` is the key of the command that was finally selected; `path`
  lists the keys from `__main__` down to it. With subcommands, `path` has
  one entry per level and `commands` has one record per entry.
- Each record is keyed by the command's key and holds `flags` (the long
  names present), `options`, and `positionals`. Anything absent from the
  command line is omitted. A `single` option or slot yields one value; a
  `multiple` one yields an array.
- Every value is a string (`"3"`, not `3`). The parser does not interpret
  values; a library may offer typed accessors, and the application decides
  what a value means.

For a command line the declaration does not accept, every library reports
the same code and the same position:

| Command line | Error | Reason |
| --- | --- | --- |
| `greet` | `too_few_positionals` at 0 | The `name` slot is required; the index is the end of input. |
| `greet --times 3 Ada` | `invalid_option_form` at 0 | `times` is `attached`; the spaced form is refused. |

Libraries expose the result through native types as well; the portable form
above is what the specification guarantees ([Portable results](../reference/results.md)).

## Libraries

Kaira libraries are being published for the following languages. Each
implements the same specification and passes the same conformance suite.
Installation and API documentation is maintained in each library's own
repository.

| Language | Library | Status |
| --- | --- | --- |
| Python | `pykaira` | in preparation |
| Rust | `kaira-rs` | in preparation |
| C++ | `kaira-cpp` | in preparation |

## Terms

`declaration`
:   A KORML document listing a program's commands. The format is defined by
    the [KORML schema](../reference/schema.md).

`argv`
:   The ordered list of words produced by the shell, excluding the
    executable name. Kaira does not split, trim, or unquote words.

`command`, `level`
:   One entry of `commands`. During parsing, the command currently being
    read is the current level; selecting a subcommand moves to the next
    level. Flags and options belong to the level in which they appear.

`slot`
:   One named positional argument of a command, with an alignment
    (`left`, `center`, `right`) and a cardinality.

`portable result`
:   The JSON-compatible value every conforming library produces for a
    successful parse, or the `code`/`index` pair produced on failure.

Writing a new Kaira library for another language is covered under
[Implementation and conformance](../reference/implementation.md).
