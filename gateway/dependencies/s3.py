import boto3
from fastapi import Depends

from gateway.settings import Settings, get_settings


def s3_client(settings: Settings = Depends(get_settings)):
    session = boto3.session.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                    region_name=settings.AWS_DEFAULT_REGION)
    return session.client(service_name="s3", endpoint_url=settings.S3_ENDPOINT_URL)
