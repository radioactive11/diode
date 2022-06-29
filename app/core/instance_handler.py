from typing import Dict
from linode_api4 import LinodeClient, Instance

import os
from dotenv import load_dotenv

from app.schema import instance

PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCBqtVjKq3VjnWpcerUYCmUrLPFBXyE6M7kxulQ2qabdXgvu3cu9lRxgZS7K/8lJMhS39EgFtdoD+AowYD73g0Oj0XTn3rNhr9LIUxWD0rZuVDma9tzwUEwWdRMeLZgnjGA6AllprHb+EF0K2F9bXuOuT9N3UpN9j6Gs2LQ+xCSvWElZrugpfQvlBq2MdMIkQy2s3GZZG9Rdpf9RhqkjRZg23iWL7fHB4kdcWI6KZsWSJuE/H63LtHheFGqMmQtFFBiqtQGVLkqj3EH/iQih9348oujs0pVVXMcm+Ji46yag5AVGu1JoRLf14Q9UxlYc/cDXcLXHNfhg8BN9oH3jGtn"


def create_instance(details: instance.CreateInstance, client: LinodeClient) -> Dict:
    new_linode, password = client.linode.instance_create(
        details.instance_type, details.region, details.image, authorized_keys=PUBLIC_KEY
    )

    ip4_addr = new_linode.ipv4[0]
    _id = new_linode.id

    return {
        "id": _id,
        "ip4_addr": ip4_addr,
        "password": r"{password}".format(password=password),
    }


def delete_instance(details: instance.DeleteInstance, client: LinodeClient) -> bool:
    instance = Instance(client, details.instance_id)
    result = instance.delete()

    return result


def get_metrics(id: str, client: LinodeClient):
    instance = Instance(client, id)
    try:
        result = instance.stats
    except Exception as e:
        result = {"error": e}

    return result


def get_status(instance_id: str, client: LinodeClient):
    instance = Instance(client, instance_id)
    result = instance.status

    return {"status": result}
