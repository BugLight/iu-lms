import argparse
import asyncio
import logging

from grpclib.health.service import Health
from grpclib.server import Server

from tasks.db import engine
from tasks.models import Base
from tasks.service import TasksService


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    Base.metadata.create_all(bind=engine)
    server = Server([TasksService(), Health()])
    await server.start("0.0.0.0", args.port)
    logging.info(f"GRPC server started on {args.port} port")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
