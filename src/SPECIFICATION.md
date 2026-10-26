# Kaira command declarations and argv interpretation — v1 (draft)

## 1. Status and conformance

This document is normative. The KORML schema under `schema/` and the
conformance cases under `conformance/` form the remaining v1 contract.
Where these documents disagree, the following order applies:

1. The EBNF grammar in section 10 is the authoritative definition of the
   syntactic acceptance of argument vectors.
2. The prose of this document is authoritative for declaration reading and
   validation, semantic actions, error selection, and the portable result.
3. The KORML schema describes the structure of a declaration. It does not
   express every requirement of this document (for example value ranges,
   conditional presence of fields, and references between commands).

Any contradiction between these documents, or between them and the
conformance cases, is a specification defect. Examples are informative.

### 1.1 Terminology

**SHALL** and **SHALL NOT** state conformance requirements. **SHOULD** and
**SHOULD NOT** state recommendations for which justified exceptions are
possible. **MAY** states a permitted choice. **CAN** and **CANNOT** describe
capabilities or consequences and do not impose requirements. A prohibition
is always stated with **SHALL NOT**.

A conformant implementation validates the entire declaration before
examining the argument vector and produces the specified portable result or
error code and index for every input. Diagnostic wording, APIs, and internal
data structures are language-specific.

### 1.2 Normative references

**[KORML]** Korml Language Specification, versions v0 and v1
(`%!korml version 1.0`), <https://ambhora.github.io/korml/>.

There are two distinct input languages: the KORML declaration and the
command-line words represented by the argument vector. Kaira does not parse
command strings or shell quoting.

## 2. Inputs and declaration validation

### 2.1 Argument vector

The parser input `argv` is the ordered array of Unicode strings supplied by
the host, **including the invocation name** `argv[0]`. Each element is a
word (token); words are separated by whitespace in command-line notation.
Token boundaries supplied by an adapter are authoritative; the parser
operates on words, not on the original character stream. An adapter SHALL
NOT remove, insert, split, join, or modify elements of `argv`, including
`argv[0]`.

`argv[0]` is not interpreted. It is not matched against `program`, a
command word, or any declared spelling, and it belongs to no command level.
Scanning starts at index 1, and every error index refers to the complete
array. An empty `argv` is reported as `empty_argv` (section 7). Kaira
performs no trimming, case folding, Unicode normalization, environment
expansion, or escape interpretation.

### 2.2 Declaration source

A declaration source SHALL be a KORML v0 source or a KORML v1 stream that
contains exactly one document [KORML]. A source that begins with the
directive `%!korml version 1.0` SHALL be read as KORML v1; a source that
begins with any other `%!korml` directive is `invalid_declaration`; every
other source SHALL be read as KORML v0. A source that is not valid KORML of
the selected version, or a v1 stream with zero or more than one document,
is `invalid_declaration`.

The KORML reader SHALL reject duplicate mapping keys and SHALL preserve
mapping keys and scalar text unchanged.

### 2.3 Scalar decoding

A KORML scalar is text; its quoting style and source spelling are not
significant. Each field of a declaration has one of the following types,
and its scalar text SHALL satisfy the rule for that type:

| Type | Accepted scalar text | Decoded value |
| --- | --- | --- |
| string | any text | the text |
| identifier | the entire text matches `[A-Za-z][A-Za-z0-9_-]*` | the text |
| command key | the entire text matches `[A-Za-z_][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)*` | the text |
| short | the entire text matches `[A-Za-z0-9]` | the text |
| boolean | exactly `true` or `false` | the Boolean |
| integer | the entire text is `0` or matches `[1-9][0-9]*`, and its value is at most 2⁶³ − 1 | the integer |
| count limit | an integer as above, or exactly `unbounded` | the integer, or unbounded |
| enumeration | exactly one of the listed words | the word |

2⁶³ − 1 = 9 223 372 036 854 775 807 is the largest value representable in
both signed and unsigned 64-bit integers. A mapping or sequence where a
scalar is required, or a scalar where a mapping or sequence is required, is
`invalid_declaration`. All matching is case-sensitive.

### 2.4 Document structure

The root of the document SHALL be a mapping with exactly the keys
`version`, `program`, and `commands`. `version` is a string that SHALL be
exactly `kaira.command-declaration/v1`. `program` is an identifier; it
labels the result and is not matched against `argv[0]`. `commands` is a
mapping from *command keys* to command declarations. The declaration is
flat: every command, at any depth of the command tree, is an entry of
`commands`, and the tree is expressed by reference.

The *word* of a command key is the text after its last `.`, or the whole
key if it contains none. The key `__main__` SHALL be present and denotes the
root command. Unknown fields are invalid everywhere.

### 2.5 Commands

Every command has a required `shape`, an enumeration of exactly one of:

| `shape` | Bare words at this level are | Required field |
| --- | --- | --- |
| `none` | not accepted | — |
| `subcommands` | the word of one listed child, which opens the next level | `subcommands` |
| `positionals` | positional values assigned to the declared slots | `positionals` |

Optional fields are `help` (a string with no parsing effect), `flags`, and
`options`, both mappings defaulting to empty. `subcommands` SHALL be
present if and only if `shape` is `subcommands`, and `positionals` SHALL be
present if and only if `shape` is `positionals`; each is a nonempty
sequence.

Tree constraints:

1. `subcommands` lists command keys. Every listed key SHALL exist in
   `commands`; `__main__` SHALL NOT be listed. The words of the keys listed
   by one command SHALL be distinct.
2. Every key other than `__main__` SHALL be listed by exactly one command.
3. Every key SHALL be reachable from `__main__` by following `subcommands`
   lists.

Constraints 2 and 3 together make the commands a tree rooted at `__main__`:
every command other than the root has exactly one parent, and there is no
cycle, because a cycle reachable from the root would require a command with
two parents or a listing of `__main__`.

The dotted prefix of a key carries no meaning beyond readability; only the
word is matched against `argv`, and only the listing establishes the tree.

### 2.6 Flags and options

`flags` maps an identifier, the long name, to a mapping with optional
`short` (a short) and `help` (a string). A flag takes no value.

`options` maps an identifier, the long name, to a mapping with required
`style` (`spaced` or `attached`) and optional `short`, `help`,
`multiplicity` (`single`, the default, or `multiple`), and `separator` (a
nonempty string). `separator` SHALL NOT be present unless `multiplicity` is
`multiple`. An option consumes exactly one value per occurrence.

Each flag and option has a *permitted number of occurrences* per level,
counted across its long and short spellings combined:

| Kind | Permitted occurrences |
| --- | --- |
| flag | at most one |
| option, `single` | at most one |
| option, `multiple`, with `separator` | at most one; its value is split (section 4) |
| option, `multiple`, without `separator` | any number; each contributes one value |

Within one command, long names SHALL be distinct across `flags` and
`options` together, and so SHALL short aliases. Names and aliases MAY be
reused at a different level.

### 2.7 Positional slots

`positionals` is a sequence of single-key mappings; each key is the slot
name, an identifier distinct within the command, and each value declares
the slot with the following fields and no others:

| Field | Type | Default |
| --- | --- | --- |
| `alignment` | `left`, `center`, `right` | required |
| `multiplicity` | `single`, `multiple` | `single` |
| `required` | boolean | `true` |
| `cardinality.min` | integer | `1` if `required`, else `0` |
| `cardinality.max` | count limit | `1` if `single`, else `unbounded` |

`cardinality` is a mapping with optional `min` and `max`. Let `min` and
`max` be the effective bounds after defaults. The following SHALL hold:

1. `max >= 1` and `max >= min`; `multiplicity: single` implies `max = 1`;
   `required: true` implies `min >= 1`; `required: false` implies
   `min = 0`.
2. A `left` or `right` slot has a fixed count: `min = max`. Because
   `max >= 1`, such a slot is always required.
3. At most one slot has `alignment: center`. Only that slot MAY have
   `min != max` or `max: unbounded`.
4. Within one command, the sum of all `min` values, and the sum of all
   `max` values when none is `unbounded`, SHALL NOT exceed 2⁶³ − 1.
5. The *effective order* of slots is: all `left` slots in sequence order,
   then the `center` slot if any, then all `right` slots in sequence order.

Rules 2 and 3 make the assignment of positional words to slots unique for
every word count (section 3). Rule 4 guarantees that every count computed
in section 3 fits in a 64-bit integer.

### 2.8 Removed fields

`allow_explicit_empty`, `tail`, `value_style`, `value`, and the option
kinds `flag`/`scalar`/`repeatable`/`separated` of preliminary drafts are
not part of v1 and are unknown fields.

## 3. Grammar and parsing procedure

For a declared long name `output` and optional short name `o`, the only
recognized spellings are `--output` and `-o`. There is no abbreviation,
short-option clustering (`-abc`), short value concatenation (`-ofile`),
or implicit negation. Short aliases exist only when declared; a long option
is never shortened automatically. The same value style applies to both
spellings.

| Kind and style | Accepted | Rejected |
| --- | --- | --- |
| Flag | `--verbose`, `-v` | `--verbose=true`, `-v=true` |
| Spaced option | `--output file`, `-o file` | `--output=file`, `-o=file` |
| Attached option | `--output=file`, `-o=file` | `--output file`, `-o file` |

A spaced option consumes the immediately following token, **even if it
resembles an option**, except that the exact token `--` is reserved and
causes `missing_value`. An attached option consumes everything after the
first `=`, including an empty string or additional equals signs.
Thus `--output=--` passes the literal value `--`.

The following is an **informative sketch** of the declaration-parameterized
grammar; the complete normative EBNF appears in section 10:

```text
none level:         option*
subcommands level:  option* subcommand child-level
positionals level:  (option | positional)* [-- positional*]
```

The delimiter `--` is an exact word, not a declared option. After it,
every remaining token is positional data. Options and positional arguments
MAY interleave freely in a positionals level:

```text
app target1 --verbose target2 --include dir target3
```

Scanning starts at index 1 with the root command `__main__` as the current
level. For each command level, initialize an empty flag list, an empty
options map, and an empty positional word list, then scan tokens left to
right:

1. If the token is exactly `--`, accept it only for shape `positionals`:
   consume it, disable option recognition for the rest of `argv`, and
   treat all following tokens as positional words. For shapes `none` and
   `subcommands`, report `unexpected_delimiter`.
2. If the token begins with `-`, it is an option token. Its *spelling* is
   the text before its first `=`, or the whole token if it contains none.
   The following checks are applied in this order; the first that fails
   determines the error, reported at the index of this token:
    1. *Recognition.* The spelling SHALL be the declared long (`--name`)
        or short (`-s`) spelling of a flag or option of the current level;
        otherwise `unknown_option`. Recognition uses only the current
        level's declarations.
    2. *Form.* A flag token and a spaced option token SHALL NOT contain
        `=`; an attached option token SHALL contain `=`. Otherwise
        `invalid_option_form`.
    3. *Occurrence.* The occurrence SHALL NOT exceed the permitted number
        of occurrences of the flag or option (section 2.6); otherwise
        `duplicate_option`.
    4. *Value.* A spaced option SHALL be followed by a token that is not
        exactly `--`; otherwise `missing_value`. That token is consumed as
        the value. The value of an attached option is the text after the
        first `=` of the option token.
3. For any other token (a *bare* token), act according to the shape:
    - `none`: report `unexpected_argument`.
    - `subcommands`: require the word of a listed child, otherwise report
      `unknown_subcommand`; consume it, then **immediately** descend into
      that child's level. No parent flags or options are recognized beyond
      that boundary.
    - `positionals`: append the token to the positional word list and
      continue scanning this level; subsequent options remain recognizable.
      If the sum of all slot `max` values is finite and the list now
      exceeds it, report `too_many_positionals` at this token.
4. At end of input:
    - For shape `subcommands`, report `missing_subcommand`. End of input
      at such a level means that no child was selected, because selecting a
      child leaves the level.
    - For shape `positionals`, let `n` be the number of positional words.
      If `n` is less than the sum of the `min` values of all slots, report
      `too_few_positionals` at index `argv.length`. Otherwise assign the
      words to slots in effective order: every `left` and `right` slot
      takes exactly its `min` (= `max`) words, and the `center` slot, if
      present, takes the remaining words. Step 3 and the preceding check
      guarantee that the number of remaining words lies within the
      `center` slot's `[min, max]`, and that it is zero when there is no
      `center` slot.

After `--`, step 2 is disabled and every token follows step 3 for a
positionals level, even if it looks like an option or another delimiter.
A dash-leading positional therefore requires a preceding `--`, which MAY
appear **after earlier positional arguments**. Parent and child scopes
never overlap. A level CANNOT both select subcommands and accept positional
values.

## 4. Occurrences, splitting, and counts

A flag or option that occurs more often than its permitted number of
occurrences (section 2.6) is `duplicate_option`, reported at the first
occurrence beyond that number. No flag or option is implicitly required;
absent ones have no default value.

A `multiple` option with `separator` consumes one value and splits it from
left to right at each literal, nonoverlapping occurrence of its separator.
Empty pieces are preserved: with `;`, `";a;;"` yields `["", "a", "", ""]`,
and `""` yields `[""]`.

## 5. Values

Every option value, separator piece, and positional word is an opaque
Unicode string. Kaira does not interpret, validate, convert, trim, or
normalize values; the only operation it performs on a value is splitting
on a declared `separator`. There are no value types in a declaration, and
`invalid_value` is not a Kaira error.

Interpretation of values — as numbers, Booleans, paths, dates,
enumerations, or `NAME=VALUE` assignments — belongs to layers above this
specification: a library MAY offer typed accessors, and an application
applies whatever validation it needs after a successful parse. Such layers
SHALL NOT change which argument vectors Kaira accepts or the portable
result. In particular, a word such as `-1` or `true` is a string like any
other, and a switch is expressed by a flag, not by an option value.

## 6. Portable successful result

The result is a JSON-compatible object with exactly these four fields:

```json
{
  "program": "example",
  "command": "__main__.build",
  "path": ["__main__", "__main__.build"],
  "commands": {
    "__main__": {"flags": ["verbose"], "options": {}, "positionals": {}},
    "__main__.build": {
      "flags": [],
      "options": {"output": "a.log", "include": ["src", "inc"], "jobs": "4"},
      "positionals": {"target": ["app"], "out": "dist"}
    }
  }
}
```

- `program` is copied from the declaration.
- `command` is the key of the last selected level; `path` lists the keys
  of all selected levels from `__main__` to `command`, in order.
- `commands` maps each key in `path` to that level's record and contains
  no other keys. Each record has exactly `flags`, `options`, and
  `positionals`.
- `flags` is an array of the long names of the flags present, in
  occurrence order. Absent flags are omitted.
- `options` maps the canonical **long names** of present options to values.
  Unseen options are omitted. A `single` option yields one string; a
  `multiple` option yields an array of strings in occurrence (or piece)
  order.
- `positionals` maps slot names to values for the slots that received at
  least one word; slots with zero words are omitted. A `single` slot yields
  one string; a `multiple` slot yields an array of strings in word order.
  For shapes `none` and `subcommands`, `positionals` is `{}`.
- Every value is a JSON string, exactly as supplied in `argv`. `argv[0]`
  does not appear in the result.

JSON object key order is immaterial; all array order is significant.
The only native JSON numbers in this representation are structural
metadata such as error indices; argument values never become JSON numbers
or Booleans. Implementations MAY expose a native, typed result in addition
to this one, but SHALL expose or be able to serialize the portable
representation.

## 7. Portable failures and precedence

Declaration validation is complete before `argv` is examined and proceeds
in this order:

1. The source SHALL be read as KORML (section 2.2); otherwise
   `invalid_declaration`.
2. The root SHALL be a mapping that contains the key `version` with a
   scalar value; otherwise `invalid_declaration`.
3. If the `version` text is not exactly `kaira.command-declaration/v1`, the
   error is `unsupported_version`, whatever else the document contains.
4. Every other requirement of section 2 SHALL hold; otherwise
   `invalid_declaration`.

Declaration errors have no `index`. Which requirement of step 4 was violated
is not part of the portable representation.

For argument errors, the representation has exactly `code` and `index`,
where `index` is zero-based in the complete `argv`, including `argv[0]`.
End-of-input errors use `index = argv.length`.

| Code | Reported at (`index`) |
| --- | --- |
| `empty_argv` | 0; `argv` has no elements, so there is no invocation name. |
| `unknown_option` | Option token whose spelling is not declared at the current level. |
| `invalid_option_form` | Declared flag or option token with the wrong form (section 3, step 2.2). |
| `duplicate_option` | Token of a flag or option beyond its permitted number of occurrences (section 2.6). |
| `missing_value` | Spaced option token that is last in `argv` or followed by `--`. |
| `unexpected_argument` | First bare token on shape `none`. |
| `unknown_subcommand` | Bare token that is not a listed child's word. |
| `missing_subcommand` | End index for shape `subcommands`. |
| `unexpected_delimiter` | `--` token on shape `none` or `subcommands`. |
| `too_few_positionals` | End index. |
| `too_many_positionals` | Index of the first positional token beyond the finite total maximum. |

Argument errors are reported in this order: first `empty_argv`; then errors
detected during the left-to-right scan of section 3 (steps 1–3), at the
first token that fails, with the checks of step 2 applied in the order
given there; then `missing_subcommand` or `too_few_positionals` at end of
input. Diagnostic messages are not portable.

## 8. Versioning and non-goals

V1 is a **closed** format. Any version other than
`kaira.command-declaration/v1` gives `unsupported_version`. Unknown fields
are invalid, not ignored. Any behavior change affecting results or error
categories requires a future declaration version. An implementation MAY
support multiple versions with explicit dispatch on the `version` field.

The command language is intentionally narrow: it is not an attempt to
implement GNU-style or other general-purpose CLI conventions. The Kaira
model does not include shell tokenization, global/inherited options,
environment expansion, response files, option defaults and groups, implicit
`--help`, short-option clustering, prefix matching, optional subcommands,
value typing or validation, Unicode normalization, filesystem validation,
or application execution.

## 9. Conformance

The file `conformance/v1.json` defines language-neutral test cases.
Declarations in that file are given in decoded form: KORML scalars appear
as the JSON strings, numbers, and Booleans that section 2.3 decodes them
to. Conformant implementations SHALL pass the normative cases.
Language-specific test harnesses are free to choose their API, but SHALL
compare portable success values and error code/index, not human-readable
messages.

## 10. Normative EBNF grammar

This grammar is the **source of truth for syntax**. Sections 1–9 specify
semantic restrictions, declaration validation, error priority, and portable
output; they SHALL NOT extend the syntax below.

EBNF terminals in quotes denote entire **words**, not substrings of a
character stream; the only intra-word distinction the grammar makes is the
split of an option token at its first `=`. The token stream is a sequence
of words separated by one or more whitespace characters when written as a
command line. Whitespace is a separator, not part of a word in this
abstract syntax. A host adapter that supplies `argv` SHALL preserve its
existing word boundaries; the core parser SHALL NOT split, trim, unquote,
or re-tokenize an `argv` element. This grammar specifies no shell escaping
or quoting syntax. An empty word CAN be supplied by an adapter, but CANNOT
be written as an unquoted word in the whitespace notation.

The grammar is *indexed by a validated declaration*. In the productions
below, `declared-*` sets and `value-style` are determined exclusively by
that declaration; they are not lexical shortcuts or prefix matches.
Different command levels have different declared sets. A recursive child
level starts immediately after its exact subcommand word.

```ebnf
invocation           = invocation-name, root-level ;
root-level           = none-level | positional-level | subcommand-level ;
child-level          = none-level | positional-level | subcommand-level ;

none-level           = { option } ;
positional-level     = { option | positional-word }, [ end-of-options,
                         { raw-positional-word } ] ;
subcommand-level     = { option }, [ declared-subcommand, child-level ] ;

option               = declared-flag | declared-spaced-option
                     | declared-attached-option ;
declared-flag        = declared-flag-spelling ;
declared-spaced-option = declared-spaced-spelling, value-word ;
declared-attached-option = declared-attached-spelling, "=", attached-value ;
end-of-options       = "--" ;

(* Atomic word classes are defined by the following constraints. *)
invocation-name      = ? any word; argv[0], not interpreted ? ;
declared-subcommand  = ? one exact declared child name word ? ;
declared-flag-spelling = ? exact declared --long or -short flag word ? ;
declared-spaced-spelling = ? exact declared --long or -short spaced-style option word ? ;
declared-attached-spelling = ? exact declared --long or -short attached-style option prefix ? ;
value-word           = ? one word other than -- ? ;
positional-word      = ? bare word not beginning with - ? ;
raw-positional-word  = ? any word, including -- or a dash-leading word ? ;
attached-value       = ? suffix of the SAME word after the FIRST =, possibly empty ? ;
```

An empty `argv` matches no `invocation`; it is `empty_argv` (section 7).

For attached options, the `declared-attached-spelling`, `=`, and
`attached-value` productions together consume **exactly one word**.
For spaced options, the spelling and `value-word` consume **exactly two
words**. These are atomic word-pattern rules, not a license to combine
arbitrary tokens or split attached values on whitespace. Other occurrences
of `=` belong to the attached value. An attached option's value CAN be
empty.

`invocation-name`, `value-word`, `positional-word`, `raw-positional-word`,
and `attached-value` are not inspected further: any Unicode string is
admitted, and the word is carried into the result unchanged (section 5),
except `invocation-name`, which does not appear in the result.

The subcommand branch of `subcommand-level` is syntactically optional so
that the end-of-input condition is expressible; semantically it SHALL
occur, and its absence is `missing_subcommand` (section 7).
Positional counts, slot assignment, option occurrence restrictions, and
error-code selection are semantic checks defined above. `--` is reserved
at every level and is accepted only in the `positional-level` delimiter
production; it terminates option recognition for that level. No production
admits abbreviated options, implicit short spellings, concatenated short
values, or clusters.
