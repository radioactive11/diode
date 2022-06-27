from typing import Dict
import paramiko
from paramiko.client import SSHClient

from dotenv import load_dotenv

import os
import secrets

import celery
from celery import Celery, current_task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult

from app.core.deploy import Deploy

load_dotenv()
REDIS_BROKER = os.getenv("REDIS_URL")
print(REDIS_BROKER)
celery = Celery("tasks", broker=REDIS_BROKER, backend="rpc://")

celery_log = get_task_logger(__name__)


CONST_SUPERVISOR_CONFIG = {
    "fastapi": "/root/app/venv/bin/uvicorn main:app --reload",
    "node": "npm run start",
    "react": "npm run build",
    "flask": "root/app/venv/bin/gunicorn main:app"
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

    def run_script(self) -> Dict:
        SHELL_FILE_PATH = os.path.join(os.getcwd(), "build", f"{self.__app_type}.sh")

        password = secrets.token_urlsafe(32)

        with open(SHELL_FILE_PATH, "r") as file:
            commands = file.readlines()

        commands = [item.rstrip("\n") for item in commands if item != "\n"]

        lookup = {
            "$GIT_REPO": self.__git_repo,
            "$SUPERVIOR_CMD": CONST_SUPERVISOR_CONFIG.get(self.__app_type, ""),
            "$REDIS_PW": password,
        }

        for command in commands:
            for token in lookup:
                print(token)
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
                return {"error": error}

        # * if we need to setup supervisor & nginx for the app
        if CONST_SUPERVISOR_CONFIG.get(self.__app_type):
            # * set the supervisor command customized for each app_type
            supervisor_command = f"command={CONST_SUPERVISOR_CONFIG[self.__app_type]}"
            stdin, stdout, stderr = self.__ssh_client.exec_command(
                f"sudo sed -i '3s|.*|{supervisor_command}|' /etc/supervisor/conf.d/app.conf",
                get_pty=True,
            )

            stdout = stdout.read()
            stderr = stderr.read()

            if stderr != "" and stdout == "":
                return {"error": error}

            # * set environment variables
            if self.__env_vars:
                env_var_command = self.__parse_env()
                self.__ssh_client.exec_command(
                    f"sudo sed -i '5s|.*|{env_var_command}|' /etc/supervisor/conf.d/app.conf",
                    get_pty=True,
                )

            # * Make supervisor read new changes
            stdin, stdout, stderr = self.__ssh_client.exec_command(
                "sudo supervisorctl reread"
            )

            stdout = stdout.read()
            stderr = stderr.read()

            if stderr != "" and stdout == "":
                return {"error": error}

            stdin, stdout, stderr = self.__ssh_client.exec_command(
                "sudo supervisorctl reload"
            )

            stdout = stdout.read()
            stderr = stderr.read()

            if stderr != "" and stdout == "":
                return {"error": error}

        current_task.update_state(
            state="Deployed", meta={"password": password, "status": "deployed"}
        )
        return {"password": password, "status": "deployed"}

    def run(
        self, ip_addr: str, ssh_key: str, app_type: str, repo_url: str, env: dict
    ) -> Dict:
        self.__ssh_client: SSHClient = paramiko.client.SSHClient()
        self.__ip_addr: str = ip_addr
        self.__ssh_key: str = r"""7Ou`ZS&?+6Jn80&jS(iMxCAK2?YN5m#d,ib`!=dfd]XwD@8hTXh@UY$fNy;HjmdAo*"#<67Lk7GG0%g`4Uca68YB"%9Q?0h#-W3*k"""

        self.__app_type: str = app_type
        self.__git_repo: str = repo_url
        self.__env_vars: dict = env

        self.connect()
        stat_result = self.run_script()

        return stat_result


class ReDeploy(celery.Task):
    def __parse_env(self):
        keys = self.__env_vars.keys()
        vars_str = "environment="
        for key in keys:
            temp_str = f"{key}={self.__env_vars[key]},"
            vars_str += temp_str

        vars_str = vars_str[:-1]

        return vars_str

    def connect(self):
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.__ssh_client.connect(
                self.__ip_addr, username="root", password=self.__ssh_key
            )
            return True

        except Exception as e:
            print(f"[SSH Error] - {e}")
            return False

    def run_script(self):
        SHELL_FILE = os.path.join(os.getcwd(), "build", f"re_{self.__app_type}.sh")

        with open(SHELL_FILE, "r") as fi:
            commands = fi.readlines()

        commands = [command.rstrip("\n") for command in commands if command != "\n"]

        for command in commands:
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
                return {"error": error}

        if self.__env_vars:
            env_var_command = self.__parse_env()
            self.__ssh_client.exec_command(
                f"sudo sed -i '5s|.*|{env_var_command}|' /etc/supervisor/conf.d/app.conf",
                get_pty=True,
            )

            # * Make supervisor read new changes
            stdin, stdout, stderr = self.__ssh_client.exec_command(
                "sudo supervisorctl reread"
            )

            stdout = stdout.read()
            stderr = stderr.read()

            if stderr != "" and stdout == "":
                return {"error": error}

            stdin, stdout, stderr = self.__ssh_client.exec_command(
                "sudo supervisorctl reload"
            )

            stdout = stdout.read()
            stderr = stderr.read()

            if stderr != "" and stdout == "":
                return {"error": error}

    def run(self, ip_addr: str, ssh_key: str, app_type: str, env: dict) -> Dict:
        self.__ssh_client: SSHClient() = paramiko.client.SSHClient()
        self.__ip_addr: str = ip_addr
        self.__ssh_key: str = r"""VeQa7vYzwDb2]lz,.ZFeSJ94HsD>c4H_P#kz:W7]+bA2Ze:7EUl\nY#E'_g+w6W9j7:m;9*X^[q,rdEmVe'_iXDWOT:"""

        self.__app_type: str = app_type
        self.__env_vars: dict = env

        self.connect()
        result = self.run_script()

        return result


def task_log(task_id: str):
    result = celery.AsyncResult(task_id)
    result_dict = {
        "task_id": task_id,
        "task_status": result.status,
        "task_result": result.result,
    }
    return result_dict


DeployTask = celery.register_task(Deploy())
ReDeployTask = celery.register_task(ReDeploy())
