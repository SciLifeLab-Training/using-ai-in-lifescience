# SciLifeLab Course Webpage Template

The SciLifeLab Course Webpage Template is a Quarto-based template for creating, publishing, and maintaining reusable training materials with GitHub Pages.

The published template is available at:

**[SciLifeLab Course Webpage Template](https://scilifelab-training.github.io/scilifelab-training-template-staging/)**

The template provides:

- a landing page for general information about a course;
- separate course instances maintained in `release-YYMM` branches;
- automated publication of the landing page and course instances through GitHub Pages.

## User Guide

New to the template? See the **[SciLifeLab Course Webpage Template User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/)**.

The User Guide provides step-by-step instructions for:

- setting up the template for a new course;
- customising the landing page;
- creating and managing course instances;
- customising course instance pages;
- previewing and publishing changes;
- preparing training materials for publication, citation, and reuse.

## Working locally

-->  For detailed setup and step-by-step editing instructions, see the [User Guide](https://scilifelab-training.github.io/scilifelab-course-webpage-template-user-guide/).

The website is built with [Quarto](https://quarto.org/).

After cloning the repository, create and activate the Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Render the site with:

```bash
quarto render
```

Or preview it locally with:

```bash
quarto preview
```

## Development and maintenance

Technical documentation for developers and maintainers of the template is available in [`docs/developer/`](docs/developer/).

This includes documentation of the landing-page architecture, validation, deployment, and migration from the legacy landing-page model.

## Citation

If you use the SciLifeLab Course Webpage Template, please cite as 

Ineke Luijten, Nina Norgren & Dimitris Panouris (2026). The SciLifeLab Course Webpage Template (v1.0.0-alpha). Zenodo. https://doi.org/XX.XXXX/zenodo.XXXXX

## Licence

Unless otherwise stated, the SciLifeLab Course Page Template is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0) licence](https://creativecommons.org/licenses/by/4.0/).

