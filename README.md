# Searchlight SEO Checker

Searchlight is a small interactive on-page SEO checker. The HTML, CSS, and JavaScript frontend is served as static files; the Python analysis endpoint runs as a Vercel Function.

## Deploy on Vercel

1. Upload the contents of this folder to the root of your GitHub repository (not the enclosing folder).
2. Import that repository in Vercel.
3. Use these project settings:
   - Framework Preset: **Other**
   - Root Directory: **./**
   - Build Command: leave blank / default
   - Output Directory: leave blank / default
   - Install Command: leave blank / default
   - Environment Variables: none required
4. Deploy. Vercel maps `api/analyze.py` to `/api/analyze`; root `index.html` and `static/` assets are served as static files.

This project uses only the Python standard library, so no `requirements.txt` is needed. The `.python-version` file selects Python 3.12.

## Run locally

Requires Python 3.12 or a compatible Python 3 version. From this folder run:

```bash
python app.py
```

Then open http://127.0.0.1:8000.

## What the checker does

The checker evaluates the page details entered by the visitor. It does not fetch or crawl the supplied URL. Text entered in the form is sent to the Searchlight `/api/analyze` endpoint for processing; it is not sent to a search engine.
