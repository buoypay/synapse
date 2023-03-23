import json
import logging
from typing import TYPE_CHECKING, Tuple

import cognitojwt
from pydantic import StrictStr

from twisted.web.server import Request

from synapse.api.errors import SynapseError
from synapse.http.server import DirectServeHtmlResource
from synapse.http.servlet import (
    parse_and_validate_json_object_from_request,
)
from synapse.module_api import ModuleApi
from synapse.rest.models import RequestBodyModel
from synapse.types import RoomAlias, UserID, create_requester

if TYPE_CHECKING:
    from synapse.server import HomeServer


logger = logging.getLogger(__name__)

# TODO: get from env var
REGION = "eu-central-1"
USERPOOL_ID = "eu-central-1_C0omejJNP"
APP_CLIENT_ID = "61aa9r86j7hput4nod62nang7i"

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
        
        # TODO: verify access token? Or can we just use the id_token?
        access_token = body.access_token
        id_token = body.id_token

        # TODO: parse the token, make sure it is valid based on:
        # - cognito client's public key (inject from Env Var)
        # - access token hasn't expired
        # - other security???
        verified_claims: dict = cognitojwt.decode(
          id_token,
          REGION,
          USERPOOL_ID,
          app_client_id=APP_CLIENT_ID,
          # todo: set to False!
          testmode=True  # Disable token expiration check for testing purposes
        )
        logger.info("Verified user from `id_token` with email: %s", verified_claims['email'])
        
        # derive the username from the customer's email address
        cognito_username_localpart = verified_claims['email'].split('@')[0].replace('+', '-')
        user = UserID(cognito_username_localpart, self.api._hs.hostname)
        user_id = user.to_string()

        # Check ther username
        try:
          await self.api._hs.get_registration_handler().check_username(
            localpart=cognito_username_localpart,
          )
          # register the user if not exists
          await self.api._hs.get_registration_handler().register_user(
            localpart=cognito_username_localpart,
            bind_emails=[verified_claims['email']],
            admin=False,
          )
          logger.info("Registered new user %s", user_id)
        except SynapseError:
            logger.info("localpart already registered: %s", cognito_username_localpart)

  
        # internal call to get the login token
        login_token = await self.api._hs.get_auth_handler().create_login_token_for_user_id(
            user_id,
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