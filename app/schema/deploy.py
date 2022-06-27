from pydantic import BaseModel


class DeployRepo(BaseModel):
    ip_addr: str
    ssh_key: str
    app_type: str
    repo_url: str
    env: dict


class ReDeployRepo(BaseModel):
    ip_addr: str
    ssh_key: str
    app_type: str
    env: dict
