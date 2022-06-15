from linode_api4 import LinodeClient

import os


def create_client(token: str) -> LinodeClient | None:
    try:
        client = LinodeClient(token)
        print("[CLIENT] created")

    except Exception as e:
        client = None
        print(f"[CLIENT] Error creating client: {e}")

    return client


if __name__ == "__main__":
    TOKEN = os.getenv("LINODE_PAT")
    client = create_client(TOKEN)
    regions = client.regions()

    for region in regions:
        print(region)
