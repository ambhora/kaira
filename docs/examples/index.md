---
title: Examples
description: Complete Kaira declarations with accepted and rejected command lines and the portable results they produce.
---

# Examples

Each example consists of a complete, valid declaration; argument vectors
that are accepted, with the portable result for a representative input; and
argument vectors that are rejected, with the error code and index. Results
are abbreviated to the record of the relevant command where the rest is
empty.

| Example | Demonstrates | Shape |
| --- | --- | --- |
| [Minimal command](minimal.md) | The smallest valid declaration. | `none` |
| [Subcommands](subcommands.md) | Child commands and per-level scopes. | `subcommands` |
| [Options](options.md) | Flags and the three option multiplicities in one command. | `positionals` |
| [Primitive types](base-types.md) | `int`, `float`, `string`, `boolean` and arbitrary-length numbers. | `none` |
| [Attached values](attached-values.md) | `style: attached` for single, multiple, and separator options. | `positionals` |
| [Raw positionals](raw-positionals.md) | The `--` delimiter and the literal value `--`. | `positionals` |
| [Positional slots](slots.md) | A variable centre slot and a fixed right slot. | `positionals` |
| [Nested command tree](nested.md) | Three levels, per-level scopes, a reused short alias. | mixed |

!!! note "Indices"

    Rejected command lines list the error code and the zero-based index of
    the offending `argv` word. `argv` excludes the program name: in
    `kaira --bad`, the word `--bad` is at index 0.
