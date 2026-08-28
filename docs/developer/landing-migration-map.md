# Landing Migration Map

This document records how the legacy `data/landing.yml` configuration maps to the current Quarto-first landing-page architecture.

It is retained as a reference for developers maintaining or migrating the template. For the current landing-page architecture, validation, and deployment model, see the [Landing Page Maintenance Runbook](landing-runbook.md).

## Legacy to new ownership

| Legacy field | Current source of truth | Notes |
|---|---|---|
| `course.title` | `_sections/hero.qmd` (`.hero__title`) | Static authored copy. |
| `course.subtitle` | `_sections/hero.qmd` (`.hero__subtitle`) | Static authored copy. |
| `course.logo` | `_sections/hero.qmd` (`.hero__brand`) | Static authored asset reference. |
| `hero_actions[0].label` | `data/ui.yml` (`hero_view_current_label`) | Label for the current course instance button. |
| `hero_actions[0].href` | `data/instances.yml` current `instance_url` | Derived dynamically from the current instance; button is displayed when `show_in_hero: true`. |
| `hero_actions[0].style` | `scripts/generate_landing.py` template class (`hero-cta--primary`) | Presentation class is fixed in generator output. |
| `hero_actions[1].label` | `data/ui.yml` (`hero_registration_open_label`) | Label for the registration button. |
| `hero_actions[1].href` | `data/instances.yml` current `registration_url` | Derived dynamically from the current instance; button is omitted when `registration_url` is empty. |
| `hero_actions[1].style` | `scripts/generate_landing.py` template class (`hero-cta--secondary`) | Presentation class is fixed in generator output. |
| `instances.title` | `data/ui.yml` (`instances_band_title`) | Controls the heading in the *All course instances* banner. |
| `cards[*]` content | `_sections/top-cards.qmd` | Course content, learning outcomes, topics covered, and keywords are now authored directly in the card structure. |
| `founders[*]` | `_sections/bottom-cards.qmd` | Course founders are now authored directly in the card structure. |
| `contributors[*]` | `_sections/bottom-cards.qmd` | Course contributors are now authored directly in the card structure. |
| `footer.license` | `_sections/footer.qmd` (`.landing-footer__meta`) | Licence text and URL are authored directly in the footer. |
| `footer.built_with` | `_sections/footer.qmd` (`.landing-footer__meta`) | Hosting and build information is authored directly in the footer. |
| `footer.github_url` | `_sections/footer.qmd` (`.landing-footer__actions`) | Repository URL is set directly in the GitHub image link (`href`). |

## New architecture elements

The current landing-page model includes elements and configuration options that did not have equivalent explicit keys in the legacy `data/landing.yml`.

### `_sections/template-banner.qmd`

The template repository includes an onboarding banner that links to the externally maintained SciLifeLab Course Page Template User Guide.

This banner is specific to the template and is intended to be removed when the template is adapted for an individual course.

### `data/ui.yml`

- `instances_band_title` — controls the title displayed in the *All course instances* banner.

### `data/instances.yml`

- `show_in_hero` — controls whether the current course instance is displayed as an action button in the hero.
- `registration_url` — controls the registration link. If the value is empty, the registration button is not generated.

### `_sections/instances-band.qmd`

The *All course instances* banner is divided between authored and generated content.

- `_sections/instances-band.qmd` contains the static banner structure and decorative image.
- `_generated/instances-band.qmd` contains the dynamically generated heading and course-instance links.

The generated content is created by `scripts/generate_landing.py` from `data/ui.yml` and `data/instances.yml`.

## Removed legacy file

`data/landing.yml` has been intentionally removed from the current architecture.

Its responsibilities are now divided between:

- `_sections/*.qmd` for authored landing-page content;
- `data/instances.yml` for course-instance configuration;
- `data/ui.yml` for configurable interface labels;
- `scripts/generate_landing.py` for validation and dynamic generation;
- `_generated/*.qmd` for generated landing-page fragments.

Files in `_generated/` are generated automatically and should not be edited manually.