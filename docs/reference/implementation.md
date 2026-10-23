---
title: Implementation and conformance
description: Checklist for implementing a conforming Kaira library in a new host language, and the procedure for running the shared conformance vectors.
---

# Implementation and conformance

!!! note "Audience"

    This page is for authors of Kaira libraries. Users of an existing
    library do not need it; see [Getting started](../getting-started/index.md).

A Kaira implementation consists of a declaration validator, a per-level
scanner, and four lexical validators. This page complements the
[normative specification](../reference/specification.md) with an
implementation checklist and the conformance procedure.

## Structure

```mermaid
flowchart LR
    K[KORML source] -->|KORML reader| D[Decoded declaration]
    D --> V{Validate}
    V -->|invalid| E1["invalid_declaration /<br/>unsupported_version"]
    V -->|valid| P[Parse argv level by level]
    A[argv words] --> P
    P -->|success| R[Portable result]
    P -->|failure| E2["{ code, index }"]
```

The specification prescribes the declaration format, the validation rules,
the parsing procedure, and the output representation. The public API,
diagnostic presentation, and any typed numeric conversions are
implementation-defined.

## Checklist

- [ ] **Read KORML faithfully.** Reject duplicate mapping keys and malformed
      documents as `invalid_declaration`. Preserve keys and string values
      byte for byte.
- [ ] **Validate the whole declaration before parsing anything.** Exactly
      three root fields; `version` is exactly `kaira.command-declaration/v1`
      (anything else is `unsupported_version`); unknown fields are errors
      everywhere, including inside variant payloads.
- [ ] **Enforce the semantic constraints.** Short aliases unique per level,
      at least one child under `subcommands.commands`, nonnegative positional
      bounds with `max >= min`, a nonempty `separator` on every `separated`
      option, and only the four exact type names.
- [ ] **Scan each level left to right** following the
      [parser rules](../reference/parser-rules.md). Keep a fresh options map
      per level. Stop recognizing options after `--`. Descend into a
      subcommand immediately and never look back.
- [ ] **Implement the four lexical productions** for `int`, `float`,
      `string`, and `boolean` as *string* checks. Never let a host integer
      overflow or a floating-point parse decide acceptance.
- [ ] **Produce the portable result** with exactly `program`,
      `command_path`, and `levels`; omit absent options; emit `null` for
      `positionals` on non-positional tails and an empty array when a
      positional tail received nothing.
- [ ] **Report the first error in scan order** with the correct `code` and
      zero-based `index`; end-of-input errors use `argv.length`.
- [ ] **Pass the conformance suite.**

## Running the conformance suite

`conformance/v1.json` is a plain JSON document with three sections.

```json title="conformance/v1.json (abridged)"
{
  "format": "kaira.conformance/v1",
  "declarations": {
    "options": { "version": "kaira.command-declaration/v1", "program": "app", "command": { "…": "…" } }
  },
  "cases": [
    {
      "id": "short-attached",
      "declaration": "options",
      "argv": ["-o=--"],
      "ok": { "program": "app", "command_path": [], "levels": [ "…" ] }
    },
    {
      "id": "missing-spaced-value",
      "declaration": "options",
      "argv": ["--include", "--"],
      "error": { "code": "missing_value", "index": 0 }
    }
  ],
  "invalid_declarations": [
    { "id": "empty-separator", "declaration": { "…": "…" }, "error": { "code": "invalid_declaration" } }
  ]
}
```

A harness in any language does the same four things:

1.  For each entry in `declarations`, pass the already-decoded value to the
    validator and retain the validated declaration by name.
2.  For each entry in `cases`, look up the declaration, parse `argv`, and
    compare the outcome: a case has exactly one of `ok` or `error`. Compare the portable
    result structurally (object key order is immaterial, array order is not)
    and compare errors by `code` and `index` only.
3.  For each entry in `invalid_declarations`, assert that validation fails
    with the given `code` and no `index`.
4.  Separately, test that the KORML front end rejects malformed documents
    and duplicate keys. The JSON vectors are already decoded and therefore do
    not exercise that layer.

??? example "Sketch of a harness in Python"

    ```python
    import json
    from my_kaira import validate, parse, KairaError

    suite = json.load(open("conformance/v1.json"))
    decls = {name: validate(d) for name, d in suite["declarations"].items()}

    for case in suite["cases"]:
        decl = decls[case["declaration"]]
        try:
            got = {"ok": parse(decl, case["argv"])}
        except KairaError as err:
            got = {"error": {"code": err.code, "index": err.index}}
        expected = {k: case[k] for k in ("ok", "error") if k in case}
        assert got == expected, (case["id"], got, expected)

    for bad in suite["invalid_declarations"]:
        try:
            validate(bad["declaration"])
        except KairaError as err:
            assert err.code == bad["error"]["code"] and err.index is None, bad["id"]
        else:
            raise AssertionError(f'{bad["id"]} was accepted')
    ```

## Frequent nonconformances

!!! failure "Deciding acceptance with host numeric parsing"

    `--ratio 1.5e+1000` is a valid `float`. A host floating-point parser
    overflows or rejects it, which fails
    `lexically-validated-large-numbers`. Acceptance is decided by the
    lexical grammar on the text; conversion, if offered, is a separate step.

!!! failure "Expanding `-vo` as two flags"

    The grammar has no short-option clustering. `-vo` is a single
    unrecognized word and is reported as `unknown_option` at its index.

!!! failure "Accepting both `--name value` and `--name=value`"

    Each option declares one value style. The other form is
    `invalid_option_form`.

!!! failure "Resolving parent options inside a child level"

    After a subcommand word is consumed, only the child's declarations are
    in scope. `app test -v` is `unknown_option` at index 1 even when the root
    declares `-v`.

!!! failure "Re-tokenizing `argv` elements"

    `argv` elements are words. An element may contain whitespace, be empty,
    or be `--` itself (after a delimiter). Implementations do not split,
    trim, or unquote elements.

## Additional testing

The conformance vectors are a minimum. Implementations should additionally
test at least:

- numbers with hundreds of digits in both mantissa and exponent;
- Unicode strings, including combining characters and empty strings;
- every error code at both the first and a later `argv` index;
- repeated options interleaved with positionals and with `--`;
- short-alias collisions across sibling and parent-child levels.

Property-based testing is well suited to the model: generate a random
valid declaration and a random `argv`, and check that the outcome is a
function of those two inputs alone.
