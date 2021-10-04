import argparse
import asyncio
import logging

from grpclib.health.service import Health
from grpclib.server import Server

from sessions.db import engine
from sessions.models import Base
from sessions.service import SessionsService


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    Base.metadata.create_all(bind=engine)
    server = Server([SessionsService(), Health()])
    await server.start("0.0.0.0", args.port)
    logging.info(f"GRPC server started on {args.port} port")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
