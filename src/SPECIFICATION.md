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

The root KORML mapping has exactly `version`, `program`, and `command`.
`version` is exactly `kaira.command-declaration/v1`. The `program` field
labels the result; it is not matched against an executable filename.

Identifiers match the entire ASCII pattern `[A-Za-z][A-Za-z0-9_-]*`.
Mapping keys under `options` are long option names without dashes; under
`commands` they are bare subcommand names. `short` aliases contain exactly
one ASCII letter or digit, matching `[A-Za-z0-9]`. All matching is
case-sensitive. Short aliases SHALL be unique within a command level but
MAY be reused at a different level.

Every command has exactly one `tail` variant: `empty`, `subcommands`,
or `positionals`. Optional fields are `help` (a string with no parsing
effect) and `options` (a mapping, defaulting to empty). Every option has
exactly one variant: `flag`, `scalar`, `repeatable`, or `separated`.
Unknown fields are invalid everywhere, including variant payloads.

Additional semantic constraints:

1. `subcommands.commands` SHALL contain at least one child. Optional
   `required` is a boolean and defaults to `false`.
2. A positional tail declares one named list. Its `min` defaults to zero
   and `max` defaults to `unbounded`; finite bounds are nonnegative
   integers, with `max >= min`.
3. Every value-taking option has a `value` type (`int`, `float`, `string`,
   or `boolean`) and `value_style`, exactly `spaced` or `attached`. Flags
   have neither. The same four value types apply to positionals.
4. Separated options additionally require a nonempty string `separator`.
5. `allow_explicit_empty` from preliminary drafts is not part of v1.

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
| Spaced value | `--output file`, `-o file` | `--output=file`, `-o=file` |
| Attached value | `--output=file`, `-o=file` | `--output file`, `-o file` |

A spaced option consumes the immediately following token, **even if it
resembles an option**, except that the exact token `--` is reserved and
causes `missing_value`. An attached option consumes everything after the
first `=`, including an empty string or additional equals signs.
Thus `--output=--` passes the literal value `--`.

The following is an **informative sketch** of the declaration-parameterized
grammar; the complete normative EBNF appears at the end of this document:

```text
empty level:        option*
subcommands level:  option* [subcommand child-level]
positionals level:  (option | positional)* [-- positional*]
```

The square-bracketed subcommand is optional only if `required: false`.
The delimiter `--` is an exact word, not a declared option. After it,
every remaining token is positional data. Options and positional arguments
MAY interleave freely in a positional level:

```text
app target1 --verbose target2 --include dir target3
```

For each command level, initialize a fresh options map and scan tokens
left to right:

1. If an exact `--` token occurs, accept it only for a `positionals`
   tail. Consume it, disable option recognition, and interpret all following
   tokens as positional values. Otherwise report `unexpected_delimiter`.
2. If a token begins with `-`, require a declared long or short option
   spelling. Check its form and occurrence limit, consume its value where
   applicable, and validate it. A forbidden attached/spaced form is
   `invalid_option_form`; an undeclared dash-leading token is
   `unknown_option`. All option recognition at this level uses only the
   level's own declarations.
3. For a bare token, act according to the tail:
   - `empty`: report `unexpected_argument`.
   - `subcommands`: require an exact child name, consume it, then
     **immediately** descend into that child's command level. No parent
     options are recognized beyond that boundary.
   - `positionals`: append the token as a positional value and continue
     scanning this level; subsequent options remain recognizable.
4. For each positional value, enforce the finite `max` bound first and
   then validate the value type. At end of input, enforce `min`; for a
   subcommands tail, enforce `required`.

After `--`, step 2 is disabled and every token follows step 4, even if it
looks like an option or another delimiter. A dash-leading positional
therefore requires a preceding `--`, which may appear **after earlier
positional arguments**. Parent and child option scopes never overlap.
A level cannot both select subcommands and accept positional values.

## 4. Occurrences, splitting, and counts

`flag`, `scalar`, and `separated` MAY occur at most once per level,
across long and short spellings combined. Duplicate use is
`duplicate_option`. A `repeatable` option may occur any number of times.
No option is implicitly required; absent options have no default value.

`separated` consumes one value and splits it from left to right at each
literal, nonoverlapping occurrence of its separator. Empty pieces are
preserved: with `;`, `";a;;"` yields `["", "a", "", ""]`, and
`""` yields `[""]`. Each piece undergoes value validation in order.
The separated option itself cannot recur.

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
A `string` value is preserved unchanged. A flag is not a value-taking
option: its presence yields Boolean `true` and its absence is represented
by omission, not by `false`.

Types such as filesystem paths, assignments, dates, commands, or enums
belong to layers **above** this core. Such a layer CAN declare a `string`
value and impose additional validation or interpretation after successful
Kaira parsing. Kaira v1 itself SHALL NOT silently apply those checks or
accept extra primitive type names. The KORML schema's own `integer` and
`boolean` scalars used for *declaration metadata* (such as `min`, `max`,
or `required`) are separate from Kaira's `value` type names.

## 6. Portable successful result

The result is a JSON-compatible object with exactly these three fields:

```json
{
  "program": "example",
  "command_path": ["build"],
  "levels": [
    {"options": {"verbose": true}, "positionals": null},
    {"options": {"output": "a.log", "include": ["src", "inc"]},
     "positionals": {"target": ["app"]}}
  ]
}
```

- `program` is copied from the declaration.
- `command_path` lists child names traversed after the root.
- `levels` has one entry for root plus one per selected child, in order.
- Each level has exactly `options` and `positionals`.
- `options` maps canonical **long names** of present options to values.
  Unseen options are omitted. Flags yield Boolean `true`. A present
  `boolean` scalar yields Boolean `true` or `false`; a `string`, `int`,
  or `float` scalar yields a string. Repeatable and separated options yield
  arrays of the corresponding value representations.
- `positionals` is `null` for empty and subcommands tails. For a
  positionals tail it maps the declared name to an array of the
  corresponding value representations, including an empty array if no
  values were supplied.

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
| `invalid_option_form` | Declared option token with invalid value style. |
| `missing_value` | Spaced option token without usable next token. |
| `duplicate_option` | Second nonrepeatable option token. |
| `invalid_value` | Value token, or attached-option token. |
| `unexpected_argument` | First bare token on an empty tail. |
| `unknown_subcommand` | Unknown bare subcommand token. |
| `missing_subcommand` | End index for required subcommand. |
| `unexpected_delimiter` | `--` token on non-positional tail. |
| `too_few_positionals` | End index. |
| `too_many_positionals` | Index of first extra positional token. |

When several errors are present, report the first encountered by the
left-to-right procedure in section 3. Positional `max` is checked as each
positional is consumed; `min` is checked only at end of input.
Duplicate option detection precedes validation of that option's second
value. Diagnostic messages are not portable.

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
`--help`, short-option clustering, prefix matching, Unicode
normalization, filesystem validation, or application execution.

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
root-level           = empty-level | positional-level | subcommand-level ;
child-level          = empty-level | positional-level | subcommand-level ;

empty-level          = { option } ;
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
declared-spaced-spelling = ? exact declared --long or -short spaced option word ? ;
declared-attached-spelling = ? exact declared --long or -short attached option prefix ? ;
value-word           = ? one word other than --, matching the declared type ? ;
positional-word      = ? bare word not beginning with -, matching the declared type ? ;
raw-positional-word  = ? any word, including -- or a dash-leading word,
                         matching the declared positional type ? ;
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

The optional subcommand branch is permitted to be absent only when the
declaration says `required: false`; otherwise the branch SHALL occur.
Positional counts, validation, option occurrence restrictions, and
error-code selection are semantic checks defined above. `--` is reserved
at every level and is accepted only in the `positional-level` delimiter
production; it terminates option recognition for that level. No production
admits abbreviated options, implicit short spellings, concatenated short
values, or clusters.
