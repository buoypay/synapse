import json
import logging
from typing import TYPE_CHECKING, Tuple


from synapse.http.servlet import parse_string
from synapse.http.server import DirectServeHtmlResource
from twisted.web.server import Request

from synapse.module_api import ModuleApi

logger = logging.getLogger(__name__)


class DemoResource(DirectServeHtmlResource):
    def __init__(self, config):
        super(DemoResource, self).__init__()
        self.config = config

    async def _async_render_POST(self, request: Request) -> Tuple[int, bytes]:
        logger.info("/_synapse/modules/cognito/login")

        # get the access_token and id_token from request
        access_token = parse_string(request, "access_token", required=True)
        id_token = parse_string(request, "id_token", required=True)

        # TODO: parse the token, make sure it is valid based on:
        # - cognito client's public key (inject from Env Var)
        # - access token hasn't expired
        # - other security???

        # TODO: internal call to get the login token

        request.setHeader(b"Content-Type", b"application/json")
        body = json.dumps({"login_token": "12345"}).encode('utf-8')

        return 200, body
    
class Cognito:
    def __init__(self, config: dict, api: ModuleApi):
        logger.info("Starting Cognito module")

        self.config = config
        self.api = api

        self.api.register_web_resource(
            path="/_synapse/modules/cognito/login",
            resource=DemoResource(self.config),
        )

    @staticmethod
    def parse_config(config):
        return config