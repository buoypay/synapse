import json
import logging


from twisted.web.resource import Resource
from twisted.web.server import Request

from synapse.module_api import ModuleApi

logger = logging.getLogger(__name__)


class DemoResource(Resource):
    def __init__(self, config):
        super(DemoResource, self).__init__()
        self.config = config

    def render_GET(self, request: Request):
        logger.info("/_synapse/client/demo/hello")
        # name = request.args.get(b"name")[0]
        # request.setHeader(b"Content-Type", b"application/json")
        return json.dumps({"hello": True})


class Cognito:
    def __init__(self, config: dict, api: ModuleApi):
        logger.info("Starting Cognito module")

        self.config = config
        self.api = api

        self.api.register_web_resource(
            path="/_synapse/client/demo/hello",
            resource=DemoResource(self.config),
        )

    @staticmethod
    def parse_config(config):
        return config