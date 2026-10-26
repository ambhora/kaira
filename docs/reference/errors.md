---
title: Error codes
description: Every portable Kaira error code, what triggers it, where its index points, and a concrete argv from the conformance suite that produces it.
---

# Error codes

A Kaira failure is a `code` from the closed list below plus, for `argv`
failures, a zero-based `index` into the complete argument vector, counting
the invocation name `argv[0]` as index 0. Diagnostic text is deliberately
not standardized; the code and index are what implementations must agree
on.

Each example below is taken from the conformance suite. Unless noted, the
declaration is the suite's `options` declaration: a flag `verbose` (`-v`),
an attached option `output` (`-o`), a spaced `multiple` option `include`,
a spaced `multiple` option `features` with separator `;`, and one centre
slot `target` accepting up to three words.

## Declaration errors

Reported before any argument is read. They carry **no** `index`. The
version is checked first: a document whose `version` is a scalar other than
`kaira.command-declaration/v1` is `unsupported_version` regardless of any
other content.

| Code | Triggered by | Example |
| --- | --- | --- |
| `unsupported_version` | A `version` scalar other than `kaira.command-declaration/v1`. | `version: kaira.command-declaration/v2` |
| `invalid_declaration` | Everything else that the reading or validation rules reject: malformed KORML or a KORML version other than v0 and v1.0, duplicate keys, a missing or non-scalar `version`, unknown fields (including the `value` field of earlier drafts and `help` on a slot), a missing `__main__`, a listed child key that does not exist or is listed twice, a command unreachable from `__main__` (including cycles), two children with the same word, a name or short alias shared by a flag and an option, `separator` on a `single` option, a `left`/`right` slot with a variable count, two `center` slots, a slot with `max = 0`, a `single` slot with `max > 1`, or an integer or slot-count sum above 2⁶³ − 1. | two flags both declaring `short: a` |

## Argument errors

Reported during the left-to-right scan, or at end of input. The first
failing word wins.

| Code | Triggered by | `index` points to | Example `argv` |
| --- | --- | --- | --- |
| `empty_argv` | An `argv` without elements, so without an invocation name. | 0 | `[]` → 0 (`empty` declaration) |
| `unknown_option` | A dash-leading word whose spelling is not a declared long or short spelling at this level — including clusters like `-vo` and parent flags used in a child. | The unrecognized word. | `["app", "-vo"]` → 1 · `["app", "target", "--bad"]` → 2 |
| `invalid_option_form` | A declared option written in the wrong value style, or a flag given a value. | The flag or option word. | `["app", "--verbose=true"]` → 1 · `["app", "--output", "a.log"]` → 1 |
| `duplicate_option` | An occurrence of a flag or option beyond its permitted number: a second flag, `single` option, or separator option, counting long and short spellings together. | That occurrence. | `["app", "-v", "--verbose"]` → 2 |
| `missing_value` | A spaced option at end of input, or followed by the exact word `--`. | The option word. | `["app", "--include", "--"]` → 1 |
| `unexpected_argument` | A bare word on `shape: none`. | That word. | `["app", "extra"]` → 1 (`empty` declaration) |
| `unknown_subcommand` | A bare word on `shape: subcommands` that is not a listed child's word. | That word. | `["app", "deploy"]` → 1 (`commands` declaration) |
| `missing_subcommand` | End of input on `shape: subcommands`. | `argv.length` | `["app"]` → 1 (`commands` declaration) |
| `unexpected_delimiter` | The word `--` on `shape: none` or `subcommands`. | The `--` word. | `["app", "--", "build"]` → 1 (`commands` declaration) |
| `too_few_positionals` | Fewer positional words than the sum of the slot minima, determined at end of input. | `argv.length` | `["cp", "a"]` → 2 (`slots` declaration) |
| `too_many_positionals` | A positional word beyond the finite sum of all slot maxima. | The first excess word. | `["app", "a", "--verbose", "b", "c", "d"]` → 5 |

## Precedence

Errors are reported in three stages: `empty_argv`; scan errors at the first
failing word; then `missing_subcommand` or `too_few_positionals` at end of
input. Within one option word the checks run in a fixed order —
recognition, form, occurrence, value — so `app --output=a --output b` is
`invalid_option_form` at 2 rather than `duplicate_option`
([parser rules](parser-rules.md#order-of-checks)). Consequently
`too_many_positionals` is raised immediately when the excess word is
consumed, whereas `too_few_positionals` waits for end of input. Values are
never a source of errors: Kaira does not type or validate them.

## Presenting errors to users

The index lets an application highlight the offending word without parsing
anything itself:

```text
$ app target --bad
             ^^^^^ unknown option
```

How that looks — colors, suggestions, exit codes — is entirely up to the
implementation.
