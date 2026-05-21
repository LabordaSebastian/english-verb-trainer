---
name: documentation
description: Conventions and patterns for maintaining the project's MkDocs documentation site
---

## When to use

Use this skill whenever you are asked to update, extend, or create documentation files in the `docs/` directory. Apply these patterns to keep documentation consistent with the existing site.

## Site overview

The documentation uses **MkDocs** with the **Material for MkDocs** theme, deployed to GitHub Pages via `.github/workflows/docs.yml`.

- **Config**: `mkdocs.yml` at project root
- **Source**: `docs/` directory
- **Build**: `mkdocs build`
- **Serve locally**: `make docs-serve` (or `mkdocs serve`, defaults to port 8001)

### MkDocs config (`mkdocs.yml`)

Key settings to respect:

```yaml
theme:
  name: material
  features:
    - navigation.sections
    - navigation.expand
    - content.code.copy
    - content.tabs.link

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed

plugins:
  - search: { lang: es }
  - awesome-pages
```

The `nav` section defines the sidebar structure. When adding a new page, register it in `nav` using the relative path from `docs/`:

```yaml
nav:
  - New Section:
      - Page Title: path/to/page.md
```

## File conventions

### Location

| Content | Location |
|---------|----------|
| Home | `docs/index.md` |
| Quick start | `docs/quick-start.md` |
| Project structure | `docs/structure.md` |
| CLI reference | `docs/cli-reference.md` |
| Architecture docs | `docs/architecture/*.md` |
| API docs | `docs/api/*.md` |
| Database docs | `docs/database/*.md` |
| Development guides | `docs/development/*.md` |

### File naming

- Lowercase, hyphen-separated: `quick-start.md`, `data-flow.md`
- Subdirectory per section: `docs/api/endpoints.md`
- `index.md` for section homepages (e.g., `docs/architecture/index.md`)

### Frontmatter and title

Each page starts with an H1 title matching the nav entry:

```markdown
# Page Title

Brief one-line description of what this page covers.
```

No YAML frontmatter is used (Material theme infers from nav).

## Writing style

### Headings

- `#` — Page title only (one per file)
- `##` — Major sections
- `###` — Sub-sections
- `####` — Details within a sub-section
- Headings use sentence case: "Running the tests", not "Running The Tests"
- Leave one blank line before and after each heading

### Content patterns

**Prose** — Concise, direct, imperative. Avoid marketing language.

**Code blocks** — Always specify language:

```markdown
\```bash
command --flag value
\```

\```python
def hello():
    print("world")
\```

\```json
{"key": "value"}
\```
```

**Tables** — Use GFM tables with aligned columns:

```markdown
| Command | Description |
|---------|-------------|
| `make up` | Start containers |
| `make test` | Run tests |
```

**Lists** — Use `-` for unordered, `1.` for ordered. Blank line before and after.

**Admonitions** (Material callout boxes):

```markdown
!!! note "Optional Title"
    Content text indented by 4 spaces.

!!! tip
    A helpful tip.

!!! warning
    Something to watch out for.

!!! danger
    Critical information.
```

**Collapsible details**:

```markdown
??? example "Click to expand"
    Hidden content indented by 4 spaces.
```

**Content tabs** (for multi-language examples):

```markdown
=== "cURL"
    \```bash
    curl http://localhost:8000/api/stats
    \```

=== "Python"
    \```python
    import requests
    response = requests.get("http://localhost:8000/api/stats")
    \```
```

### Common section structure

For API endpoint docs:

```markdown
### METHOD /path

Brief description.

#### Request

\```bash
METHOD /path?param=value
\```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|

#### Response (200 OK)

\```json
{...}
\```

#### Response Schema

\```python
class ModelName(BaseModel):
    field: type
\```

#### Errors

| Status | Reason |
|--------|--------|

#### Example

=== "cURL"
    ...

=== "Python"
    ...

#### Notes

- Edge cases
- Side effects
- Related endpoints
```

For setup/development guides:

```markdown
# Title

Brief intro.

## Prerequisites

- Requirement 1
- Requirement 2

## Step 1 — Do Thing

\```bash
command
\```

Explanation of what this does.

## Step 2 — Next Step

...
```

## Cross-references

Use relative links within `docs/`:

```markdown
[Quick Start](quick-start.md)
[Architecture Overview](architecture/overview.md)
[API Endpoints](api/endpoints.md)
[REST API Reference](../api/endpoints.md)  <!-- from a subdirectory -->
```

Do NOT use absolute URLs for internal pages.

## Diagrams

Use **Mermaid** code blocks (rendered natively by Material):

```markdown
\```mermaid
graph LR
    A[FastAPI] --> B[SQLAlchemy]
    B --> C[PostgreSQL]
\```
```

ASCII art diagrams are also acceptable for architecture and data flow.

## Generated documentation

Some docs are maintained manually, NOT auto-generated:

- `docs/api/endpoints.md` — manually written with cURL/Python/JS examples
- `docs/api/schemas.md` — manually written descriptions of Pydantic models
- `docs/cli-reference.md` — manually written command reference

When updating endpoints or schemas, update the corresponding documentation file in the same PR.

## When adding new features

When a new feature adds:

1. **New models** → Update `docs/database/models.md` and `docs/database/relationships.md`
2. **New API endpoints** → Update `docs/api/endpoints.md` and `docs/api/schemas.md`
3. **New CLI commands** → Update `docs/cli-reference.md`
4. **New architecture component** → Update `docs/architecture/*.md`
5. **New environment variable** → Update `docs/development/setup.md` and `.env.example`
6. **New dependency** → Update the relevant `requirements-*.txt` file
7. **New Docker configuration** → Update `docs/quick-start.md` and `docs/structure.md`

Always add the new page to `mkdocs.yml` `nav:` section.

## Common pitfalls

- **Broken links**: Use relative paths. Verify links by building (`mkdocs build`) or serving (`mkdocs serve`). Links to files not in `docs/` are invalid.
- **Missing nav entry**: Adding a `.md` file without registering it in `mkdocs.yml` `nav:` means it won't appear in the sidebar. If using `awesome-pages` plugin, a `.pages` file may be needed.
- **Inconsistent examples**: When updating an endpoint, update ALL language examples (cURL, Python, JavaScript) — don't leave stale examples.
- **Forgetting code tabs**: Use `=== "cURL"` tab syntax for multi-language API examples, not separate code blocks.
- **Over-nesting**: Keep heading depth to `##` and `###` max for readability.
- **Line length**: Wrap prose at 88 characters to match code style.
