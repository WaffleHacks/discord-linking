from authlib.integrations.flask_client import OAuth

registry = OAuth()

# Setup Auth0
registry.register("auth0", client_kwargs={"scope": "openid profile email"})

# Setup Discord
registry.register(
    "discord",
    api_base_url="https://discord.com/api/",
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    userinfo_endpoint="https://discord.com/api/users/%40me",
    client_kwargs={
        "token_endpoint_auth_method": "client_secret_post",
        "scope": "identify",
    },
)


def init(app):
    registry.init_app(app)
