# Kaira command declarations and argv interpretation — v1 (draft)

## 1. Status and conformance

This document is normative. The KORML schema under `schema/` and the
conformance cases under `conformance/` form the remaining v1 contract.
The EBNF grammar in the final section of this document is the
authoritative definition of syntactic acceptance. The prose defines
declaration-dependent constraints, semantic actions, and result mapping.
If prose, schemas, examples, or conformance cases contradict the grammar
on syntactic acceptance, the grammar prevails and the contradiction is a
specification defect. Examples are informative.

**SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, **MAY NOT**,
**CAN**, and **CANNOT** have distinct meanings in this specification.
**SHALL** and **SHALL NOT** state conformance requirements;
**SHOULD** and **SHOULD NOT** state recommendations for which justified
exceptions are possible; **MAY** and **MAY NOT** express permitted or
forbidden choices; **CAN** and **CANNOT** describe capabilities or
possibilities, not implementation requirements.
A conformant implementation validates the entire declaration before parsing
arguments and produces the specified portable result or error code/index for
every accepted input. Diagnostic wording, APIs, and internal data structures
are language-specific.

There are two distinct input languages: the KORML declaration and the
whitespace-separated command-line words represented by the argument vector. Kaira does not parse command strings
or shell quoting. The KORML reader SHALL reject duplicate mapping keys and
preserve mapping keys and string values unchanged.

## 2. Inputs and declaration validation

The parser input is `argv`, an ordered array of Unicode strings **excluding
the executable name**. Each element is a word (token); words are separated
by whitespace in command-line notation. Token boundaries supplied by an
adapter are authoritative; the portable parser operates on words, not
on the original character stream. Native adapters MAY decode and strip their host's
`argv[0]`. Kaira performs no trimming, case folding, Unicode normalization,
environment expansion, or escape interpretation.

### 2.1 Document structure

The root KORML mapping has exactly `version`, `program`, and `commands`.
`version` is exactly `kaira.command-declaration/v1`. The `program` field
labels the result; it is not matched against an executable filename.
`commands` is a mapping from *command keys* to command declarations. The
declaration is flat: every command, at any depth of the command tree, is an
entry of `commands`, and the tree is expressed by reference.

Identifiers match the entire ASCII pattern `[A-Za-z][A-Za-z0-9_-]*`.
A command key matches `[A-Za-z_][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)*`;
its *word* is the text after the last `.`, or the whole key if it contains
none. The key `__main__` SHALL be present and denotes the root command.
`short` aliases contain exactly one ASCII letter or digit, matching
`[A-Za-z0-9]`. All matching is case-sensitive. Unknown fields are invalid
everywhere.

### 2.2 Commands

Every command has a required `shape`, exactly one of:

| `shape` | Bare words at this level are | Required field |
| --- | --- | --- |
| `none` | not accepted | — |
| `subcommands` | the word of one listed child, which opens the next level | `subcommands` |
| `positionals` | positional values assigned to the declared slots | `positionals` |

Optional fields are `help` (a string with no parsing effect), `flags`, and
`options`, both mappings defaulting to empty. `subcommands` SHALL be
present iff `shape` is `subcommands` and `positionals` SHALL be present
iff `shape` is `positionals`; each is a nonempty list.

Tree constraints:

1. `subcommands` lists command keys. Every listed key SHALL exist in
   `commands`; `__main__` SHALL NOT be listed. The words of the keys listed
   by one command SHALL be distinct.
2. Every key other than `__main__` SHALL be listed by exactly one command.
   Consequently the commands form a tree rooted at `__main__`.

The dotted prefix of a key carries no meaning beyond readability; only the
word is matched against `argv`, and only the listing establishes the tree.

### 2.3 Flags and options

`flags` maps a long name to a mapping with optional `short` and `help`.
A flag takes no value and MAY occur at most once per level.

`options` maps a long name to a mapping with required `value` (`int`,
`float`, `string`, or `boolean`) and `style` (`spaced` or `attached`),
and optional `short`, `help`, `multiplicity` (`single`, the default, or
`multiple`), and `separator`. An option consumes exactly one value per
occurrence. A `single` option MAY occur at most once. A `multiple` option
without `separator` MAY occur any number of times, each occurrence
contributing one value. A `multiple` option with a nonempty string
`separator` MAY occur at most once and its one value is split (section 4).
`separator` is invalid without `multiplicity: multiple`.

Within one command, long names SHALL be distinct across `flags` and
`options` together, and so SHALL short aliases. Names and aliases MAY be
reused at a different level.

### 2.4 Positional slots

`positionals` is a list of single-key mappings; each key is the slot name
(distinct within the command) and each value declares the slot:

| Field | Values | Default |
| --- | --- | --- |
| `alignment` | `left`, `center`, `right` | required |
| `value` | a value type (section 5) | required |
| `multiplicity` | `single`, `multiple` | `single` |
| `required` | boolean | `true` |
| `cardinality.min` | integer ≥ 0 | `1` if `required`, else `0` |
| `cardinality.max` | integer, or `unbounded` | `1` if `single`, else `unbounded` |

Let `min` and `max` be the effective bounds after defaults. The following
SHALL hold:

1. `max >= min`; `multiplicity: single` implies `max = 1`;
   `required: true` implies `min >= 1`; `required: false` implies
   `min = 0`.
2. A `left` or `right` slot has a fixed count: `min = max`.
3. At most one slot has `alignment: center`. Only that slot MAY have
   `min != max` or `max: unbounded`.
4. The *effective order* of slots is: all `left` slots in list order, then
   the `center` slot if any, then all `right` slots in list order.

Rules 2 and 3 make the assignment of positional words to slots unique for
every word count (section 3).

### 2.5 Additional constraints

1. Value type names are exactly the four of section 5.
2. The KORML reader SHALL reject duplicate mapping keys; such documents are
   `invalid_declaration`.
3. `allow_explicit_empty`, `tail`, `value_style`, and the option kinds
   `flag`/`scalar`/`repeatable`/`separated` of preliminary drafts are not
   part of v1 and are unknown fields.

## 3. Grammar and parsing procedure

For a declared long name `output` and optional short name `o`, the only
recognized names are `--output` and `-o`. There is no abbreviation,
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
grammar; the complete normative EBNF appears at the end of this document:

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

For each command level, initialize an empty flag list, an empty options
map, and an empty positional word list, then scan tokens left to right:

1. If an exact `--` token occurs, accept it only for shape `positionals`.
   Consume it, disable option recognition, and treat all following tokens
   as positional words. Otherwise report `unexpected_delimiter`.
2. If a token begins with `-`, require a declared long or short spelling
   of a flag or option of this level. Check its form and occurrence limit,
   consume and validate its value where applicable (option values are
   validated as they are consumed). A forbidden attached/spaced form is
   `invalid_option_form`; an undeclared dash-leading token is
   `unknown_option`. All recognition at this level uses only the
   level's own declarations.
3. For a bare token, act according to the shape:
   - `none`: report `unexpected_argument`.
   - `subcommands`: require the word of a listed child, consume it, then
     **immediately** descend into that child's level. No parent flags or
     options are recognized beyond that boundary.
   - `positionals`: append the token to the positional word list and
     continue scanning this level; subsequent options remain recognizable.
     If the sum of all slot `max` values is finite and the list now
     exceeds it, report `too_many_positionals` at this token.
4. At end of input: for shape `subcommands`, report `missing_subcommand`
   if no child was selected. For shape `positionals`, assign the positional
   words to slots in effective order: every slot with a fixed count takes
   exactly `min` words; the `center` slot, if present, takes the remaining
   words, whose number SHALL lie within its `[min, max]`, otherwise report
   `too_few_positionals` (index `argv.length`). Then validate each word
   against its slot's value type in word order; the first failure is
   `invalid_value` at that word's index.

After `--`, step 2 is disabled and every token follows step 3 for a
positionals level, even if it looks like an option or another delimiter.
A dash-leading positional therefore requires a preceding `--`, which may
appear **after earlier positional arguments**. Parent and child scopes
never overlap. A level cannot both select subcommands and accept positional
values.

## 4. Occurrences, splitting, and counts

A flag and a `single` option MAY occur at most once per level, across long
and short spellings combined. Duplicate use is `duplicate_option`. A
`multiple` option without `separator` MAY occur any number of times. No
flag or option is implicitly required; absent ones have no default value.

A `multiple` option with `separator` consumes one value and splits it from
left to right at each literal, nonoverlapping occurrence of its separator.
Empty pieces are preserved: with `;`, `";a;;"` yields `["", "a", "", ""]`,
and `""` yields `[""]`. Each piece undergoes value validation in order.
Such an option itself cannot recur.

## 5. Portable base types and value validation

Kaira v1 defines **exactly four** primitive value types: `int`, `float`,
`string`, and `boolean`. Every value-taking option and positional SHALL
specify one of these exact, case-sensitive names. A different type name,
including `integer`, `path`, `assignment`, or `command`, is an
`invalid_declaration`. These names are not aliases.

| Type | Meaning and whole-value validation |
| --- | --- |
| `int` | A signed, base-ten integer with an arbitrary number of ASCII decimal digits. The exact lexical production appears in section 10. |
| `float` | A finite, base-ten floating-point literal with an arbitrary number of mantissa and exponent digits. No particular precision, binary format, range, or rounding behavior is implied. |
| `string` | Any Unicode string, including the empty string, without normalization or additional validation. |
| `boolean` | Exactly the lowercase words `true` and `false`. |

Both numeric types are **unbounded at the lexical level**. Implementations
SHALL validate them without host-integer overflow, host-floating-point
rounding, underflow, or overflow determining acceptance. Numeric syntax
uses ASCII characters only; there are no separators, prefix radices,
`NaN`, or infinity literals. For example, `+1` and `01` are invalid for
`int`; `-0` is valid for `float` but not `int`. Integer-shaped decimal
strings such as `1` are also valid `float` values. A sign on a `float`
mantissa, if present, is `-`; an exponent MAY use `+` or `-`.

The language-independent *lexical values* of `int` and `float` are their
original strings. No conversion to native numeric types is required by
Kaira. A language binding MAY provide typed numeric conversions using its
own rules, but failures, range limits, and loss of precision in that
additional API SHALL NOT change Kaira's lexical acceptance or portable
result. A binding CAN use arbitrary-precision numeric libraries or retain
the decimal text. The parser does not perform arithmetic.

A `boolean` value is represented as a Boolean, not as its original text.
A `string` value is preserved unchanged. A flag carries no value: its
presence is recorded by name and its absence by omission.

Types such as filesystem paths, assignments, dates, commands, or enums
belong to layers **above** this core. Such a layer CAN declare a `string`
value and impose additional validation or interpretation after successful
Kaira parsing. Kaira v1 itself SHALL NOT silently apply those checks or
accept extra primitive type names. The KORML schema's own `integer` and
`boolean` scalars used for *declaration metadata* (such as `cardinality`
bounds or `required`) are separate from Kaira's `value` type names.

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
      "options": {"output": "a.log", "include": ["src", "inc"]},
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
- `flags` is an array of the long names of the flags present, in first
  occurrence order. Absent flags are omitted.
- `options` maps the canonical **long names** of present options to values.
  Unseen options are omitted. A `single` option yields one value
  representation; a `multiple` option yields an array of them in occurrence
  (or piece) order.
- `positionals` maps slot names to values for the slots that received at
  least one word; slots with zero words are omitted. A `single` slot yields
  one value representation; a `multiple` slot yields an array in word
  order. For shapes `none` and `subcommands`, `positionals` is `{}`.
- A `boolean` value is a JSON Boolean; a `string`, `int`, or `float` value
  is a string.

JSON object key order is immaterial; all array order is significant.
The only native JSON numbers in this representation are structural
metadata such as error indices; decimal `int` and `float` arguments never
become JSON numbers. This distinction prevents loss of precision during
interchange. Implementations MAY expose a native, typed result in addition
to this one, but SHALL expose or be able to serialize the portable
representation.

## 7. Portable failures and precedence

Invalid declarations fail before argument parsing with `invalid_declaration`
or `unsupported_version`, and have no `index`. Duplicate KORML keys and
malformed KORML are `invalid_declaration`.
For argv parsing errors, the representation has exactly `code` and
`index`, where `index` is zero-based in the vector excluding `argv[0]`.
End-of-input errors use `index = argv.length`.

| Code | Reported at (`index`) |
| --- | --- |
| `unknown_option` | Unrecognized dash-leading token. |
| `invalid_option_form` | Declared flag or option token with invalid value style. |
| `missing_value` | Spaced option token without usable next token. |
| `duplicate_option` | Second token of a flag or `single` option. |
| `invalid_value` | Value token, attached-option token, or positional token. |
| `unexpected_argument` | First bare token on shape `none`. |
| `unknown_subcommand` | Bare token that is not a listed child's word. |
| `missing_subcommand` | End index for shape `subcommands`. |
| `unexpected_delimiter` | `--` token on shape `none` or `subcommands`. |
| `too_few_positionals` | End index. |
| `too_many_positionals` | Index of the first positional token beyond the finite total maximum. |

Errors are reported in this order: first, errors detected during the
left-to-right scan of section 3 (steps 1–3), at the first token that fails;
then `missing_subcommand` or `too_few_positionals` at end of input; then
`invalid_value` for positional words, in word order. Option values are
validated during the scan. Duplicate option detection precedes validation
of that option's second value. Diagnostic messages are not portable.

## 8. Versioning and non-goals

V1 is a **closed** format. Any unrecognized version gives
`unsupported_version`. Unknown fields are invalid, not ignored.
Any behavior change affecting results or error categories requires a future
declaration version. An implementation MAY support multiple versions with
explicit dispatch.

The command language is intentionally narrow: it is not an attempt to
implement GNU-style or other general-purpose CLI conventions. The Kaira
model does not include shell tokenization, global/inherited options,
environment expansion, response files, option defaults and groups, implicit
`--help`, short-option clustering, prefix matching, optional subcommands,
Unicode normalization, filesystem validation, or application execution.

## 9. Conformance

The file `conformance/v1.json` defines language-neutral test cases.
Conformant implementations SHALL pass the normative cases. Language-specific
test harnesses are free to choose their API, but SHALL compare portable
success values and error code/index, not human-readable messages.

## 10. Normative EBNF grammar

This grammar is the **source of truth for syntax**. Sections 1–9 specify
semantic restrictions, declaration validation, error priority, and portable
output; they SHALL NOT extend the syntax below. The value lexical
productions at the end of this grammar are also normative.

In the command-level grammar, EBNF terminals in quotes denote entire
**words**, not substrings of a character stream. Only the explicitly
marked primitive-value lexical subgrammar uses character terminals inside
one word. The token stream is a sequence of words separated by one
or more whitespace characters when written as a command line. Whitespace
is a separator, not part of a word in this abstract syntax. A host adapter
that supplies `argv` SHALL preserve its existing word boundaries; the core
parser SHALL NOT split, trim, unquote, or re-tokenize an `argv` element.
This grammar specifies no shell escaping or quoting syntax. An empty word
CAN be supplied by an adapter, but cannot be written as an unquoted word in
the whitespace notation.

The grammar is *indexed by a validated declaration*. In the productions
below, `declared-*` sets and `value-style` are determined exclusively by
that declaration; they are not lexical shortcuts or prefix matches.
Different command levels have different declared sets. A recursive child
level starts immediately after its exact subcommand word.

```ebnf
invocation           = root-level ;
root-level           = none-level | positional-level | subcommand-level ;
child-level          = none-level | positional-level | subcommand-level ;

none-level          = { option } ;
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
declared-subcommand  = ? one exact declared child name word ? ;
declared-flag-spelling = ? exact declared --long or -short flag word ? ;
declared-spaced-spelling = ? exact declared --long or -short spaced-style option word ? ;
declared-attached-spelling = ? exact declared --long or -short attached-style option prefix ? ;
value-word           = ? one word other than --, matching the declared type ? ;
positional-word      = ? bare word not beginning with -, matching the type of
                         the slot it is assigned to (section 3) ? ;
raw-positional-word  = ? any word, including -- or a dash-leading word,
                         matching the type of the slot it is assigned to ? ;
attached-value       = ? suffix of the SAME word after the FIRST =,
                         matching the declared type; possibly empty for string ? ;

(* Lexical productions apply to entire values within ONE word. In this *)
(* subgrammar only, quoted terminals denote individual characters.    *)
int-value            = "0" | [ "-" ], nonzero-digit, { decimal-digit } ;
float-value          = [ "-" ], unsigned-decimal,
                       [ ".", decimal-digit, { decimal-digit } ],
                       [ exponent ] ;
string-value         = ? any Unicode string, including empty ? ;
boolean-value        = "true" | "false" ;
unsigned-decimal     = "0" | nonzero-digit, { decimal-digit } ;
exponent             = ( "e" | "E" ), [ "+" | "-" ],
                       decimal-digit, { decimal-digit } ;
decimal-digit        = "0" | nonzero-digit ;
nonzero-digit        = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

For attached options, the `declared-attached-spelling`, `=`, and
`attached-value` productions together consume **exactly one word**.
For spaced options, the spelling and `value-word` consume **exactly two
words**. These are atomic word-pattern rules, not a license to combine
arbitrary tokens or split attached values on whitespace. Other occurrences
of `=` belong to the attached value. An attached option's value can be empty.

`value-word`, `positional-word`, `raw-positional-word`, and
`attached-value` SHALL match the entire `int-value`, `float-value`,
`string-value`, or `boolean-value` lexical production selected by their
declaration. These productions are character-level checks *within* a
single word; they do not change word boundaries or allow splitting one
word into multiple arguments. Numeric literal length is unbounded.

The subcommand branch of `subcommand-level` is syntactically optional so
that the end-of-input condition can be expressed; semantically it SHALL
occur, and its absence is `missing_subcommand` (section 7).
Positional counts, slot assignment, validation, option occurrence
restrictions, and error-code selection are semantic checks defined above. `--` is reserved
at every level and is accepted only in the `positional-level` delimiter
production; it terminates option recognition for that level. No production
admits abbreviated options, implicit short spellings, concatenated short
values, or clusters.
