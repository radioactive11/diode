import paramiko
from paramiko.client import SSHClient

import os


CONST_SUPERVISOR_CONFIG = {
    "fastapi": "venv/bin/uvicorn main:app --reload",
}


class Deploy:
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

    def run_script(self, celery_obj) -> bool:

        SHELL_FILE_PATH = os.path.join(os.getcwd(), "build", "fastapi.sh")

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
                celery_obj.update_state(state=self.__status)
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
                return False

            else:
                print(output)

        #! Add supervisor configuration
        supervisor_command = f"command=/root/app/{CONST_SUPERVISOR_CONFIG['fastapi']}"
        stdin, stdout, stderr = self.__ssh_client.exec_command(
            f"sudo sed -i '3s|.*|{supervisor_command}|' /etc/supervisor/conf.d/app.conf",
            get_pty=True,
        )

        if stderr != "" and stdout == "":
            return False

        #! Update Environment Variables
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

    def __init__(
        self, ip_addr: str, ssh_key: str, app_type: str, repo_url: str, env: dict
    ) -> None:
        self.__ssh_client: SSHClient = paramiko.client.SSHClient()
        self.__ip_addr: str = ip_addr
        self.__ssh_key: str = (
            r"""z9"'%;oZZzNEaD<Z6T0)KPnuz>-Zl9I=ge=c'<jv&:tM.xXETTN$vm"""
        )
        self.__app_type: str = app_type
        self.__git_repo: str = repo_url
        self.__env_vars: dict = env

        self.connect()
        self.run_script()

    def print_all(self):
        print(self.__ip_addr)


# ssh_key = r"""z9"'%;oZZzNEaD<Z6T0)KPnuz>-Zl9I=ge=c'<jv&:tM.xXETTN$vm"""
# dp = Deploy(
#     "172.105.37.44",
#     ssh_key,
#     app_type="fastapi",
#     repo_url="https://github.com/radioactive11/fastapi-sample-app",
#     env={"PYTHONPATH": "app"},
# )
