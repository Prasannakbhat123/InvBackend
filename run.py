import uvicorn
import os

if __name__ == "__main__":
    # Production-default runner.
    os.environ.setdefault("APP_ENV", "production")
    os.environ.setdefault("ENV_FILE", ".env")

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
