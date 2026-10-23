---
title: Primitive types
description: The four Kaira value types - int, float, string, boolean - and how arbitrary-length numeric literals are preserved in the portable result.
---

# Primitive types

Kaira v1 defines four and only four value types: `int`, `float`, `string`,
and `boolean`. The normative lexical productions are in
[section 10 of the specification](../reference/specification.md#10-normative-ebnf-grammar).

```yaml title="calc.korml"
version: kaira.command-declaration/v1
program: calc
commands:
  __main__:
    shape: none
    options:
      count:   {value: int,     style: attached}
      ratio:   {value: float,   style: spaced}
      enabled: {value: boolean, style: spaced}
      output:  {value: string,  style: attached}   # (1)!
```

1.  There is no `path` type. Declare a `string` and validate the file system
    after parsing.

Given these six words (each entry is exactly one `argv` word)

```json
["--count=123456789012345678901234567890", "--ratio", "0.12345678901234567890e+9999",
 "--enabled", "false", "--output=result.txt"]
```

the record for `__main__` is:

```json
{
  "flags": [],
  "options": {
    "count": "123456789012345678901234567890",
    "ratio": "0.12345678901234567890e+9999",
    "enabled": false,
    "output": "result.txt"
  },
  "positionals": {}
}
```

The numeric strings are preserved exactly, regardless of their length and
regardless of whether the host language has arbitrary-precision arithmetic.
No floating-point rounding takes place in the portable result. A
language-specific API may convert the strings afterwards.

| Command line | Outcome |
| --- | --- |
| `calc --count=01` | `invalid_value` at 0 — `int` forbids leading zeros |
| `calc --count=+1` | `invalid_value` at 0 — `int` allows only a leading `-` |
| `calc --count=1.0` | `invalid_value` at 0 — an `int` has no fraction |
| `calc --ratio NaN` | `invalid_value` at 1 — `float` is finite and decimal only |
| `calc --ratio Infinity` | `invalid_value` at 1 — no infinity literals |
| `calc --enabled TRUE` | `invalid_value` at 1 — `boolean` is exactly lowercase `true` or `false` |
| `calc --enabled` | `missing_value` at 0 — a spaced option needs a following word |

## Lexical cheat sheet

| Type | Valid | Invalid |
| --- | --- | --- |
| `int` | `0`, `-7`, `123456789012345678901234567890` | `+1`, `01`, `-0`, `1.0`, `1e3` |
| `float` | `1`, `-0`, `0.5`, `1e3`, `1.5E+1000`, `12345678901234567890.000000001e-999999999` | `.5`, `1.`, `+1`, `NaN`, `Infinity`, `0x1p3` |
| `string` | anything, including `""` and `東京` | — |
| `boolean` | `true`, `false` | `TRUE`, `yes`, `1`, `0` |

Note in particular that integer-shaped text such as `1` is a valid `float`,
and that `-0` is a valid `float` but **not** a valid `int`.

`output` is deliberately declared as a `string`. Kaira has no fifth built-in
type named `path`, and no `assignment` type for `NAME=VALUE` words either;
applications interpret such strings after parsing. A flag such as
`--verbose` is not a `boolean` option: it consumes no word and is listed in
`flags` when present, whereas a `boolean` option requires an explicit `true`
or `false` word.
