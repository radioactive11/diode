from unittest import result
from fastapi import APIRouter

from linode_api4 import LinodeClient
from app.core.catalouge import users_linodes

from app.core.instance_handler import (
    create_instance,
    delete_instance,
    get_metrics,
    get_status,
)
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


@router.get("/metrics")
def get_instance_metrics(token: str, id: str):
    client = create_client(token)
    result = get_metrics(id, client)

    return result


@router.get("/status")
def get_instance_metrics(token: str, id: str):
    client = create_client(token)
    result = get_status(id, client)

    return result


@router.get("/instances")
def list_user_intances(token: str):
    client = create_client(token)
    result = users_linodes(client)

    return result
