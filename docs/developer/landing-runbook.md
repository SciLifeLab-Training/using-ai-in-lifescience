# Landing Page Maintenance Runbook

This document describes the technical architecture, local validation, deployment, and recovery procedures for the landing page on the main branch.

It is intended for developers and maintainers of the SciLifeLab Course Page Template. Instructions for course organisers using the template are provided in the user guide.

## 1. Architecture overview

The published website consists of two layers:

- the **landing page**, published at the root of the website;
- individual **course instances**, published in separate subdirectories.

The repository uses three types of branches:

| Branch | Purpose | Published location |
|---|---|---|
| `main` | Landing page source | `/` |
| `release-YYMM` | Source for an individual course instance | `/YYMM/` |
| `gh-pages` | Machine-managed published output | Entire published website |

For example:

- `main` publishes the landing page to `/`;
- `release-2605` publishes a course instance to `/2605/`;
- `release-2505` publishes a course instance to `/2505/`.

The landing page and course instances are deployed independently but share the same `gh-pages` branch.

::: {.callout-important}
Do not edit `gh-pages` directly during normal development. It contains machine-managed published output. Manual changes should only be made as part of a targeted recovery procedure.
:::

## 2. Landing page architecture

The landing page is built from three layers.

### Authored content

Static page content and structure are maintained in:

```text
index.qmd
_sections/*.qmd
```

### Data and generated content

Dynamic landing-page content is controlled by:

```text
data/instances.yml
data/ui.yml
```

The generator:

```text
scripts/generate_landing.py
```

validates these files and generates the dynamic landing-page fragments:

```text
_generated/hero-actions.qmd
_generated/instances-band.qmd
```

Do not edit files in `_generated/` manually. They are overwritten when the generator runs.

### Presentation

Landing-page styling and responsive behaviour are defined in:

```text
styles.css
```

## 3. Render flow

The landing page is generated as part of the Quarto render process.

The render sequence is:

1. `quarto render` starts.
2. Quarto runs `scripts/generate_landing.py` as a pre-render step.
3. The generator reads and validates `data/instances.yml` and `data/ui.yml`.
4. The generator writes the dynamic fragments to `_generated/`.
5. `index.qmd` includes the authored files from `_sections/`.
6. The relevant authored sections include the generated fragments.
7. Quarto renders the complete landing page.
8. The rendered site is written to `_site/`.

The relationship between the main components is therefore:

```text
data/instances.yml ──┐
                     ├──> scripts/generate_landing.py ──> _generated/*.qmd ──┐
data/ui.yml ─────────┘                                                       │
                                                                             ├──> index.qmd ──> _site/
_sections/*.qmd ─────────────────────────────────────────────────────────────┘

styles.css ──────────────────────────────────────────────────────────────────>
```

## 4. Prerequisites

Local development requires:

- Python 3.12
- Quarto 1.3.340 (matching the CI pin)

## 5. One-time local setup

From the repository root, create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

The virtual environment only needs to be created once. In subsequent terminal sessions, reactivate it with:

```bash
source .venv/bin/activate
```

## 6. Files maintained on `main`

For landing-page development, the primary files are:

| Purpose | File |
|---|---|
| Top-level page shell | `index.qmd` |
| Authored landing-page content | `_sections/*.qmd` |
| Template onboarding banner | `_sections/template-banner.qmd` |
| *All course instances* banner structure and decorative image | `_sections/instances-band.qmd` |
| Course instances, URLs, status and visibility | `data/instances.yml` |
| Dynamic UI labels | `data/ui.yml` |
| Landing-page styling | `styles.css` |
| Dynamic content generation and validation | `scripts/generate_landing.py` |
| Generated hero actions | `_generated/hero-actions.qmd` |
| Generated *All course instances* heading and instance links | `_generated/instances-band.qmd` |

`_sections/template-banner.qmd` is specific to the template repository. It links to the externally maintained [SciLifeLab Course Page Template User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/) and is intended to be removed when the template is adapted for a course.

The *All course instances* banner is split between authored and generated content. `_sections/instances-band.qmd` contains the static banner structure and decorative image, while `_generated/instances-band.qmd` contains the dynamically generated heading and course-instance links.

Files under `_generated/` are created automatically by `scripts/generate_landing.py` and should not be edited directly.

## 7. Local validation and rendering

Before pushing changes to `main`, run:

```bash
python -m pytest -q
python scripts/generate_landing.py
quarto render
```

Expected outputs include:

```text
_generated/
_site/
```

The `_generated/` directory contains generated Quarto fragments.

The `_site/` directory contains the rendered website.

To inspect the site locally, run:

```bash
quarto preview
```

## 8. Landing data validation

The generator validates landing-page configuration before generating the dynamic fragments.

### `data/instances.yml`

The following high-impact rules are enforced:

- Exactly one instance must have `status: current`.
- The current instance must have `visible: true`.
- Each `slug` must be unique.
- A `slug` must contain four digits.
- `0000` is allowed as the template placeholder.
- Other slugs must represent a valid `YYMM` value.
- A relative `instance_url` must correspond to its slug:

```yaml
slug: "2605"
instance_url: "./2605/"
```

- `registration_url` may be empty, relative, or use `http(s)`.
- Protocol-relative URLs such as `//example.org` are not allowed.
- `sort_key` must be an integer and not a boolean.

An invalid configuration stops generation and therefore prevents the landing page from rendering.

### `data/ui.yml`

Only documented keys are accepted.

Currently supported keys are:

```yaml
hero_view_current_label:
hero_registration_open_label:
instances_band_title:
```

Provided values must be non-empty strings.

## 9. Relationship between instances and the landing page

Course-instance branches are not automatically discovered by the landing page.

Creating and pushing:

```text
release-2605
```

publishes that course instance, but does **not** automatically add it to the landing page.

The corresponding instance must also be configured in:

```text
data/instances.yml
```

on `main`.

For example:

```yaml
- slug: "2605"
  label: "May 2026"
  status: current
  visible: true
  show_in_hero: true
  instance_url: "./2605/"
  registration_url: ""
  sort_key: 202605
```

The `visible` setting controls whether an instance is displayed in the *All course instances* banner.

For the current instance, `show_in_hero` controls whether its link is also displayed as an action button in the hero.

## 10. GitHub Actions

Landing-page validation and deployment are handled by GitHub Actions.

### Landing validation

```text
.github/workflows/validate-landing.yml
```

This workflow:

- runs on pull requests to `main`;
- runs the landing tests;
- renders the landing page;
- checks that raw YAML configuration does not leak into `_site`.

### Landing deployment

```text
.github/workflows/deploy-landing.yml
```

This workflow:

- runs on pushes to `main`;
- renders the landing page;
- publishes only landing-owned files and directories to `gh-pages`.

### Course-instance deployment

```text
.github/workflows/main.yml
```

On `release-*` branches, this workflow publishes the corresponding course instance to its own directory on `gh-pages`.

For example:

```text
release-2605 → gh-pages/2605/
```

Updating a course instance therefore does not require republishing or replacing the landing page.

## 11. Deployment safety contract

The landing page and course instances share the same `gh-pages` branch. Deployment must therefore avoid deleting output owned by another branch.

The landing deployment must:

- copy only landing-owned root files, including `index.html` and `styles.css`;
- mirror only landing-owned directories such as `site_libs/`, `index_files/`, and `img/`, using per-directory deletion where required;
- never perform a root-level destructive sync such as:

```bash
rsync -a --delete _site/ gh-pages/
```

- preserve `.nojekyll` on `gh-pages`;
- prevent raw configuration files from being published;
- remove leaked configuration such as `gh-pages/data` or root YAML files;
- use the shared `deploy-gh-pages` concurrency control for landing and instance deployments.

These constraints prevent a landing-page deployment from deleting published course-instance directories.

## 12. Important maintenance rules

When modifying the landing architecture:

1. Treat `gh-pages` as machine-managed output.
2. Do not edit `_generated/*` manually.
3. Keep raw YAML configuration out of the published site.
4. Preserve `.nojekyll` on `gh-pages`.
5. Do not introduce a root-level destructive deployment sync.
6. Keep landing and course-instance deployments isolated.
7. Update `data/instances.yml` on `main` when instance visibility, status, or links change.
8. Keep validation rules and the user-facing configuration model aligned.

## 13. Deployment recovery

If a deployment assertion fails:

1. Identify and fix the workflow or configuration problem on `main`.
2. Re-run the failed validation or deployment.
3. If an incorrect artifact has already been written to `gh-pages`, remove only the affected artifact using a targeted cleanup commit.
4. Re-run the deployment from `main` to restore the expected landing-page output.

Do not add a permanent assertion bypass to a workflow in order to make a failed deployment pass.

If course-instance content has been affected, verify that the corresponding `gh-pages/YYMM/` directory remains intact before performing additional deployment operations.

## 14. Related documentation

### User documentation

The [User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/) contains instructions for course organisers, including:

- setting up and previewing the template;
- customising the landing page;
- creating and managing course instances;
- customising course instance pages;
- preparing course materials for publication and reuse.

### Developer documentation

See also:

- [`landing-migration-map.md`](landing-migration-map.md) — maps the legacy `data/landing.yml` model to the current Quarto-first architecture.