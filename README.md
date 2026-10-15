# PROJECT QUEEN — iPhone cloud prototype

This is a Streamlit mobile-friendly web app. It is not a native iOS app and does not include voice cloning, persistent memory, or an avatar yet.

## Deploy using only Safari on iPhone
1. Create a GitHub account at https://github.com and a new repository named `project-queen-iphone`. **Use a private repository if supported by your hosting account.**
2. In the repository choose **Add file → Upload files** (in Safari, **Request Desktop Website** if needed). Upload `app.py` and `requirements.txt` from Files. Commit the files. Never upload an API key.
3. Create an OpenAI API key through https://platform.openai.com/api-keys and set a spending limit/budget. API billing is separate from ChatGPT subscriptions.
4. Visit https://share.streamlit.io/ and sign in with GitHub. Choose **Create app**, select your repository, branch `main`, and entry point `app.py`. Deploy. Hosting availability, repo visibility, and free-plan limits can change.
5. In the Streamlit app management dashboard, open **Settings → Secrets** and enter `OPENAI_API_KEY = "your_actual_key_here"` (do not include this key in GitHub, screenshots, or messages). Save and reboot/redeploy the app if required.
6. Open the app's URL in Safari. Use **Share → Add to Home Screen** to create a QUEEN icon.

## Important security and privacy
- This demo does **not** have user authentication. A public URL may be accessible to others and could consume your API credits. Before using it with sensitive data or sharing its link, add real sign-in or host it behind access control.
- Conversation state is temporary. Chat export is available; no persistent memory is promised.
- Messages are processed by OpenAI's API. Check its data handling policies before sharing confidential information.
- Do not paste passwords, API keys, or private records into the chat.
- The app catches provider errors without showing raw exceptions or secrets.

## Run locally later (optional)
`pip install -r requirements.txt && OPENAI_API_KEY=... streamlit run app.py`
