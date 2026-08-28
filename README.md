# Release Branch Course Template

This branch is the starter template for one course instance.

Use it to create branches like:

- `release-0000`
- `release-2505`
- `release-2511`

Each `release-YYMM` branch publishes one course instance to `gh-pages/YYMM/`.

## What This Branch Is For

- course pages and navigation
- course-specific Quarto configuration
- styles and assets for one course run

This branch does **not** control the landing page at the root of the site. The landing page lives on `main`.

## Simple Workflow

1. Create a new branch from `release-0000`.
2. Name it `release-YYMM`, for example `release-2505`.
3. Update the course content in that new branch.
4. Push the branch.
5. GitHub Actions renders the course and publishes it to `gh-pages/YYMM/`.

The output directory is derived from the branch name by the release workflow. You do not need to maintain a separate branch-mapping list in `_quarto.yml`.

## What To Edit

For normal course work, edit:

- the course `.qmd` pages
- `_quarto.yml` for course-site settings like title, sidebar, navbar, and theme
- images and other course assets

## Local Preview

If you have Quarto installed, you can render locally:

```bash
quarto render
```

Rendered output is written to `_site/`.

## GitHub Actions

This branch uses `.github/workflows/main.yml`.

On push to a `release-*` branch, the workflow:

1. reads the branch name
2. validates that it matches `release-YYMM`
3. renders the course site
4. publishes the result to the matching directory on `gh-pages`

Examples:

- `release-0000` -> `gh-pages/0000/`
- `release-2505` -> `gh-pages/2505/`

## Notes

- `gh-pages` is deployment output only
- `.nojekyll` is kept by the workflow
- the landing page branch (`main`) separately controls which instances appear on the landing page
