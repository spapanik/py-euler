# Commands

As a rule of thumb any command that expects a language, defaults to all
languages defined in the `euler.toml` file. Similarly, all commands that
expect a problem default to all problems in `.euler/statements/` directory.

The main command can be run with any of the following subcommands, or with the
flag `-V/--version` that prints the version and exits.

For all subcommands you can pass `-h/--help` to show a help text, and `-v/--verbose`
to increase the verbosity. The later can be passed multiple times to further increase
the verbosity level.

## Compare

`euler compare` compares the timings between different languages. It uses the cached
timings, that are produced from `euler time`.

Optional arguments:

-   -l/--languages [LANGUAGE ...]
-   -p/--problems [PROBLEM ...]

```console title="compare"
user@localhost $ euler compare -p 3 107 -l nim python
┌─────────┬─────────┬─────────┬─────────┐
│ problem │    id   │   nim   │  python │
├─────────┼─────────┼─────────┼─────────┤
│        3│        1│   10.1µs│  249.5µs│
│        3│        2│     85ns│    1.5µs│
│        3│        3│    171ns│    2.7µs│
│        3│        4│  106.7µs│    2.7ms│
├─────────┼─────────┼─────────┼─────────┤
│      107│        1│      N/A│  832.5µs│
└─────────┴─────────┴─────────┴─────────┘
```

## Generate

`euler generate` will create a new skeleton for a solution for a new problem
from the language template. As it can create a very large number of files, it
is strongly advised to always run with a specific language and problem.

Optional arguments:

-   -l/--languages [LANGUAGE ...]
-   -p/--problems [PROBLEM ...]

## Run

`euler run` runs problems for various language implementations

Optional arguments:

-   -l/--languages [LANGUAGE ...]
-   -p/--problems [PROBLEM ...]
-   -u/--update

```console title="run"
user@localhost $ euler run -l rust java -p 1 2
🟢 Running java // 1 // 1... 233168
🟢 Running java // 1 // 2... 23331668
🟢 Running java // 1 // 3... 23
🟢 Running java // 1 // 4... 52492500
🟢 Running java // 2 // 1... 4613732
🟢 Running java // 2 // 2... 19544084
🟢 Running java // 2 // 3... 350704366
🟢 Running rust // 1 // 1... 233168
🟢 Running rust // 1 // 2... 23331668
🟢 Running rust // 1 // 3... 23
🟢 Running rust // 1 // 4... 52492500
🟢 Running rust // 2 // 1... 4613732
🟢 Running rust // 2 // 2... 19544084
🔴 Running rust // 2 // 3... expected: 350704366, got: 44
🟠 Running rust // 2 // 4... new response: 1089154
RuntimeError: Some tests failed
```

The emojis in front of each line have the following meaning:

-   🟢 The answer for this problem and response_key matches the saved one
-   🟠 This is a new problem/response_key combination
-   🔴 The run didn't produce the same answer as the saved one

Passing the `-u/--update` flag, will update the saved answers with the ones
from this run.

## Test

`euler test` tests the solutions for the problems for various language implementations,
running each problem multiple times. This is done to ensure that the solution always
produces the same answer.

Optional arguments:

-   -l/--languages [LANGUAGE ...]
-   -p/--problems [PROBLEM ...]
-   -t/--times TIMES (defaults to 2)

This will run the problem for \<TIMES\> times and it will check if all of them match
the saved ones.

```console title="test"
user@localhost $ euler test -p 1 -l java
🟢 Running java // 1 // 1... 233168
🔴 Running java // 1 // 2... Not deterministic answer.
🟢 Running java // 1 // 3... 23
🟢 Running java // 1 // 4... 52492500
RuntimeError: Some tests failed
```

The emojis have the same meaning as in run, but now, as it runs every problem twice,
the red emoji also indicates that not all runs produced the same answer.

## Statement

`euler statement` shows the problem statement and (optionally) the hint for the solution.

Optional arguments:

-   -l/--languages [LANGUAGE ...]
-   -p/--problems [PROBLEM ...]
-   -s/--show-hints

```console title="statement"
user@localhost $ euler-dev statement -p 1 -s
Two Sum
~~~~~~~
Given an array of integers, return indices of the two numbers such that they
add up to a specific target.
You may assume that each input would have exactly one solution, and you may not
use the same element twice.

Hint
~~~~
For better than O(n^2) complexity, keep a dictionary of the complements.
```

## Time

`euler time` times

Optional arguments:

-   -l/--languages [LANGUAGE ...]
-   -p/--problems [PROBLEM ...]
-   -t/--times TIMES (defaults to 10)
-   -u/--update

```console title="time"
user@localhost $ euler time -l python -t 3 -u -p 74 -vvvv
Time 1 1097407458
Answer 1 402
Time 1 1093154930
Answer 1 402
Time 1 1112696508
Answer 1 402

Timing python // 74 // 1...
~~~~~~~~~~~~~~~~~~~~~~~~~~~
🟤 Old timing: 1.11s
🟢 New timing: 1.10s
    ⏱  New timings:
       ⬇  Run 1 took: 1.10s
       ⬇  Run 2 took: 1.09s
       ⬆  Run 3 took: 1.11s
🟢 Performance difference: 0.94%
```

The `-u/--update` flag updates the cached timings, and the emojis in front of each line
have the following meaning:

-   🟤 This is the old timing
-   🟢 This set of runs is overall better than the cached one
-   🔵 This set of runs is the same as the cached one (or there isn't a cached one)
-   🔴 This set of runs is overall worse than the cached one
-   ⬇ This specific run is better than the cached one
-   ⬆ This specific run is worse than the cached one

The `-a/--append` flag only append new timings to the cached timings, and the emojis in front of each line
have the same meaning as with the `-u/--update` flag.
