# Commit Message Format (Conventional Commits v1.0.0)

Create a conventional commit message following the [Conventional Commits Specification v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification).

Structure:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Required Elements:

- Type: MUST be one of the following:
  - `feat`: Introduces a new feature (correlates with MINOR in SemVer)
  - `fix`: Patches a bug (correlates with PATCH in SemVer)
  - Other types MAY be used (e.g., `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`)

- Scope: OPTIONAL. MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., `fix(parser):`

- Description: REQUIRED. A short summary of the code changes that immediately follows the colon and space after the type/scope prefix. Use imperative mood ("add feature" not "added feature"), lowercase first letter, no period at end.

Optional Elements:

- Body: MAY be provided to give additional contextual information about the code changes. MUST begin one blank line after the description. Is free-form and MAY consist of any number of newline separated paragraphs. Explain WHY not WHAT. Wrap at 72 characters.

- Footer(s): One or more footers MAY be provided one blank line after the body. Each footer MUST consist of a word token, followed by either `:<space>` or `<space>#` separator, followed by a string value (e.g., `Reviewed-by: Z`, `Refs: #123`). A footer's token MUST use `-` in place of whitespace characters (e.g., `Acked-by`), with the exception of `BREAKING CHANGE`.

Breaking Changes:

- Breaking changes MUST be indicated either in the type/scope prefix or as an entry in the footer.
- In prefix: Indicated by a `!` immediately before the `:`, e.g., `feat!: drop support for Node 6`
- As footer: MUST consist of the uppercase text `BREAKING CHANGE`, followed by a colon, space, and description, e.g., `BREAKING CHANGE: environment variables now take precedence over config files`
- If `!` is used in the prefix, `BREAKING CHANGE:` MAY be omitted from the footer section

Case Sensitivity:

- The units of information that make up Conventional Commits MUST NOT be treated as case-sensitive by implementors, with the exception of `BREAKING CHANGE` which MUST be uppercase.
- `BREAKING-CHANGE` is synonymous with `BREAKING CHANGE` when used as a token in a footer.

## Examples

### Commit message with description and breaking change footer

```text
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

Guidelines:

- Type `feat` indicates a new feature (MINOR version bump)
- Description uses imperative mood, lowercase first letter, no period
- Breaking change indicated via footer with uppercase `BREAKING CHANGE:` token followed by colon and space
- Blank line separates description from body/footer sections

### Commit message with `!` to draw attention to breaking change

```text
feat!: send an email to the customer when a product is shipped
```

Guidelines:

- The `!` immediately before the colon indicates a breaking change (MAJOR version bump)
- When `!` is used, `BREAKING CHANGE:` footer MAY be omitted
- Commit description SHALL describe the breaking change

### Commit message with scope and `!` to draw attention to breaking change

```text
feat(api)!: send an email to the customer when a product is shipped
```

Guidelines:

- Scope `(api)` describes the section of the codebase affected
- Scope MUST consist of a noun surrounded by parenthesis
- The `!` follows the scope and precedes the colon: `<type>(<scope>)!: <description>`

### Commit message with both `!` and BREAKING CHANGE footer

```text
feat!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

Guidelines:

- Both prefix indicator (`!`) and footer can be used together
- Footer provides additional detail about the breaking change
- Blank line separates description from footer section

### Commit message with no body

```text
docs: correct spelling of CHANGELOG
```

Guidelines:

- Body is OPTIONAL - simple changes may not need it
- Type `docs` indicates documentation-only changes (no SemVer impact)
- Description alone can be sufficient for straightforward commits

### Commit message with scope

```text
feat(lang): add Polish language
```

Guidelines:

- Scope `(lang)` provides additional contextual information
- Useful in monorepos or large projects to identify affected modules
- Scope is OPTIONAL but RECOMMENDED when applicable

### Commit message with multi-paragraph body and multiple footers

```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

Guidelines:

- Body is free-form with any number of newline separated paragraphs
- Each paragraph separated by blank line
- Multiple footers MAY be provided, each on its own line
- Footer tokens use `-` in place of whitespace (e.g., `Reviewed-by`, not `Reviewed by`)
- Footer format: `<token>: <value>` or `<token> #<value>`
- Explain WHY not WHAT in the body

### Commit message with revert type

```text
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

Guidelines:

- Type `revert` indicates a commit that reverts previous changes
- Footer references the original commit SHAs being reverted
- Revert behavior is left to tooling authors - use flexibility of types and footers
