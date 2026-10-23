---
title: Examples
description: Complete Kaira declarations with accepted and rejected command lines and the portable results they produce.
---

# Examples

Each example consists of a complete, valid declaration; argument vectors
that are accepted, with the portable result for a representative input; and
argument vectors that are rejected, with the error code and index.

| Example | Demonstrates | Tail mode |
| --- | --- | --- |
| [Minimal command](minimal.md) | The smallest valid declaration. | `empty` |
| [Subcommands](subcommands.md) | Required and optional child commands. | `subcommands` |
| [Options](options.md) | All four option kinds in one command. | `positionals` |
| [Primitive types](base-types.md) | `int`, `float`, `string`, `boolean` and arbitrary-length numbers. | `empty` |
| [Attached values](attached-values.md) | `value_style: attached` for scalar, repeatable, and separated options. | `positionals` |
| [Raw positionals](raw-positionals.md) | The `--` delimiter and the literal value `--`. | `positionals` |
| [Nested command tree](nested.md) | Three levels, per-level option scopes, a reused short alias. | mixed |

!!! note "Indices"

    Rejected command lines list the error code and the zero-based index of
    the offending `argv` word. `argv` excludes the program name: in
    `kaira --bad`, the word `--bad` is at index 0.
