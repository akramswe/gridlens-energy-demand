# Upload this project to GitHub

This folder is ready to become a repository. You do not have to create each file manually.

## The browser way

1. Go to https://github.com/new and create a **public** repository named `gridlens-energy-demand`. Do **not** add a README, license, or `.gitignore` from GitHub; those files are already included.
2. On the new repository page choose **uploading an existing file**. Drag the **contents of the unzipped folder**, not the `.zip` itself.
3. Commit the upload. If the browser refuses a large upload, use the terminal method below.

**Note:** The bundled Plotly JavaScript library is about 4.8 MB, so pushing with Git is often easier than dragging files.

## The terminal way (recommended)

Open a terminal inside the unzipped `gridlens-energy-demand/` directory:

```bash
git init
git add .
git commit -m "Initial GridLens energy analytics project"
git branch -M main
git remote add origin https://github.com/akramswe/gridlens-energy-demand.git
git push -u origin main
```

First create an **empty** repo at https://github.com/new using that exact name. GitHub may ask you to sign in or use a personal access token / credential manager; it does not accept your account password for HTTPS Git pushes.

## Make it look good on GitHub

Use this repository description:

> Full-stack energy analytics dashboard with 24-hour load forecasting, explainable baselines, CSV upload, and Power BI-ready exports.

Suggested topics: `python`, `fastapi`, `machine-learning`, `scikit-learn`, `energy-analytics`, `forecasting`, `plotly`, `data-visualization`, `power-bi`.

You can pin the repository to your GitHub profile. Add the link to your CV only after running the project yourself, reviewing the code, and being comfortable answering questions about it.

**GitHub Pages will not run this app** because it contains a Python API. To publish a live site, deploy the FastAPI server on a Python-compatible host (or via the included Dockerfile). The README currently gives a verified local run path; no live hosted URL is claimed.
