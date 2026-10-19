# Local API configuration

Edit the `.env` file in the repository root:

```dotenv
AGENT_DIPLOMACY_API_KEY=put-your-new-key-here
AGENT_DIPLOMACY_BASE_URL=https://api.deepseek.com
AGENT_DIPLOMACY_MODEL=deepseek-flash
AGENT_DIPLOMACY_TIMEOUT_SECONDS=90
```

Use a fresh key from your provider. Do not paste it into chat, screenshots, source code, or `.env.example`. The `.env` file is excluded from Git.

After saving `.env`, restart the backend so it loads the new values. Start it from the repository root:

```bash
.venv/bin/uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

The backend loads the repository-root `.env` when it starts. Values in `.env` take precedence over inherited shell variables. The timeout must be between 5 and 300 seconds. The frontend does not need the API key and should never contain it.

For another OpenAI-compatible provider, change `BASE_URL`, `MODEL`, and the key together. The base URL should be the provider’s plain API base URL, without Markdown brackets or parentheses. DeepSeek uses `https://api.deepseek.com`.
