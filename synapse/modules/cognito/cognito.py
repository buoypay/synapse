import json
import logging
from typing import TYPE_CHECKING, Tuple
from pydantic import Extra, StrictStr


from synapse.http.servlet import (
    parse_string,
    parse_and_validate_json_object_from_request,
)
from synapse.http.server import DirectServeHtmlResource
from synapse.rest.models import RequestBodyModel
from twisted.web.server import Request

from synapse.module_api import ModuleApi

if TYPE_CHECKING:
    from synapse.server import HomeServer


logger = logging.getLogger(__name__)


class DemoResource(DirectServeHtmlResource):
    def __init__(self, config, api: ModuleApi):
        super(DemoResource, self).__init__()
        self.config = config
        self.api = api


    class PostBody(RequestBodyModel):
        access_token: StrictStr
        id_token: StrictStr

    async def _async_render_POST(self, request: Request) -> Tuple[int, bytes]:
        logger.info("/_synapse/modules/cognito/login")

        # get the access_token and id_token from request
        body = parse_and_validate_json_object_from_request(request, self.PostBody)
        access_token = body.access_token
        id_token = body.id_token

        # TODO: parse the token, make sure it is valid based on:
        # - cognito client's public key (inject from Env Var)
        # - access token hasn't expired
        # - other security???

        # TODO: register the user if not exists
        new_user = await self.api._hs.get_registration_handler().register_user(
            localpart="test2",
            bind_emails=["test2@customer.com"],
            admin=False,
        )
        logger.info("Registered new user %s", new_user)

        # internal call to get the login token
        login_token = await self.api._hs.get_auth_handler().create_login_token_for_user_id(
            new_user
            # TODO: make this shorter
            1000 * 60 * 30,
            "cognito",
        )

        request.setHeader(b"Content-Type", b"application/json")
        body = json.dumps({"login_token": login_token}).encode('utf-8')

        return 200, body
    
class Cognito:
    def __init__(self, config: dict, api: ModuleApi):
        logger.info("Starting Cognito module")

        self.config = config
        self.api = api

        self.api.register_web_resource(
            path="/_synapse/modules/cognito/login",
            resource=DemoResource(self.config, self.api),
        )

    @staticmethod
    def parse_config(config):
        return config