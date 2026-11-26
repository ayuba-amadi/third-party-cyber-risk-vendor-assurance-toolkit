# Deployment readiness

**READY FOR DEPLOYMENT**

This recommendation covers the fictional demonstration working tree. A future GitHub-backed deployment must target its reviewed release commit. The current branch tip is the Phase 1 base and cannot serve the tested GUI on its own.

| Check | Result |
|---|---|
| Branch and base commit | `main`, `00eb6ee6d27dd4fad720cdc45f440328424f7a76` |
| Application entry point | `app/streamlit_app.py` |
| Runtime verified | Python 3.12.3, Streamlit 1.67.0, Ubuntu 24.04.5 LTS |
| Required dependencies | Streamlit and its transitive packages from `app/requirements.txt`; root `requirements.txt` includes it |
| Start command | `streamlit run app/streamlit_app.py --server.headless true --server.port 8501` |
| Health check | `curl -fsS http://localhost:8501/_stcore/health` returned `ok`; local process stopped |
| Fictional data | Ten synthetic vendors. Evidence metadata and fake reference paths only. |
| Secrets scan | PASS. Reviewed keyword candidates and credential-shaped hits. No real credentials found. |
| Source-data protection | PASS. Hashes matched after the app and controlled CLI runs. App saves operate in memory. |
| Tests | 100 automated tests passed under each runner. All 10 demonstrations passed. Browser CSV and Markdown downloads opened. |
| Configuration | Root Streamlit config enables headless mode and disables usage statistics. |
| Rollback | Deploy a reviewed branch from the last verified Git commit or revert the faulty release on its deployment branch. Repeat health and smoke checks. |
| Live deployment | NOT ATTEMPTED |

Deployment preparation completed; live deployment not executed.

The hosted demo is public-facing fictional software with session storage and user-entered roles. Hosted runtime and rollback remain untested. See [deployment guide](../../docs/deployment_guide.md) and [limitations](limitations.md).
