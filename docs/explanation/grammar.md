---
title: Command-line grammar
description: How Kaira parses a command line as a sequence of command levels, with option scopes, tail modes, value styles, and the -- delimiter.
---

# Command-line grammar

Kaira separates two concerns:

1.  A **command declaration language** (KORML) that describes the command
    tree.
2.  A **fixed `argv` interpreter** that reads command-line words using that
    declaration.

The interpreter is generic. It does not know what a particular command does;
it only knows what the declaration permits.

## Command levels

A Kaira command line is parsed as a sequence of *command levels*. The root
command is the first level; every selected subcommand opens the next.

```text
program [root-options] subcommand [child-options and positionals, interleaved]
```

Each level has zero or more declared options and **exactly one** tail mode.

| Tail mode | Meaning |
| --- | --- |
| `empty` | The command accepts no bare words at all. |
| `subcommands` | The first bare word must name a declared child command. |
| `positionals` | Bare words are positional values; options may be interleaved freely. |

A level cannot declare both subcommands and positionals. That restriction
is what makes the grammar unambiguous: a bare word is *always* either a
subcommand name or a positional value, never "whichever fits".

## Option and command scopes

Options belong to the level where they appear. Consider a program `kaira`
with a `project` subcommand that itself has a `build` subcommand:

```console
$ kaira project --name test build --release target
```

<figure class="kaira-figure" markdown>
![The command line is split into two command levels. Level one, project, owns --name test and selects build. Level two, build, owns --release and the positional target.](../assets/images/command-levels.svg)
<figcaption>The subcommand word is a hard boundary. Everything before it belongs to the parent; everything after it belongs to the child.</figcaption>
</figure>

Reading left to right:

```text
project:
  option: --name test
  tail:   subcommand build        ← scope boundary

build:
  option: --release
  tail:   positionals [target]
```

The first bare word in a `subcommands` level selects the child and
**irreversibly** opens its scope. Parent options may appear only before that
word; child options may appear only after it. There are no inherited or
"global" options in Kaira — if two levels need the same switch, each
declares it.

Within a `positionals` level, by contrast, options and positional values may
interleave. If `release` is a declared flag of `build`, this is valid:

```console
$ kaira build target --release another-target
```

The positional list is `["target", "another-target"]` and `release` is
`true`. An option that appears after a positional is still an option.

## Subcommand or positional?

The current declaration decides, and it decides the same way for every word
at that level.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Scan
    Scan --> Scan : declared option
    Scan --> Child : bare word<br/>(tail = subcommands)
    Scan --> Scan : bare word → positional<br/>(tail = positionals)
    Scan --> Raw : "--"<br/>(tail = positionals)
    Raw --> Raw : any word → positional
    Scan --> Error : bare word<br/>(tail = empty)
    Scan --> Error : unknown dash-leading word
    Child --> [*] : new level, new scope
```

- With a `subcommands` tail, `kaira project build` descends into `build`
  if `project` declares it; otherwise it is `unknown_subcommand`.
- With a `positionals` tail, `kaira build target1 target2` yields two
  positional values of `build`.
- With an `empty` tail, any bare word is `unexpected_argument`.

## Option value styles

A **flag** has no value:

```text
--verbose
```

Every value-taking option declares exactly one of two value styles.

=== "spaced"

    The value is the **next word**.

    ```text
    --option value
    ```

    The value may itself begin with a dash (`--threshold -1` is fine).
    The only word a spaced option refuses is the exact delimiter `--`,
    which produces `missing_value`.

=== "attached"

    The value follows the **first `=`** in the same word.

    ```text
    --option=value
    ```

    Everything after the first `=` is the value, including further `=`
    signs or nothing at all. `--output=--` therefore passes the literal
    value `--`.

The two styles are not aliases of each other. An option declared `spaced`
rejects the attached form, and an option declared `attached` rejects the
spaced form, in both cases with `invalid_option_form`.

## Option kinds

The declaration also decides how many times an option may occur and whether
its value is split.

| Kind | Value | Occurrences | Result shape |
| --- | --- | --- | --- |
| `flag` | none | at most once | `true` |
| `scalar` | one | at most once | one value |
| `repeatable` | one per occurrence | any number | array, in occurrence order |
| `separated` | one, split on a declared separator | at most once | array, in piece order |

## Repeatable versus separated values

Kaira offers two ways to pass several values, and a declaration picks one.

=== "Repeatable"

    Repeat the option once per value.

    ```console
    $ kaira --include src --include include --include tests target
    ```

    ```json
    {"include": ["src", "include", "tests"]}
    ```

=== "Separated"

    Pass one value and let the declared separator split it.

    ```console
    $ kaira --features "mpi;cuda;openmp" target
    ```

    ```json
    {"features": ["mpi", "cuda", "openmp"]}
    ```

    Empty pieces are preserved: with separator `;`, the value `;a;;` splits
    into `["", "a", "", ""]`.

The multiplicity style and the value style are independent choices. For a
`separated` option declared with `value_style: spaced`:

```console
$ kaira --features "mpi;cuda;openmp" target   # accepted
$ kaira --features=mpi;cuda;openmp target     # rejected: invalid_option_form
```

For the same option declared with `value_style: attached`, the two verdicts
swap. Either way, the word that reaches Kaira must contain the semicolons,
so most shells need quotes:

```console
$ kaira --features='mpi;cuda;openmp' target
```

!!! note "Quoting is the shell's job"

    Kaira never sees quotes. It sees the word
    `--features=mpi;cuda;openmp` and nothing else. The quoting shown above
    exists only to stop the shell from treating `;` as a command separator.

## The `--` delimiter

The exact word `--` ends **option recognition** at the current level. It
does not end parsing: every remaining word becomes a raw positional value of
the current command, including words that look like options, subcommands,
or further delimiters.

```console
$ kaira run -- --not-an-option build --help
```

Raw positionals of `run`:

```text
--not-an-option
build
--help
```

The delimiter may follow earlier positional values:

```console
$ kaira run input -- --not-an-option --help
```

Because `--` is only meaningful for a `positionals` tail, it is an error
(`unexpected_delimiter`) on an `empty` or `subcommands` tail. In particular,

```console
$ kaira project -- build
```

does **not** select the `build` subcommand. It is valid only if `project`
accepts positionals, in which case `build` is a positional value.

Without a delimiter, declared options are recognized anywhere in a
`positionals` level, and any undeclared dash-leading word is
`unknown_option`.

## The literal value `--`

A spaced option cannot receive `--` as its value, because the delimiter is
checked first:

```console
$ kaira --output --     # missing_value at the index of --output
```

If an option must be able to carry the literal value `--`, declare it with
`value_style: attached`:

```console
$ kaira --output=--
```

Other dash-leading values are fine for spaced options:

```text
--threshold -1
--pattern --foo
```
