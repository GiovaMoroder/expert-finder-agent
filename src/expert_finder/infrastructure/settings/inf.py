from infisical_sdk import InfisicalSDKClient
from dotenv import load_dotenv, dotenv_values

load_dotenv(override=True)
env_vars = dotenv_values()

client = InfisicalSDKClient(
    host="https://app.infisical.com"
)  # host is optional, defaults to https://app.infisical.com

client.auth.universal_auth.login(
    env_vars["INFISICAL_USER"], env_vars["INFISICAL_KEY"]
)


def get_secret(name: str, env: str):
    val = client.secrets.get_secret_by_name(
        name,
        project_id=env_vars["INFISICAL_PROJECT_ID"],
        environment_slug=env,
        secret_path="/",
    )
    return val.secretValue
