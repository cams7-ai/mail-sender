from api import create_app

import os
import uvicorn
from infrastructure import load_dotenv

app = create_app()

def run() -> None:
    load_dotenv()
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)

if __name__ == "__main__":  # pragma: no cover
    run()
