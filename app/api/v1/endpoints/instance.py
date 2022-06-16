from unittest import result
from fastapi import APIRouter

from linode_api4 import LinodeClient

from app.core.instance_handler import create_instance, delete_instance
from app.core.client_maker import create_client
from app.schema import instance

router = APIRouter()


@router.post("/create")
def create_new_instance(request_body: instance.CreateInstance):
    client = create_client(request_body.token)
    new_instance_details = create_instance(request_body, client)

    return new_instance_details


@router.post("/delete")
def delete_existing_instance(request_body: instance.DeleteInstance):
    client = create_client(request_body.token)
    result = delete_instance(request_body, client)

    return {"result": result}
