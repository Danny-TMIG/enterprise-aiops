# Grammar atlases + crossword + sudoku

## The unification

Sudoku and crossword are both constraint-satisfaction over a grid.

- **Sudoku**: 81 vars, domain {1..9}, 27 all-different constraints.
- **Crossword**: N vars (one per slot), domain = words of the slot's
  length from the grammar atlas, one constraint per intersecting
  cell pair.

The solver is the same. The configurator picks the shape.

## Grammar atlas

`Atlas` loads the linguistic taxonomy
(`Grammar/{Phonology,Morphology,Syntax,Semantics,Pragmatics,Discourse,
Theoretical grammar}`) and exposes it as a lexicon per category.
Queries:

    by_category("Phonology")     -> all phonology terms
    by_length(5)                 -> every 5-letter term in any category
    categories_for_length(5)     -> {category: [5-letter terms]}

The built-in fallback lexicon provides ~100 terms across the seven
categories. If `app/grammar/taxonomy.json` exists, it takes
precedence.

## Sudoku

`make_sudoku(givens, seed)` builds a `Grid` with 81 `Var`s and 27
`Constraint`s. `solve_sudoku` runs the shared backtracker with MRV
and forward-checking.

Three difficulty presets: `easy` (~44 givens), `medium` (~30),
`hard` (~18).

## Crossword

`make_crossword(atlas, seed)` builds a 5×5 template with six slots
(3 across on rows 0/2/4, 3 down on cols 0/2/4). Each slot's domain
is `atlas.by_length(5)`. Six intersection constraints require the
letters at shared cells to match.

## Configurator

`Config(kind, difficulty, categories, seed)` picks the puzzle.
`configure(cfg)` returns `{kind, puzzle, ...}`. `reconfig(cfg, change)`
returns a new `Config`. `Configurator` keeps a stack so `undo()`
works.

## Honest limits

- The template is fixed at 5×5. A real crossword generator would
  search the layout space.
- The sudoku generator does not produce minimal puzzles; the three
  presets are hand-picked.
- The backtracker is not as fast as DLX or Knuth's Algorithm X, but
  it is shape-agnostic: it solves both sudoku and crossword with the
  same code path.
- The atlas is small. It is a demonstration of the mechanism, not a
  dictionary.
