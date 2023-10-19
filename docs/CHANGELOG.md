# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Changed

- Default to hide the problem hints when using `euler statement`
- Move all eulertools related files to an `.euler` directory

## [0.10.0] - 2023-10-16

### Added

- Add a command to run the tests for a problem

### Changed

- Add emoji to `euler time` output

### Fixed

- Fix non-deterministic runs output, so it doesn't show a random answer

## [0.9.0] - 2023-05-19

### Added

- Allow extra test cases for a problem without breaking the cached cases
- Allow the solution to be the empty string
- Allow adding new answers with a flag in `euler run` automatically

## [0.8.0] - 2023-05-17

### Added

- Add an optional return type in statements
- Allow setting a custom path for a language

### Changed

- Create the required files if they don't exist
- Have a single source of truth for the language name

### Fixed

- Stop showing the title line if the title is missing

## [0.7.0] - 2023-05-16

### Added

- Allow showing solution hints with the `statement` subcommand

### Changed

- Use toml files to store statements

## [0.6.0] - 2023-05-15

### Changed

- Delay the failure for all types of runs, to complete running all problems

## [0.5.0] - 2023-05-15

### Changed

- Runner should return "Time &lt;response_id&gt; &lt;timing in ns&gt;" for timings
- Runner should return "Answer &lt;response_id&gt; &lt;answer&gt;" for runs

## [0.4.0] - 2023-05-12

### Removed

- Drop `benchmark` subcommand, as it can be done via `time`
- Drop `update` subcommand, as it can be done via `time`
- Drop `test` subcommand, as it can be done via `run`

## [0.3.0] - 2023-05-11

### Added

- Add more information to the output depending on the chosen verbosity

### Fixed

- Delay the failure for a test run, to complete running all problems

## [0.2.0] - 2023-05-09

### Added

- Allow formatting a problem name

## [0.1.0] - 2023-05-09

### Added

- Add a `run` subcommand, to run a problem
- Add a `test` subcommand, to test a problem
- Add a `timing` subcommand, to time a problem
- Add a `benchmark` subcommand, to benchmark a problem
- Add a `statement` subcommand to show the problem statement
- Add a `generate` subcommand to generate the solution file from a template

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[Unreleased]: https://github.com/spapanik/eulertools/compare/v0.10.0...main
[0.10.0]: https://github.com/spapanik/yamk/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/spapanik/yamk/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/spapanik/yamk/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/spapanik/yamk/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/spapanik/yamk/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/spapanik/yamk/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/spapanik/yamk/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/spapanik/yamk/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/spapanik/yamk/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/spapanik/yamk/releases/tag/v0.1.0
