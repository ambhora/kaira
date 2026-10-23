---
title: Getting started
description: How to use Kaira in a program - write a KORML declaration, load it with a Kaira library for the host language, and consume the parse result.
---

# Getting started

A program uses Kaira in three steps:

1.  Write a declaration file in KORML that describes the program's
    commands, options, and positional arguments.
2.  Load the declaration with a Kaira library for the host language and pass
    it the process's argument vector.
3.  Read the parse result (or handle the error) in application code.

The declaration format and parsing behavior are identical across languages.
Only step 2 is library-specific.

## 1. Write a declaration

A minimal declaration for a program `greet` that takes one name and an
optional `--loud` flag:

```yaml title="greet.korml"
version: kaira.command-declaration/v1
program: greet
command:
  options:
    loud:
      flag:
        short: l
  tail:
    positionals:
      positionals:
        name: name
        value: string
        min: 1
        max: 1
```

[Writing a declaration](writing-a-declaration.md) builds a complete
declaration step by step. The [KORML schema](../reference/schema.md) lists
every field.

## 2. Load it with a library

Kaira libraries are being published for the following languages. Each
implements the same specification and passes the same conformance suite.

| Language | Library | Status |
| --- | --- | --- |
| Python | `pykaira` | in preparation |
| Rust | `kaira-rs` | in preparation |
| C++ | `kaira-cpp` | in preparation |

Library-specific installation and API documentation is maintained in each
library's own repository. The behavior documented on this site applies to
all of them.

## 3. Consume the result

For `greet -l Ada`, every library yields the same portable result:

```json
{
  "program": "greet",
  "command_path": [],
  "levels": [
    {
      "options": {"loud": true},
      "positionals": {"name": ["Ada"]}
    }
  ]
}
```

For `greet` with no name, every library reports the same error:

```json
{"code": "too_few_positionals", "index": 0}
```

Libraries expose this result through native types (for example, a typed
record or struct) in addition to the portable form. The portable form is
what the specification guarantees; see
[Portable results](../reference/results.md).

## Terms

`declaration`
:   A KORML document describing a program's command tree. The format is
    defined by the [KORML schema](../reference/schema.md).

`argv`
:   The ordered list of words produced by the shell, excluding the
    executable name. Kaira does not split, trim, or unquote words.

`command level`
:   One node of the command tree active during parsing. The root is a level;
    each selected subcommand opens another. Options belong to the level in
    which they appear.

`portable result`
:   The JSON-compatible value every conforming library produces for a
    successful parse, or the `code`/`index` pair produced on failure.

## Implementing a library

Writing a new Kaira library for another language is covered under
[Implementation and conformance](../reference/implementation.md).
