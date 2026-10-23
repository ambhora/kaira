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
an attached option `output` (`-o`), a spaced `multiple` option `include`,
a spaced `multiple` option `features` with separator `;`, and one centre
slot `target` accepting up to three words.

## Declaration errors

Reported before any argument is read. They carry **no** `index`.

| Code | Triggered by | Example |
| --- | --- | --- |
| `unsupported_version` | Any `version` other than `kaira.command-declaration/v1`. | `version: kaira.command-declaration/v2` |
| `invalid_declaration` | Anything else the schema or semantic rules reject: unknown fields (including the `value` field of earlier drafts), malformed or duplicate KORML keys, a missing `__main__`, a listed child key that does not exist or is listed twice, an unlisted command, two children with the same word, a name or short alias shared by a flag and an option, `separator` on a `single` option, a `left`/`right` slot with a variable count, two `center` slots, or a `single` slot with `max > 1`. | two flags both declaring `short: a` |

## Argument errors

Reported during the left-to-right scan, or at end of input. The first
failing word wins.

| Code | Triggered by | `index` points to | Example `argv` |
| --- | --- | --- | --- |
| `unknown_option` | A dash-leading word that is not a declared long or short spelling at this level — including clusters like `-vo` and parent flags used in a child. | The unrecognized word. | `["-vo"]` → 0 · `["target", "--bad"]` → 1 |
| `invalid_option_form` | A declared option written in the wrong value style, or a flag given a value. | The flag or option word. | `["--verbose=true"]` → 0 · `["--output", "a.log"]` → 0 |
| `missing_value` | A spaced option at end of input, or followed by the exact word `--`. | The option word. | `["--include", "--"]` → 0 |
| `duplicate_option` | A second occurrence of a flag or a `single` option (or a separator option), counting long and short spellings together. | The second occurrence. | `["-v", "--verbose"]` → 1 |
| `unexpected_argument` | A bare word on `shape: none`. | That word. | `["extra"]` → 0 (`empty` declaration) |
| `unknown_subcommand` | A bare word on `shape: subcommands` that is not a listed child's word. | That word. | `["deploy"]` → 0 (`commands` declaration) |
| `missing_subcommand` | End of input on `shape: subcommands`. | `argv.length` | `[]` → 0 (`commands` declaration) |
| `unexpected_delimiter` | The word `--` on `shape: none` or `subcommands`. | The `--` word. | `["--", "build"]` → 0 (`commands` declaration) |
| `too_few_positionals` | Fewer positional words than the slots require, determined at end of input. | `argv.length` | `["a"]` → 1 (`slots` declaration) |
| `too_many_positionals` | A positional word beyond the finite sum of all slot maxima. | The first excess word. | `["a", "--verbose", "b", "c", "d"]` → 4 |

## Precedence

Errors are reported in two stages: scan errors at the first failing word;
then `missing_subcommand` or `too_few_positionals` at end of input.
Consequently `too_many_positionals` is raised immediately when the excess
word is consumed, whereas `too_few_positionals` waits for end of input.
Values are never a source of errors: Kaira does not type or validate them.

## Presenting errors to users

The index lets an application highlight the offending word without parsing
anything itself:

```text
$ app target --bad
             ^^^^^ unknown option
```

How that looks — colors, suggestions, exit codes — is entirely up to the
implementation.
