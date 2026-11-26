# Streamlit UI evidence

Run `python -m unittest discover -s tests/ui -v`. AppTest builds each page from the real navigation entry point. It can set inputs and check drawn data and warnings. For browser-only coverage, open the local app, follow the screenshot and demonstration guides, click both CSV and Markdown downloads, open the files, then reset and repeat the source integrity check. See the test register for execution status.

To generate the screenshots and repeat the two browser download checks, start the app locally and run `python tests/ui/capture_screenshots.py` from the repository root with Playwright installed and Google Chrome at `/usr/bin/google-chrome`.
