---
title: Parser rules
description: The per-level scanning procedure a conforming Kaira parser follows, with option forms, occurrence limits, and delimiter handling.
---

# Parser rules

The Kaira parser is a fixed interpreter for Kaira command declarations. The
normative definition — including validation, output, and error precedence —
is the [specification](specification.md); this page is the working summary.

The shell has already split the command line into `argv` words. Quoting
and escaping are therefore the shell's concern, never Kaira's.

## Per-level parsing

Each command declares one of three mutually exclusive tail modes.

| Tail | Permitted stream at this level |
| --- | --- |
| `empty` | Declared options only. |
| `subcommands` | Declared options, then one child command name; parsing continues in the child's new scope. |
| `positionals` | Declared options freely interleaved with positional values; optionally `--` followed by raw positionals. |

The procedure for one level:

<figure class="kaira-figure" markdown>
![Parsing procedure: validate the declaration, then scan argv word by word at the current command level, dispatching on word class and tail mode; check counts at end of input.](../assets/images/parse-flow.svg)
<figcaption>Each word is classified and dispatched according to the current level's declaration; a subcommand word opens a new level and the loop continues there.</figcaption>
</figure>

The same procedure as pseudo-code:

```text
parse_level(command, argv):
  options = {}
  positionals = []
  raw = false

  while argv is not empty:
    token = argv.front
    if raw:
      consume_and_validate_positional(token)
    else if token == "--":
      require command.tail is positionals        # else unexpected_delimiter
      raw = true
      consume token
    else if token starts with "-":
      consume_and_validate_declared_option(command.options)
    else if command.tail is empty:
      error unexpected_argument
    else if command.tail is subcommands:
      child = lookup_subcommand(token)           # else unknown_subcommand
      return parse_level(child, argv.after_front)
    else:
      consume_and_validate_positional(token)

  check_required_subcommand_or_minimum_positionals()
  return result_for_level
```

This is explanatory pseudo-code, not a prescribed API. Occurrence checks
and error precedence are defined normatively in the specification.

## Option parsing

An option consumes zero or one following word.

| Declaration | Accepted form | Meaning |
| --- | --- | --- |
| `flag` | `--name`, `-n` | No value. |
| `value_style: spaced` | `--name value`, `-n value` | The value is the next word. |
| `value_style: attached` | `--name=value`, `-n=value` | The value follows the first `=` in the same word. |

The declaration decides the accepted form. A parser must not accept both
`--name value` and `--name=value` for one option. Short aliases are
explicit, never inferred from long names. Short-option clustering (`-abc`),
short value concatenation (`-ofile`), and abbreviation are not part of the
grammar; such words are `unknown_option`.

With `value_style: spaced`, the next word is consumed as the value **even
if it begins with a dash** — the only exception is the exact delimiter `--`,
which yields `missing_value`.

With `value_style: attached`, the value is everything after the first `=`,
including an empty string or further `=` signs. For separated values whose
separator is special to a shell, such as `;`, users must quote or escape so
that the whole word reaches Kaira.

## Option occurrence rules

| Kind | Occurrence rule |
| --- | --- |
| `flag` | At most once. |
| `scalar` | At most once. |
| `repeatable` | Any number of times. |
| `separated` | At most once. |

Long and short spellings count together: `-v --verbose` is
`duplicate_option`. No option is implicitly required, and absent options
have no default value.

## Separated option rule

A separated option is one occurrence with one value. After the value is
consumed, it is split at every literal, non-overlapping occurrence of the
declared separator, from left to right. Empty pieces are kept.

```text
--features "mpi;cuda;openmp"     →  ["mpi", "cuda", "openmp"]
--features ";a;;"                →  ["", "a", "", ""]
--features ""                    →  [""]
```

Each piece is validated against the declared value type in order. Whether
the option is written `--features VALUE` or `--features=VALUE` is decided by
its `value_style`.

## Tail rules

| Tail | Rule |
| --- | --- |
| `empty` | Options only; the first bare word is `unexpected_argument`. |
| `subcommands` | The first bare word must be a declared subcommand; parent parsing ends at that boundary. |
| `positionals` | Bare words are positional values; options may occur before, between, and after them. |

A declaration cannot have both `subcommands` and `positionals` at the same
level.

## The `--` delimiter

The exact word `--` ends **option recognition** at the current
`positionals` level. It may occur before or after positional values.

After `--`, every remaining word is a raw positional value of the current
command, including dash-leading words and further `--` words. Without the
delimiter, any declared option is parsed as an option even when it follows
a positional, and any undeclared dash-leading word is `unknown_option`.

```console
$ kaira run -- --not-an-option --help build
```

Raw positionals: `--not-an-option`, `--help`, `build`.

`--` is valid only when the current command accepts positionals. On an
`empty` or `subcommands` tail it is `unexpected_delimiter`, and it never
selects a subcommand.

## The literal value `--`

A spaced option cannot receive `--` as its value:

```console
$ kaira --output --        # missing_value
```

Declare the option with `value_style: attached` and write `--output=--` to
pass the literal value.

## Error precedence

Errors are reported in scan order: the first word that fails, fails the
parse. Two details matter for implementers:

- The positional `max` bound is checked as each positional is consumed;
  `min` is checked only at end of input.
- Duplicate-option detection precedes validation of the duplicate's value.

See [Error codes](errors.md) for the full list with examples.
