---
title: Portable results and conformance
description: The JSON-compatible result every conforming Kaira parser produces, how values are represented, and how the conformance suite is organized.
---

# Portable results and conformance

Kaira makes declaration and argument parsing portable across language
implementations. The common representation uses JSON-compatible types,
although no implementation is required to use JSON internally.

## Successful parse

For a declaration whose root lists `__main__.build`, and the command line
`kaira -v build --output=build.log --include src --include inc app`:

```json
{
  "program": "kaira",
  "command": "__main__.build",
  "path": ["__main__", "__main__.build"],
  "commands": {
    "__main__": {
      "flags": ["verbose"],
      "options": {},
      "positionals": {}
    },
    "__main__.build": {
      "flags": [],
      "options": {"output": "build.log", "include": ["src", "inc"]},
      "positionals": {"target": "app"}
    }
  }
}
```

| Field | Content |
| --- | --- |
| `program` | Copied from the declaration. |
| `command` | Key of the last selected command. |
| `path` | Keys of all selected commands, from `__main__` to `command`, in order. |
| `commands` | One record per key in `path`, keyed by that key; no other keys. |

Each record has exactly `flags`, `options`, and `positionals`:

| Record field | Content |
| --- | --- |
| `flags` | Array of the long names of the flags present, in first-occurrence order. |
| `options` | Mapping from long option name to value; absent options are omitted. |
| `positionals` | Mapping from slot name to value for slots that received at least one word; others are omitted. `{}` for `shape: none` and `subcommands`. |

The result is keyed by the same names as the declaration, so a record can
be matched against the file that declared it without counting levels.

### Value representation

| Declaration | Portable value |
| --- | --- |
| option or slot, `single` | One string. |
| option or slot, `multiple` | Array of strings, in occurrence (or piece, or word) order. |

Every value is the original word (or the suffix after `=` for an attached
option), as a JSON string. Values are never numbers or Booleans in the
portable result, whatever they look like: `"count": "123456789012345678901234567890"`
and `"enabled": "false"` are exactly what a conforming parser emits.
Libraries may add typed accessors without changing this representation.

## Errors

Invalid declarations fail before any argument is read and return a `code`
with no `index`:

```json
{"code": "invalid_declaration"}
```

Argument failures return a `code` and a zero-based `index` into the
complete `argv`, including the invocation name `argv[0]`, so the index can
be used directly on the host's argument vector. Errors detected at end of
input use `index = argv.length`.

```json
{"code": "missing_value", "index": 2}
```

The full list of codes, with triggering examples, is on the
[Error codes](errors.md) page. Human-readable messages and presentation are
intentionally not standardized.

## Conformance suite

The repository's `tests/conformance/v1.json` contains three sections.

`declarations`
:   Named, already-decoded representations of KORML command declarations:
    scalars appear as the JSON strings, numbers, and Booleans that the
    specification decodes them to. JSON is used only as a neutral
    interchange format for tests.

`cases`
:   Each case names a declaration, supplies an `argv` array that begins
    with the invocation name, and expects
    exactly one of `ok` (a portable result) or `error` (a `code` and
    `index`).

`invalid_declarations`
:   Declarations that must be rejected during validation, with the expected
    error code and no argument index.

An implementation loads KORML source files with a reader for KORML v0 and
v1.0, then passes the resulting data to its validator and `argv`
parser. The shared JSON cases test the **semantic** layer; they do not
replace tests that the KORML front end rejects malformed documents and
duplicate keys and decodes scalars as specified.

The suite currently covers, among other things:

- every error code at least once, including scope violations such as a
  parent flag used inside a child;
- an empty `argv`, and an `argv[0]` that looks like an option, which is
  not interpreted;
- the order of checks within one option word: recognition, form,
  occurrence, value;
- numeric-looking words far beyond 64-bit range, `-0`, `true`, and `NAME=VALUE`
  words, all delivered as strings;
- empty attached values, empty separator pieces, and Unicode strings;
- `--` before, between, and after positional words, and `--` where it is
  not allowed;
- slot assignment with fixed and variable slots and count errors;
- tree validation: missing root, unknown or doubly listed child keys,
  orphan commands, cycles unreachable from the root, duplicate child words,
  and name or alias collisions between flags and options;
- version precedence, slots with `max = 0`, and integers and slot-count
  sums at and beyond the 64-bit limit.

!!! note "Scope of the suite"

    Passing the vectors is necessary but not sufficient. Implementers should
    also exercise very large numbers, Unicode strings, empty values,
    short-alias collisions, and repeated option combinations — ideally with
    property-based tests. See [Implementation and conformance](implementation.md).
