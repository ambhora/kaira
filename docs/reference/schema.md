---
title: KORML schema reference
description: The Kaira v1 command declaration language - root fields, commands and shapes, flags, options, and positional slots.
---

# KORML schema reference

This page explains the Kaira v1 command declaration language. The canonical
schema is `schema/kaira.command-declaration.v1.korml` in the repository;
the listing below is included from that file at build time. The
[normative specification](specification.md) adds semantic checks on top of
the schema (tree structure, name uniqueness, slot consistency), and its
EBNF grammar is the final authority on syntactic acceptance of `argv`.
Values have no types: every option value and positional word is an opaque
string.

The schema describes declarations only; the runtime grammar of `argv` is
defined in [Parser rules](parser-rules.md).

## Structure

```text
root
├── version      "kaira.command-declaration/v1"
├── program      identifier
└── commands     key → command            (must contain __main__)
    └── command
        ├── shape         none | subcommands | positionals
        ├── help?         string
        ├── flags?        name → {short?, help?}
        ├── options?      name → {style, multiplicity?, separator?, short?, help?}
        ├── subcommands?  [key, …]                  (iff shape = subcommands)
        └── positionals?  [{name: slot}, …]         (iff shape = positionals)
            └── slot      {alignment, multiplicity?, required?, cardinality?, help?}
```

## Schema

```yaml title="schema/kaira.command-declaration.v1.korml"
--8<-- "schema/kaira.command-declaration.v1.korml"
```

## Root document

| Field | Required | Meaning |
| --- | --- | --- |
| `version` | yes | Exactly `kaira.command-declaration/v1`. |
| `program` | yes | Program name, copied into results; not matched against the executable name. |
| `commands` | yes | Mapping from command key to command. Must contain `__main__`. |

Unknown fields are rejected everywhere.

## Command keys and the tree

Every command of the program is one entry of `commands`. A key matches
`[A-Za-z_][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)*`; its **word** — the
text after the last `.` — is what the user types to select it. `__main__`
is the root. The tree is formed by listing child keys under a parent's
`subcommands`:

```yaml
commands:
  __main__:         {shape: subcommands, subcommands: [__main__.build, __main__.test]}
  __main__.build:   {shape: none}
  __main__.test:    {shape: none}
```

Rules: every listed key must exist; `__main__` is never listed; every other
key is listed by exactly one parent; the words of one parent's children
are distinct. The dotted prefix is a naming convention with no effect on
parsing — `build` could equally be keyed `b` — but it keeps keys unique and
self-describing.

## Command

| Field | Required | Meaning |
| --- | --- | --- |
| `shape` | yes | `none`, `subcommands`, or `positionals`; see below. |
| `help` | no | Metadata; no parsing effect. v1 does not create `--help`. |
| `flags` | no | Mapping of flag name → flag. |
| `options` | no | Mapping of option name → option. |
| `subcommands` | iff `shape: subcommands` | Nonempty list of command keys. |
| `positionals` | iff `shape: positionals` | Nonempty list of slots. |

=== "shape: none"

    No bare words are accepted.

    ```yaml
    __main__.version: {shape: none}
    ```

    | Command line | Verdict |
    | --- | --- |
    | `kaira version` | accepted |
    | `kaira version extra` | `unexpected_argument` |

=== "shape: subcommands"

    The first bare word must be the word of a listed child; parsing then
    continues in that child with its own flags and options. A child is
    always required.

    ```yaml
    __main__: {shape: subcommands, subcommands: [__main__.build, __main__.test]}
    ```

    | Command line | Verdict |
    | --- | --- |
    | `kaira build` | accepted; `command` is `__main__.build` |
    | `kaira` | `missing_subcommand` |
    | `kaira deploy` | `unknown_subcommand` |

=== "shape: positionals"

    Bare words are positional values, assigned to the declared slots at end
    of input. Flags and options may appear anywhere among them.

    ```yaml
    __main__.build:
      shape: positionals
      positionals:
        - target: {alignment: center, multiplicity: multiple, required: false}
    ```

    | Command line | Verdict |
    | --- | --- |
    | `kaira build`, `kaira build a b` | accepted |

## Flags

A flag takes no value and may appear at most once per command.

| Field | Required | Meaning |
| --- | --- | --- |
| `short` | no | One ASCII letter or digit; unique within the command across flags and options. |
| `help` | no | Metadata. |

```yaml
flags:
  verbose: {short: v}
  dry-run: {}
```

| Command line | Verdict |
| --- | --- |
| `--verbose`, `-v` | accepted → `"flags": ["verbose"]` |
| `--verbose=true` | `invalid_option_form` |
| `-v --verbose` | `duplicate_option` |

## Options

An option takes exactly one value per occurrence; the value is an opaque
string.

| Field | Required | Meaning |
| --- | --- | --- |
| `style` | yes | `spaced` (`--name value`) or `attached` (`--name=value`). The other form is `invalid_option_form`. |
| `multiplicity` | no | `single` (default): at most one occurrence, one value. `multiple`: see below. |
| `separator` | no | Nonempty string; only with `multiple`. The one value is split on it. |
| `short` | no | As for flags. |
| `help` | no | Metadata. |

=== "single"

    ```yaml
    output: {style: attached}
    ```

    | Command line | Verdict |
    | --- | --- |
    | `--output=result.txt` | accepted → `"output": "result.txt"` |
    | `--output result.txt` | `invalid_option_form` |
    | `--output=a.txt --output=b.txt` | `duplicate_option` |

=== "multiple"

    Repeated occurrences, one value each.

    ```yaml
    include: {style: spaced, multiplicity: multiple}
    ```

    | Command line | Verdict |
    | --- | --- |
    | `--include src --include tests` | accepted → `"include": ["src", "tests"]` |
    | `--include=src` | `invalid_option_form` |
    | `--include "src;tests"` | accepted → **one** value, `"src;tests"` |

=== "multiple with separator"

    One occurrence whose value is split.

    ```yaml
    features: {style: spaced, multiplicity: multiple, separator: ";"}
    ```

    | Command line | Verdict |
    | --- | --- |
    | `--features "mpi;cuda;openmp"` | accepted → `["mpi", "cuda", "openmp"]` |
    | `--features=mpi;cuda;openmp` | `invalid_option_form` (declared `spaced`) |
    | `--features mpi --features cuda` | `duplicate_option` |

Long names must be distinct across `flags` and `options` of one command,
and so must short aliases. Both may be reused in a different command.

## Positional slots

`positionals` is an ordered list; each entry is a single-key mapping from
the slot name to its fields.

| Field | Required | Values | Default |
| --- | --- | --- | --- |
| `alignment` | yes | `left`, `center`, `right` | — |
| `multiplicity` | no | `single`, `multiple` | `single` |
| `required` | no | boolean | `true` |
| `cardinality.min` | no | integer ≥ 0 | `1` if required, else `0` |
| `cardinality.max` | no | integer ≥ min, or `unbounded` | `1` if single, else `unbounded` |
| `help` | no | string | — |

Consistency rules, violations of which are `invalid_declaration`:

1. `single` ⇒ `max = 1`; `required: true` ⇒ `min ≥ 1`; `required: false`
   ⇒ `min = 0`. An explicit `cardinality` must agree with these.
2. A `left` or `right` slot has a fixed count (`min = max`).
3. At most one slot is `center`; only it may have a variable count.
4. Effective order: all `left` slots in list order, the `center` slot, all
   `right` slots in list order.

```yaml
positionals:
  - input:  {alignment: left,   multiplicity: multiple, cardinality: {min: 2, max: 2}}
  - extra:  {alignment: center, multiplicity: multiple, required: false}
  - output: {alignment: right}
```

| Command line | Assignment |
| --- | --- |
| `a b out` | `input = ["a", "b"]`, `output = "out"` |
| `a b 1 2 out` | `input = ["a", "b"]`, `extra = ["1", "2"]`, `output = "out"` |
| `a out` | `too_few_positionals` |
| `a b x out` | `input = ["a", "b"]`, `extra = ["x"]`, `output = "out"` — words are not typed |

## Values

Option values and positional words are opaque strings. The declaration
carries no value types and the parser performs no validation or conversion;
a word such as `-1`, `true`, or `NAME=VALUE` is delivered unchanged. Typed
access is provided by libraries, and validation by applications, above this
specification. A `value` field in an option or slot is an unknown field and
makes the declaration invalid.

!!! note "`integer` and `boolean` in the schema"

    The schema uses intrinsic `integer` and `boolean` scalars only to
    describe *declaration metadata* such as `cardinality` bounds and
    `required`. They say nothing about command-line values.
