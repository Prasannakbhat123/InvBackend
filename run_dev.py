import os
import uvicorn

if __name__ == "__main__":
    # Use Neon/local development configuration by default.
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("ENV_FILE", ".env.dev")

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
