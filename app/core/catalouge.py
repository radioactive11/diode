from pprint import pprint
from typing import Dict, List

from linode_api4 import LinodeClient

from dotenv import load_dotenv
import os


def available_regions(client: LinodeClient) -> List:
    regions = client.regions()
    region_list = []

    for region in regions:
        region_dict: Dict = region._raw_json
        region_dict.pop("resolvers", None)
        region_list.append(region_dict)

    return region_list


def available_images(client: LinodeClient):
    images = client.images()
    image_list = []

    for image in images:
        image_dict: Dict = image._raw_json
        image_list.append(image_dict)

    return image_list


if __name__ == "__main__":
    TOKEN = os.getenv("LINODE_PAT")
    client = LinodeClient(TOKEN)
    regions = available_regions(client)
    pprint(regions)
