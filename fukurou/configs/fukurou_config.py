import json
import logging

from os.path import exists

class FukurouConfig:
    def __init__(self, logger: logging.Logger):
        self.FILE_NAME = "discord_token.json"
        self.DEFAULT_FORMAT = {
            "client_id": "INSERT_CLIENTID_HERE",
            "permissions": "INSERT_PERMISSIONS_HERE",
            "token": "INSERT_TOKEN_HERE"
        }

        self.logger = logger


    # Check if json file exists
    def exists(self): 
        return exists(self.FILE_NAME)
    
    
    # Initialize json for token
    def init(self, force_init = False):
        if not force_init and self.exists():
            return

        json_str = json.dumps(self.DEFAULT_FORMAT, sort_keys = True, indent = 4)

        file = open(self.FILE_NAME, "w")
        file.write(json_str)
        file.close()


    # Read a Client ID from json file
    def getClientId(self):
        if not self.exists():
            self.logger.error(f"Cannot find {self.FILE_NAME}!")
            return None

        file = open(self.FILE_NAME, "r")
        json_str = file.read()

        deserialized = json.loads(json_str)
        self.logger.debug(f"Read client_id from {self.FILE_NAME}: " + deserialized["client_id"])

        return deserialized["client_id"]


    # Read permissions from json file
    def getPermissions(self):
        if not self.exists():
            self.logger.error(f"Cannot find {self.FILE_NAME}!")
            return None

        file = open(self.FILE_NAME, "r")
        json_str = file.read()

        deserialized = json.loads(json_str)
        self.logger.debug(f"Read permissions from {self.FILE_NAME}: " + deserialized["permissions"])

        return deserialized["permissions"]


    # Read a token from json file
    def getToken(self):
        if not self.exists():
            self.logger.error(f"Cannot find {self.FILE_NAME}!")
            return None

        file = open(self.FILE_NAME, "r")
        json_str = file.read()

        deserialized = json.loads(json_str)
        self.logger.debug(f"Read token from {self.FILE_NAME}: " + deserialized["token"])

        return deserialized["token"]


    def getInviteLink(self):
        if not self.exists():
            self.logger.error(f"Cannot find {self.FILE_NAME}!")
            return None

        client_id = self.getClientId()
        permissions = self.getPermissions()

        return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot"