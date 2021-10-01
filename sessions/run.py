import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

from sessions.proto import sessions_pb2_grpc, sessions_pb2

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from sessions.db import engine
from sessions.models import Base
from sessions.service import SessionsService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    Base.metadata.create_all(bind=engine)
    server = grpc.server(ThreadPoolExecutor())
    sessions_pb2_grpc.add_SessionsServicer_to_server(SessionsService(), server)
    server.add_insecure_port("localhost:{}".format(args.port))
    health_servicer = health.HealthServicer()
    health_servicer.set(sessions_pb2.DESCRIPTOR.services_by_name["Sessions"].full_name,
                        health_pb2.HealthCheckResponse.SERVING)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    server.start()
    logging.info("GRPC server started")
    server.wait_for_termination()
