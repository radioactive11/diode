from fastapi import APIRouter
from requests import request

from app.core import client_maker, catalouge

from app.schema import details

router = APIRouter()


@router.post("/regions")
def get_instance_details(request_body: details.Details):
    client = client_maker.create_client(request_body.token)
    details = catalouge.available_regions(client)

    return details


@router.post("/images")
def get_image_details(request_body: details.Details):
    client = client_maker.create_client(request_body.token)
    details = catalouge.available_images(client)

    return details


@router.post("/instances")
def get_instance_details(request_body: details.Details):
    client = client_maker.create_client(request_body.token)
    details = catalouge.available_instances(client)

    return details


@router.post("/all")
def get_all_details(request_body: details.Details):
    client = client_maker.create_client(request_body.token)
    details = catalouge.available_combined(client)

    return details
