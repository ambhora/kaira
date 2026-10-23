---
title: Error codes
description: Every portable Kaira error code, what triggers it, where its index points, and a concrete argv from the conformance suite that produces it.
---

# Error codes

A Kaira failure is a `code` from the closed list below plus, for `argv`
failures, a zero-based `index` into the argument vector. Diagnostic text is
deliberately not standardized; the code and index are what implementations
must agree on.

Each example below is taken from the conformance suite. Unless noted, the
declaration is the suite's `options` declaration: a flag `verbose` (`-v`),
an attached scalar `output` (`-o`), a spaced repeatable `include`, a spaced
separated `features` with separator `;`, and a `target` positional tail
with `max: 3`.

## Declaration errors

Reported before any argument is read. They carry **no** `index`.

| Code | Triggered by | Example |
| --- | --- | --- |
| `unsupported_version` | Any `version` other than `kaira.command-declaration/v1`. | `version: kaira.command-declaration/v2` |
| `invalid_declaration` | Anything else the schema or semantic rules reject: unknown fields, malformed or duplicate KORML keys, a repeated short alias in one level, an empty `separator`, `max < min`, or a type name such as `integer` or `path`. | two flags both declaring `short: a` |

## Argument errors

Reported during the left-to-right scan. The first failing word wins.

| Code | Triggered by | `index` points to | Example `argv` |
| --- | --- | --- | --- |
| `unknown_option` | A dash-leading word that is not a declared long or short spelling at this level — including clusters like `-vo` and parent options used in a child. | The unrecognized word. | `["-vo"]` → 0 · `["target", "--bad"]` → 1 |
| `invalid_option_form` | A declared option written in the wrong value style, or a flag given a value. | The option word. | `["--verbose=true"]` → 0 · `["--output", "a.log"]` → 0 |
| `missing_value` | A spaced option at end of input, or followed by the exact word `--`. | The option word. | `["--include", "--"]` → 0 |
| `duplicate_option` | A second occurrence of a `flag`, `scalar`, or `separated` option, counting long and short spellings together. | The second occurrence. | `["-v", "--verbose"]` → 1 |
| `invalid_value` | A value that does not match its declared type's lexical grammar. | The value word for spaced options and positionals; the whole option word for attached options. | `["--count=01"]` → 0 · `["--ratio", "NaN"]` → 1 (`values` declaration) |
| `unexpected_argument` | A bare word on an `empty` tail. | That word. | `["extra"]` → 0 (`empty` declaration) |
| `unknown_subcommand` | A bare word on a `subcommands` tail that is not a declared child. | That word. | `["deploy"]` → 0 (`commands` declaration) |
| `missing_subcommand` | End of input on a `subcommands` tail with `required: true`. | `argv.length` | `[]` → 0 (`commands` declaration) |
| `unexpected_delimiter` | The word `--` on an `empty` or `subcommands` tail. | The `--` word. | `["--", "build"]` → 0 (`commands` declaration) |
| `too_few_positionals` | Fewer positional values than `min` at end of input. | `argv.length` | `["a"]` → 1 (`two_positionals` declaration) |
| `too_many_positionals` | A positional value beyond the finite `max`. | The first excess positional. | `["a", "--verbose", "b", "c", "d"]` → 4 |

## Precedence in practice

Errors are detected in scan order, so the leftmost problem is reported even
if a later word is "worse":

```text
argv: ["--include=src", "--bogus"]
      ^^^^^^^^^^^^^^^
      invalid_option_form at 0   (unknown_option at 1 is never reached)
```

Two ordering rules apply:

1.  `too_many_positionals` is raised immediately when the excess value is
    consumed; `too_few_positionals` is raised only at end of input.
2.  `duplicate_option` is checked before the duplicate's value is validated,
    so `["--output=a", "--output=!!"]` is `duplicate_option` at 1 even if
    `!!` were invalid for the declared type.

## Presenting errors to users

The index lets an application highlight the offending word without parsing
anything itself:

```text
$ app target --bad
             ^^^^^ unknown option
```

How that looks — colors, suggestions, exit codes — is entirely up to the
implementation.
