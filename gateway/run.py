import argparse
from gateway.app import app
import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
