import argparse
import asyncio
import logging

from grpclib.health.service import Health
from grpclib.server import Server

from courses.db import engine
from courses.models import Base
from courses.service import CoursesService


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    Base.metadata.create_all(bind=engine)
    server = Server([CoursesService(), Health()])
    await server.start("0.0.0.0", args.port)
    logging.info(f"GRPC server started on {args.port} port")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
