import os
import io
import re
import yaml
import logging
import requests
import subprocess

logging.basicConfig(level=logging.INFO)

_PORT = 34567


class Plugin:
    manifest_file = ".well-known/ai-plugin.json"
    spec_file = "openapi.yaml"
    run_file = "main.py"
    
    introduction = """Before giving a response to the user, you can interact with several plugins to gather information. Whenever you are unable to answer a question with confidence, you can call a plugin in the format of "💬PLUGIN_NAME: OPERATION [PARAM=VALUE...]\nDATA". Each of my message may contain at most one plugin request, placed at the end. The available plugins and their operations are listed as follows:\n"""
    request_pattern = re.compile(
        r"^💬(?P<plugin>[\w ]+): (?P<operation>\w+)(?P<params>( +\w+=\S+)* *)\n(?P<body>.*)$",
        re.DOTALL | re.MULTILINE
    )

    instances: dict[str, "Plugin"]
    
    def __init__(self, name: str, url: str = None) -> None:
        self.name = name
        dir = os.path.dirname(__file__)
        self.spec_path = os.path.join(dir, name, self.spec_file)
        self.run_path = os.path.join(dir, name, self.run_file)
        self.op_paths: dict[str, tuple[str, str]] = {}
        if not os.path.exists(self.run_path):
            logging.warn(f'Plugin {name} does not exist.')
            return
        if url is None:
            global _PORT
            self.url = f'http://localhost:{_PORT}'
            self.proc = subprocess.Popen(["python", self.run_path, "--port", str(_PORT)])
            _PORT += 1
        else:
            self.url = url.rstrip('/')
            self.proc = subprocess.Popen(["python", self.run_path, "--host", self.url])

    def get_spec(self) -> dict:
        with open(self.spec_path, encoding='utf8') as f:
            spec = yaml.safe_load(f)
        operations: dict[str, str] = {}
        for path, ops in spec['paths'].items():
            for op, info in ops.items():
                key = info['operationId']
                operations[key] = info['summary']
                self.op_paths[key] = (path, op)
        return dict(
            description = spec['info']['description'],
            operations = operations,
        )

    def call(self, operation: str, data: str, params: dict=None):
        path, op = self.op_paths[operation]
        if params is not None:
            path = path.format(**params)
        url = self.url + path
        req = requests.request(op, url, data=data)
        return req.text
    
    @classmethod
    def load_all(cls):
        dir = os.path.dirname(__file__)
        plugins = [cls(name) for name in os.listdir(dir) if name[0] not in '._']
        cls.instances = {
            p.name: logging.info(f"Loaded plugin: {p.name}") or p 
            for p in plugins if hasattr(p, 'proc')
        }
        
    @classmethod
    def get_instructions(cls):
        sio = io.StringIO()
        yaml.safe_dump({k: v.get_spec() for k, v in cls.instances.items()}, sio)
        return cls.introduction + sio.getvalue()
    
    @classmethod
    def send_request(cls, request: str):
        m = cls.request_pattern.match(request)
        plugin = cls.instances[m['plugin']]
        params = dict(s.split('=') for s in m['params'].split())
        return plugin.call(m['operation'], m['body'], params)


Plugin.load_all()
