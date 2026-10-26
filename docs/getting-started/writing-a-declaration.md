---
title: Writing a declaration
description: An incremental guide to Kaira declarations, from an empty command to a nested command tree and multiple positional slots, with the argument vectors each step accepts and rejects.
hide:
  - navigation
---

# Writing a declaration

This page develops a declaration for a hypothetical build tool, `forge`,
from an empty command to a nested command tree. Each step shows the
declaration, accepted argument vectors with their results, and rejected
argument vectors with the resulting error code and index. Results are
abbreviated to the record of the relevant command where the rest is
unchanged.

## 1. The smallest program

A declaration has three root fields, and `commands` must contain
`__main__`. `shape: none` means the command accepts no bare words.

```yaml title="forge.korml"
version: kaira.command-declaration/v1
program: forge
commands:
  __main__:
    shape: none
```

| Command line | Outcome |
| --- | --- |
| `forge` | `{"flags": [], "options": {}, "positionals": {}}` |
| `forge now` | `unexpected_argument` at 1 — `shape: none` accepts no bare words. |

## 2. A flag

Flags live under `flags`; a short alias exists only when declared.

```yaml title="forge.korml" hl_lines="6-7"
version: kaira.command-declaration/v1
program: forge
commands:
  __main__:
    shape: none
    flags:
      verbose: {short: v}
```

| Command line | Outcome |
| --- | --- |
| `forge -v`, `forge --verbose` | `"flags": ["verbose"]` — the result always uses the long name. |
| `forge --verbose=true` | `invalid_option_form` at 1 — a flag never takes a value. |
| `forge -v --verbose` | `duplicate_option` at 2 — both spellings count as the same flag. |
| `forge --verb` | `unknown_option` at 1 — there is no prefix matching. |

## 3. Options

Options live under `options` and take exactly one value per occurrence.
Each declares one `style`: `spaced` (`--name value`) or `attached`
(`--name=value`); the other form is refused. `multiplicity: multiple`
allows repetition.

```yaml title="forge.korml" hl_lines="8-10"
version: kaira.command-declaration/v1
program: forge
commands:
  __main__:
    shape: none
    flags:
      verbose: {short: v}
    options:
      jobs: {style: attached}
      include: {style: spaced, multiplicity: multiple}
```

| Command line | Outcome |
| --- | --- |
| `forge --jobs=8 --include src --include tests` | `"options": {"jobs": "8", "include": ["src", "tests"]}` |
| `forge --jobs 8` | `invalid_option_form` at 1 — `jobs` is `attached`. |
| `forge --include=src` | `invalid_option_form` at 1 — `include` is `spaced`. |
| `forge --jobs=4 --jobs=8` | `duplicate_option` at 2 — a `single` option occurs at most once. |

`jobs` is `"8"`, a string. Kaira does not type or validate values; the
application (or a typed accessor of the library) converts it.

## 4. Positional values

`shape: positionals` accepts bare words and assigns them to the declared
slots. A slot is `single` and `required` by default; this one is
`multiple`, so it takes one or more words. Options may appear anywhere
among the positional words.

```yaml title="forge.korml" hl_lines="5 11-12"
version: kaira.command-declaration/v1
program: forge
commands:
  __main__:
    shape: positionals
    flags:
      verbose: {short: v}
    options:
      jobs: {style: attached}
      include: {style: spaced, multiplicity: multiple}
    positionals:
      - target: {alignment: center, multiplicity: multiple}
```

| Command line | Outcome |
| --- | --- |
| `forge app -v docs --include src` | `"flags": ["verbose"], "options": {"include": ["src"]}, "positionals": {"target": ["app", "docs"]}` |
| `forge` | `too_few_positionals` at 1 — the slot is required; the index is the end of input. |
| `forge app --clean` | `unknown_option` at 2 — dash-leading words are always options unless `--` came first. |

A slot whose count can vary (here: one or more) must be aligned `center`;
only one such slot is allowed per command. Step 7 shows why.

## 5. Passing arbitrary words through

The exact word `--` ends option recognition for the rest of the level.
Everything after it is a positional word, even if it starts with a dash.

| Command line | Outcome |
| --- | --- |
| `forge app -- --clean -j8` | `"positionals": {"target": ["app", "--clean", "-j8"]}` |
| `forge --include --` | `missing_value` at 1 — a spaced option never consumes `--`. An option that must accept the literal value `--` is declared `attached` and written `--name=--`. |

## 6. Subcommands

`shape: subcommands` lists child keys. Each child is its own entry of
`commands` with its own flags, options, and slots; nothing is inherited.
The word typed on the command line is the last segment of the key.

```yaml title="forge.korml"
version: kaira.command-declaration/v1
program: forge
commands:
  __main__:
    shape: subcommands
    flags:
      verbose: {short: v}
    subcommands: [__main__.build, __main__.clean]
  __main__.build:
    shape: positionals
    flags:
      release: {}
    positionals:
      - target: {alignment: center, multiplicity: multiple}
  __main__.clean:
    shape: none
```

For `forge -v build --release app`:

```json
{
  "program": "forge",
  "command": "__main__.build",
  "path": ["__main__", "__main__.build"],
  "commands": {
    "__main__":       {"flags": ["verbose"], "options": {}, "positionals": {}},
    "__main__.build": {"flags": ["release"], "options": {}, "positionals": {"target": ["app"]}}
  }
}
```

| Command line | Outcome |
| --- | --- |
| `forge clean` | `"command": "__main__.clean"`, two records, both empty. |
| `forge build -v app` | `unknown_option` at 2 — `verbose` belongs to `__main__`; inside `build` it is unknown. |
| `forge --release build` | `unknown_option` at 1 — `release` belongs to `build`. |
| `forge` | `missing_subcommand` at 1 — a `subcommands` command always requires a child. |
| `forge deploy` | `unknown_subcommand` at 1 — only listed children are accepted. |

## 7. Several positional slots

A command may declare several slots. Slots aligned `left` and `right` have
a fixed count; at most one slot, aligned `center`, may take a variable
number of words. The parser fills the fixed slots first and gives the rest
to the centre slot, so the assignment is unique for any number of words.

```yaml title="forge.korml"
version: kaira.command-declaration/v1
program: forge
commands:
  __main__:
    shape: positionals
    flags:
      force: {short: f}
    positionals:
      - source: {alignment: center, multiplicity: multiple}
      - destination: {alignment: right}
```

| Command line | Outcome |
| --- | --- |
| `forge a.txt b.txt dist/` | `"positionals": {"source": ["a.txt", "b.txt"], "destination": "dist/"}` |
| `forge -f a.txt dist/` | `"flags": ["force"]`, `"positionals": {"source": ["a.txt"], "destination": "dist/"}` |
| `forge a.txt -- -x dist/` | `"positionals": {"source": ["a.txt", "-x"], "destination": "dist/"}` |
| `forge dist/` | `too_few_positionals` at 2 — one word fills `destination`; `source` needs at least one. |

Declaring `source` as `left` with `multiplicity: multiple` is rejected as
`invalid_declaration`: a `left` slot must have a fixed count.

## Further reading

- [Command-line grammar](../explanation/grammar.md) describes levels,
  scopes, shapes, and slot assignment.
- The [KORML schema](../reference/schema.md) lists every field; the
  [parser rules](../reference/parser-rules.md) summarize the
  [normative specification](../reference/specification.md).
- Each [example](../examples/index.md) is a complete declaration with
  accepted and rejected argument vectors.
