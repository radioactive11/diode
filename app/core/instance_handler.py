from typing import Dict
from linode_api4 import LinodeClient, Instance

import os
from dotenv import load_dotenv

from app.schema import instance


def create_instance(details: instance.CreateInstance, client: LinodeClient) -> Dict:
    new_linode, password = client.linode.instance_create(
        details.instance_type, details.region, details.image
    )

    ip4_addr = new_linode.ipv4[0]
    _id = new_linode.id

    return {"id": _id, "ip4_addr": ip4_addr, "password": password}


def delete_instance(details: instance.DeleteInstance, client: LinodeClient) -> bool:
    instance = Instance(client, details.instance_id)
    result = instance.delete()

    return result
