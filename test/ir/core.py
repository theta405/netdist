# Imports

import os
import ssl

from elasticsearch import Elasticsearch
from elasticsearch.connection import create_ssl_context

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from json import dumps, loads
from traceback import extract_stack


# Constants

ROOT = Path(__file__).parent # Root path
SEP = os.sep


# Variables and so

context = create_ssl_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


# Classes

class config(): # Config of a module
    def __init__(self, **conf):
        modulePath = extract_stack()[-2][0]
        self.moduleName = modulePath.split(SEP)[-1].split(".")[0]
        if not hasConfig(self.moduleName): # Init if no config
            saveConfig(self.moduleName, conf)
        else:
            conf = readConfig(self.moduleName)
        configs[self.moduleName] = conf

    def save(self):
        saveConfig(self.moduleName, configs[self.moduleName])
        

class customDict(dict): # Customized dict, where elements are accessible using attributes
    def __getattr__(self, __name):
        return self.get(__name)
 
    def __setattr__(self, __name, __value):
        self[__name] = __value

    def __setitem__(self, __key, __value):
        if isinstance(__value, dict) and not isinstance(__value, customDict):
            __value = customDict(__value)
        super().__setitem__(__key, __value)

    def __init__(self, data = None):
        if data is None: data = {}
        super().__init__(data)
        for e in self.keys(): # Traverse to convert inner dicts
            if isinstance(self[e], dict) and not isinstance(self[e], customDict):
                self[e] = customDict(self[e])


class stopException(BaseException): pass


class customException(BaseException): pass


# File handlers

def getPath(name, fileName = ""):
    return ROOT / name / fileName # Return concatenated path


def hasConfig(name): # Check if config exists
    return getPath("configs", f"{name}.json").exists()


def readConfig(name): # Config reader
    with open(getPath("configs", f"{name}.json"), "r") as config:
        return loads(config.readline())


def saveConfig(name, data): # Config saver
    folderPath = getPath("configs")
    if not folderPath.exists(): folderPath.mkdir(parents = True)
    with open(folderPath / f"{name}.json", "w+") as config:
        config.writelines([dumps(data, ensure_ascii = False)])


# Functions

def importModules(modulesList = None): # Import modules
    modulesList = modulesList if modulesList else {}
    for f in (getPath("modules")).rglob("*.py"): # Fetch modules
        try: # Error handler
            spec = spec_from_file_location(f.stem, f)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
        except BaseException as e:
            print(f"🚫Error importing [{f.stem}]: {e}")
            continue
        modulesList[f.stem] = module
    return modulesList


def getES():
    return Elasticsearch(
        [configs.system.server_ip],
        port = configs.system.server_port,
        scheme = configs.system.scheme,
        http_auth = (
            configs.system.username,
            configs.system.password
        ),
        ssl_context = context
    )


def initialize():
    global configs, modules
    configs = customDict()
    modules = customDict(importModules())


initialize()