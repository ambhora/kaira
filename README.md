# Kaira specification

Kaira specifies a deterministic, language-independent command-line parser.
A program declares its command tree in KORML; an implementation receives that
declaration and an already-tokenized argument vector and produces the same
portable result or error in any language.

The grammar is deliberately small: each command has declared options and
exactly one tail mode (empty, subcommands, or positionals). Options and
positionals may be interleaved within a positional command. A subcommand
starts its **own** command level and option scope. There is no option
abbreviation or clustering; any short alias must be explicitly declared.

**This repository is the specification, not a parser implementation.** It
defines the declaration format, parsing semantics, results, and conformance
vectors. Language libraries implement the contract independently.

## Specification v1 (draft)

- [Normative specification](src/SPECIFICATION.md)
- [KORML declaration schema](schema/kaira.command-declaration.v1.korml)
- [Portable conformance vectors](conformance/v1.json)
- [Documentation](docs/index.md)

The draft is not yet declared stable. Once v1 is stabilized, any incompatible
grammar or result changes require a new declaration version.

## Example

```yaml
version: kaira.command-declaration/v1
program: example
command:
  options:
    verbose:
      flag:
        short: v
  tail:
    positionals:
      positionals:
        name: input
        value: string
        min: 1
        max: 1
```

For `argv = ["-v", "report.txt"]` (without `argv[0]`), the portable
result is:

```json
{
  "program": "example",
  "command_path": [],
  "levels": [
    {
      "options": {"verbose": true},
      "positionals": {"input": ["report.txt"]}
    }
  ]
}
```

The core value types are `int`, `float`, `string`, and `boolean` only.
Arbitrary-length numeric literals retain their original decimal text in
portable results; Boolean values are represented as booleans. Paths and
other application-specific types are built on top of `string`, and language
libraries MAY offer additional native numeric conversions.

## Conformance contract

1. Load and validate the KORML declaration.
2. Parse argument strings using Kaira v1 grammar.
3. Return the portable result or structured error.
4. Agree with the language-neutral conformance vectors.

No public API, runtime library, language, automatic help behavior, or
application execution behavior is prescribed here.

Both `--name value` and `--name=value` are supported, but each
value-taking option declares which **one** it accepts. An optional
single-character short alias follows that same style; it is never
generated from the long name.

## Documentation

The rendered documentation lives at <https://ambhora.github.io/kaira/>. It is
built with ProperDocs and the Material theme, and includes a guided tour,
an implementer's checklist, an error-code reference, and worked examples.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e .
python scripts/sync_specification.py
properdocs serve
```

Run `python scripts/sync_specification.py` before `properdocs build --strict`.
The generated `docs/reference/specification.md` is a byte-for-byte copy of
`src/SPECIFICATION.md`; edit only the file in `src/`.
