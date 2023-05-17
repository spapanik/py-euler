=====
Usage
=====

``eulertools`` provides a cli command called ``euler``, which has the following subcommands:

compare: compare the timings between different languages
generate: generate a template for a new problem from the language template
run: run (and test) problems for various language implementations
statement: show the problem statement and the hint for the solution
time: run the timings for a specific problem

Project structure
-----------------
``eulertools`` can be invoked from everywhere inside the project, as it recursively looks
for the project root. The project root is marked by the existence of a `leet.toml` file.

``leet.toml``
~~~~~~~~~~~~~
`leet.toml` is a special file, that keeps the language information.

Each language is a section ``[language.<language_name>]``, with the following fields:

extension: the filename extension for the problems solved in this language
path: [optional] the path (relative to the project root) of the language solution. Defaults to ``./<language_name>``.
runner: the path (relative to the project root) of the solution runner

the runner is a cli, that has the following interface:
<runner> problem times

It should run the ``problem`` for ``times``. Each run should return exactly k pair of lines, each pair having the following format:
.. code-block:: shell

    Time <response_id> <timing in nanoseconds>

    Answer <response_id> <answer for this response>

Language directory
~~~~~~~~~~~~~~~~~~
Each language should have all the solutions inside a sub-directory of the project.
There are only two requirements for the structure of the directory.

#. there is a directory called ``.leet``, that contains a file ``solution.jinja`` that is the template for new solutions
#. the solutions live in a subdirectory ``src/solutions`` and they are named ``<problem>.<language_extension>``.
