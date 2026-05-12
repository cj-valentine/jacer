# Contributing to Jacer

Thanks for thinking about contributing. Jacer is a single-author OSS project for now — response times are governed by life and a day job, but every contribution gets read.

## Status of the project

Jacer is mid-rewrite (v2). Until `v0.1.0` ships, the public API and data shapes are unstable. **Open an issue before doing substantial work** so we can align — I'd hate to reject a PR because it conflicts with a decision that hadn't been documented yet.

For small fixes (typos, broken links, obvious bugs), just send the PR.

## Quick steps

1. Open an issue describing the problem you're solving or the feature you'd like.
2. Wait for a "yes, please" before writing code on anything non-trivial.
3. Fork, branch (`feature/short-description` or `fix/short-description`), commit, push, open a PR.
4. CI must be green for review.

## Standards

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org). `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- **Backend:** Python 3.12, `ruff format` + `ruff check`, pytest passing.
- **Frontend:** TypeScript, ESLint clean, Vitest passing.
- **PRs:** small, focused, one concern per PR. A 50-line PR will be reviewed faster than a 500-line PR.
- **English:** Australian spelling in user-facing strings and docs (organise, colour, behaviour). British English in code comments is fine. American spelling is not the end of the world but will probably be tidied during review.

## Scope discipline

Jacer is deliberately narrow. Before proposing a feature, check it against [Marvin UX Moves We Borrowed](https://github.com/cjvalentine/jacer/wiki/marvin-ux-moves) (linked once the wiki is up) — features that match the routine-template or day-planning loops are in scope. Features outside that (habits, gamification, calendar sync, plugins, multi-user) are likely answered with "thank you, please open a discussion."

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind, assume good faith, leave the discussion in better shape than you found it.
