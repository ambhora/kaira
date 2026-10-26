<img src="brand/kaira-logo.svg" alt="Kaira" width="300">

# Kaira specification

Kaira specifies a deterministic, language-independent command-line parser.
A program declares its command tree in KORML; an implementation receives that
declaration and an already-tokenized argument vector and produces the same
portable result or error in any language.

The declaration is flat: every command, at any depth, is one entry of a
`commands` mapping, and the tree is formed by listing child keys. Each
command has flags, options, and exactly one shape (`none`, `subcommands`,
or `positionals`). A `positionals` command declares named slots with
alignments and cardinalities such that the assignment of words to slots is
unique. A subcommand opens its own command level and scope. There is no
option abbreviation or clustering; any short alias must be declared.

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
commands:
  __main__:
    shape: positionals
    flags:
      verbose: {short: v}
    positionals:
      - input: {alignment: left}
```

For `argv = ["example", "-v", "report.txt"]`, the portable result is as
follows; `argv[0]` is kept in the vector but not interpreted:

```json
{
  "program": "example",
  "command": "__main__",
  "path": ["__main__"],
  "commands": {
    "__main__": {
      "flags": ["verbose"],
      "options": {},
      "positionals": {"input": "report.txt"}
    }
  }
}
```

Values are opaque strings: Kaira neither types nor validates them, so
numeric literals of any length reach the application unchanged. Typed
access, paths, and other application-specific interpretation are provided
by libraries and applications above the specification.

## Conformance contract

1. Read the declaration as KORML v0 or v1.0 and validate it.
2. Parse argument strings using Kaira v1 grammar.
3. Return the portable result or structured error.
4. Agree with the language-neutral conformance vectors.

No public API, runtime library, language, automatic help behavior, or
application execution behavior is prescribed here.

Both `--name value` and `--name=value` exist, but each option declares
which **one** it accepts. An optional single-character short alias follows
that same style; it is never generated from the long name.

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
