"""
ssh_client.py

SSH Client for Raspberry Pi
"""

import paramiko


class SSHClient:

    def __init__(self):

        self.hostname = ""
        self.username = ""
        self.password = ""

        self.client = None

    def connect(self, hostname, username, password):

        self.hostname = hostname
        self.username = username
        self.password = password

        self.client = paramiko.SSHClient()

        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        try:

            self.client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                timeout=10
            )

            print("Connected Successfully")

            return True

        except Exception as e:

            print("Connection Failed")

            print(e)

            return False

    def execute(self, command):

        if self.client is None:

            print("SSH Not Connected")

            return

        stdin, stdout, stderr = self.client.exec_command(command)

        output = stdout.read().decode()

        error = stderr.read().decode()

        if output:
            print(output)

        if error:
            print(error)

        return output

    def disconnect(self):

        if self.client:

            self.client.close()

            print("Disconnected")


if __name__ == "__main__":

    ssh = SSHClient()

    HOST = input("Raspberry Pi IP : ")

    USER = input("Username : ")

    PASSWORD = input("Password : ")

    if ssh.connect(HOST, USER, PASSWORD):

        while True:

            print("\n========================")
            print("1. Check Status")
            print("2. Run Python")
            print("3. Linux Command")
            print("4. Exit")

            choice = input("Choice : ")

            if choice == "1":

                ssh.execute("hostname")

            elif choice == "2":

                ssh.execute("python3 main.py")

            elif choice == "3":

                cmd = input("Linux Command : ")

                ssh.execute(cmd)

            elif choice == "4":

                ssh.disconnect()

                break
            