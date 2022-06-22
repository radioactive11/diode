import paramiko
from paramiko.client import SSHClient

import os
from time import sleep

import celery
from celery import Celery, current_task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult

from app.core.deploy import Deploy

celery = Celery("tasks", broker="redis://localhost:6379/0", backend="rpc://")

celery_log = get_task_logger(__name__)


CONST_SUPERVISOR_CONFIG = {
    "fastapi": "venv/bin/uvicorn main:app --reload",
}


class Deploy(celery.Task):
    def get_status(self):
        return self.__status

    def __parse_env(self):
        keys = self.__env_vars.keys()
        vars_str = "environment="
        for key in keys:
            temp_str = f"{key}={self.__env_vars[key]},"
            vars_str += temp_str

        vars_str = vars_str[:-1]

        return vars_str

    def connect(self) -> bool:
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.__ssh_client.connect(
                self.__ip_addr, username="root", password=self.__ssh_key
            )
            return True

        except Exception as e:
            print(f"[SSH Error] - {e}")
            return False

    def run_script(self) -> bool:
        SHELL_FILE_PATH = os.path.join(os.getcwd(), "build", f"{self.__app_type}.sh")

        with open(SHELL_FILE_PATH, "r") as file:
            commands = file.readlines()

        commands = [item.rstrip("\n") for item in commands if item != "\n"]

        lookup = {
            "$GIT_REPO": self.__git_repo,
            "$SUPERVIOR_CMD": CONST_SUPERVISOR_CONFIG[self.__app_type],
        }

        for command in commands:
            for token in lookup:
                command = command.replace(token, lookup[token])

            if command[0] == "#":
                print(f"[LOG] - {command}")
                self.__status = command[2:]
                current_task.update_state(
                    state=self.__status, meta={"process_percent": "randomize"}
                )

                continue

            print(f"Running: {command}")

            command = "TERM=xterm " + command
            stdin, stdout, stderr = self.__ssh_client.exec_command(command)

            stdin.close()
            _output = stdout.read()
            _error = stderr.read()

            output = _output.decode()
            error = _error.decode()

            if error != "" and output == "":
                print(f"Error - {error}")
                current_task.update_state(state=error, meta={"error": "randomize"})
                return False

            else:
                print(output)

        supervisor_command = (
            f"command=/root/app/{CONST_SUPERVISOR_CONFIG[self.__app_type]}"
        )
        stdin, stdout, stderr = self.__ssh_client.exec_command(
            f"sudo sed -i '3s|.*|{supervisor_command}|' /etc/supervisor/conf.d/app.conf",
            get_pty=True,
        )

        if stderr != "" and stdout == "":
            return False

        env_var_command = self.__parse_env()
        self.__ssh_client.exec_command(
            f"sudo sed -i '5s|.*|{env_var_command}|' /etc/supervisor/conf.d/app.conf",
            get_pty=True,
        )

        stdin, stdout, stderr = self.__ssh_client.exec_command(
            "sudo supervisorctl reread"
        )

        if stderr != "" and stdout == "":
            return False

        stdin, stdout, stderr = self.__ssh_client.exec_command(
            "sudo supervisorctl reload"
        )

        if stderr != "" and stdout == "":
            return False

    def run(
        self, ip_addr: str, ssh_key: str, app_type: str, repo_url: str, env: dict
    ) -> None:
        self.__ssh_client: SSHClient = paramiko.client.SSHClient()
        self.__ip_addr: str = ip_addr
        self.__ssh_key: str = (
            r"""&i/(Kz391IM!VSw%H6nm4_!2w"E[6UXX]V=db+$`H^*4x@o`T5YbB]y+AHM!XROz"""
        )

        self.__app_type: str = app_type
        self.__git_repo: str = repo_url
        self.__env_vars: dict = env

        self.connect()
        self.run_script()

    def print_all(self):
        print(self.__ip_addr)


def task_log(task_id: str):
    result = celery.AsyncResult(task_id)
    result_dict = {
        "task_id": task_id,
        "task_status": result.status,
        "task_result": result.result,
    }
    return result_dict


DeployTask = celery.register_task(Deploy())
