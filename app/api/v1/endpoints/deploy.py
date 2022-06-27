from fastapi import APIRouter

from app.core.celery_worker import DeployTask, ReDeployTask, task_log
from app.schema.deploy import DeployRepo, ReDeployRepo

router = APIRouter()


@router.post("/repo_new")
def init_deploy_from_repo(request_body: DeployRepo):
    ip_addr = request_body.ip_addr
    ssh_key = request_body.ssh_key
    app_type = request_body.app_type
    repo_url = request_body.repo_url
    env = request_body.env

    encoded_ssh_key = ssh_key.encode()
    ssh_key = encoded_ssh_key.decode("unicode_escape")

    result = DeployTask.delay(ip_addr, ssh_key, app_type, repo_url, env)

    return {"task_id": result.task_id}


@router.post("/redeploy")
def redeploy_from_github(request_body: ReDeployRepo):
    ip_addr = request_body.ip_addr
    ssh_key = request_body.ssh_key
    app_type = request_body.app_type
    env = request_body.env

    result = ReDeployTask.delay(ip_addr, ssh_key, app_type, env)

    return {"task_id": result.task_id}


@router.get("/repo_status/{task_id}")
def deployment_status(task_id: str):
    result = task_log(task_id)

    return result
