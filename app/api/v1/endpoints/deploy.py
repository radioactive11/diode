from fastapi import APIRouter

from app.core.celery_worker import DeployTask, task_log
from app.schema.deploy import DeployRepo

router = APIRouter()


@router.post("/repo_new")
def init_deploy_from_repo(request_body: DeployRepo):
    ip_addr = request_body.ip_addr
    ssh_key = request_body.ssh_key
    app_type = request_body.app_type
    repo_url = request_body.repo_url
    env = request_body.env

    result = DeployTask.delay(ip_addr, ssh_key, app_type, repo_url, env)
    # result = dt.run_script.delay()

    return {"task_id": result.task_id}


#! Convert this to a post requst later
@router.get("/repo_status/{task_id}")
def deployment_status(task_id: str):
    result = task_log(task_id)

    return result
