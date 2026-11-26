# Deployment guide

Deployment preparation completed; live deployment not executed.

## Local installation and verification

Use Python 3.12 from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py --server.headless true --server.port 8501
```

In a second shell, run `curl -fsS http://localhost:8501/_stcore/health`. Expect HTTP 200 and `ok`. Open the app and check Dashboard, Data Quality and Reports against 18 November 2026. Stop the local process with Ctrl+C.

## Future hosted deployment

After explicit authorisation, connect your GitHub account to Streamlit Community Cloud. Select the repository, the reviewed branch and `app/streamlit_app.py` as the entry point. Select Python 3.12 if the host offers it. The app-level requirements file declares Streamlit. The root requirements file uses the same declaration for local installs. Keep `.streamlit/config.toml` at the root. It disables usage telemetry and enables headless mode. The application needs no secrets.

Deploy only the fictional demonstration fixture and fictional evidence references. Anyone with access to the public app can exercise the demonstration workflows. Role names are user inputs and provide no authentication or access enforcement. The demo keeps records in a session, and the source CSV remains the bundled baseline.

Once authorised and deployed, check the hosted app's `/_stcore/health` endpoint where exposed and verify the Dashboard, Data Quality and report export in a browser. Check build and application logs if the app fails to start. Record a live URL only after verifying it.

To remove public access, use the hosting dashboard's restricted visibility option where available or delete the hosted app. To roll back, create a deployment branch at the last verified Git commit, or revert the faulty release on the deployment branch through normal review, then redeploy and repeat the health and smoke checks. Save any required fictional exports before removing or replacing the app.

## Streamlit references

- [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Application dependency discovery](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Delete your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/delete-your-app)
