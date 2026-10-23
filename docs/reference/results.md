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
| option or slot, `single` | One value representation. |
| option or slot, `multiple` | Array of value representations, in occurrence (or piece, or word) order. |
| `int`, `float` | The original string, never a JSON number. |
| `string` | The original string. |
| `boolean` | JSON `true` or `false`. |

The representation is the same whether a value came from a spaced option,
an attached option, or a positional word. Numeric strings preserve
arbitrary-length decimal literals and never undergo host-dependent rounding
or overflow: `"count": "123456789012345678901234567890"` is exactly what a
conforming parser emits. Language bindings may add typed numeric
conversions without changing this portable representation.

## Errors

Invalid declarations fail before any argument is read and return a `code`
with no `index`:

```json
{"code": "invalid_declaration"}
```

Argument failures return a `code` and a zero-based `index` into the supplied
`argv` (which excludes the executable name). Errors detected at end of
input use `index = argv.length`.

```json
{"code": "missing_value", "index": 2}
```

The full list of codes, with triggering examples, is on the
[Error codes](errors.md) page. Human-readable messages and presentation are
intentionally not standardized.

## Conformance suite

The repository's `conformance/v1.json` contains three sections.

`declarations`
:   Named, already-decoded representations of KORML command declarations.
    JSON is used only as a neutral interchange format for tests.

`cases`
:   Each case names a declaration, supplies an `argv` array, and expects
    exactly one of `ok` (a portable result) or `error` (a `code` and
    `index`).

`invalid_declarations`
:   Declarations that must be rejected during validation, with the expected
    error code and no argument index.

An implementation should load KORML source files with its chosen compatible
KORML reader, then pass the resulting data to its validator and `argv`
parser. The shared JSON cases test the **semantic** layer; they do not
replace tests that the KORML front end rejects malformed documents and
duplicate keys.

The suite currently covers, among other things:

- every error code at least once, including scope violations such as a
  parent flag used inside a child;
- numeric literals far beyond 64-bit range, `-0`, exponents with and
  without signs, and rejected spellings such as `+1`, `01`, `NaN`, and
  `Infinity`;
- empty attached values, empty separator pieces, and Unicode strings;
- `--` before, between, and after positional words, and `--` where it is
  not allowed;
- slot assignment with fixed and variable slots, count errors, deferred
  value validation, and the precedence of scan errors over it;
- tree validation: missing root, unknown or doubly listed child keys,
  orphan commands, duplicate child words, and name or alias collisions
  between flags and options.

!!! note "Scope of the suite"

    Passing the vectors is necessary but not sufficient. Implementers should
    also exercise very large numbers, Unicode strings, empty values,
    short-alias collisions, and repeated option combinations — ideally with
    property-based tests. See [Implementation and conformance](implementation.md).
