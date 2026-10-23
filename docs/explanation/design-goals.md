---
title: Design goals
description: The properties Kaira is designed to guarantee, the features excluded to obtain them, and the relationship to common command-line conventions.
---

# Design goals

Kaira specifies a contract between a declaration and an argument vector
rather than the behavior of a particular library. The design follows from
five requirements.

## 1. Determinism

For a given declaration and argument vector, every conforming
implementation produces the same result or the same error code and index.
This excludes any feature whose outcome depends on heuristics, on the set
of other declared names, or on host-language behavior.

| Excluded feature | Reason |
| --- | --- |
| Option abbreviation (`--verb` for `--verbose`) | The meaning of an abbreviation changes when a new option with the same prefix is added. |
| Short-option clustering (`-abc`) | Ambiguous when a clustered letter takes a value. |
| Implicit short aliases | Two options with the same initial letter would collide silently. |
| Accepting both `--name value` and `--name=value` for one option | A value beginning with `-` is interpreted differently in each form. |
| Implicit `--help` or `--version` | Application behavior, not grammar. |
| Optional subcommands (stopping at a parent) | Makes the leaf command depend on the word count; a parent that can run on its own is declared with `shape: none` or `positionals` instead. |
| Value typing and validation | Numeric overflow, rounding, range, and Boolean spellings differ between languages; interpretation belongs to the library or application. |

## 2. Opaque values

Every value — option value, separator piece, or positional word — is
carried in the portable result as the original string. Kaira neither types
nor validates values, so acceptance never depends on the precision or range
of a host numeric type, on a locale, or on a Boolean spelling. Libraries may
offer typed accessors and applications apply their own validation; neither
can change which argument vectors are accepted or the portable result.

## 3. Per-level option scope

A subcommand opens a new command level with its own option scope. Option
declarations are not inherited, and no option is global. This keeps each
command declaration self-contained and gives the result a fixed shape: one
record in `commands` per selected command, keyed by the command's name.

## 4. Structured errors

A failure is reported as a code from a closed set together with a
zero-based index into `argv`. This is sufficient for an application to
locate the offending word and is language-neutral enough to be expressed in
a shared conformance suite. Message text, formatting, and suggestions are
implementation-defined.

## 5. Separation from the shell

The parser receives words, not a command string. Quoting, escaping,
globbing, environment expansion, and response-file handling are performed
by the shell or host before Kaira is invoked. The specification is
consequently independent of any particular shell and can be exercised
directly from a test harness.

## Illustration

```console
$ app --output=report.txt --include src --include tests -- --literal
```

- `--output=report.txt` is accepted because `output` is declared
  `attached`; `--output report.txt` would be `invalid_option_form`.
- `--include` is declared `spaced` with `multiplicity: multiple` and may therefore recur.
- `--` ends option recognition; `--literal` is a positional value.

Each acceptance decision is determined by a field of the declaration.

## Relationship to existing conventions

Kaira does not standardize GNU `getopt_long`, the POSIX utility syntax
guidelines, or the behavior of any existing tool. It is a strict subset of
widely used practice:

- long options introduced by `--`, with optional single-character short
  aliases introduced by `-`;
- `--` as the end-of-options delimiter;
- repeated options and separator-delimited lists, each declared explicitly.

Forms outside this subset — clustering, abbreviation, concatenated short
values such as `-ofile` — are rejected with a defined error code. In
exchange, a Kaira declaration is a complete, machine-checkable description
of the accepted input.
