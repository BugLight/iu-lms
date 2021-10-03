import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

from tasks.proto import tasks_pb2, tasks_pb2_grpc

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from tasks.db import engine
from tasks.models import Base
from tasks.service import TasksService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    Base.metadata.create_all(bind=engine)
    server = grpc.server(ThreadPoolExecutor())
    tasks_pb2_grpc.add_TasksServicer_to_server(TasksService(), server)
    server.add_insecure_port("0.0.0.0:{}".format(args.port))
    health_servicer = health.HealthServicer()
    health_servicer.set(tasks_pb2.DESCRIPTOR.services_by_name["Tasks"].full_name,
                        health_pb2.HealthCheckResponse.SERVING)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    server.start()
    logging.info("GRPC server started")
    server.wait_for_termination()
