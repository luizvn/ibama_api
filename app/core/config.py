from dynaconf import Dynaconf, Validator
from dynaconf.utils.boxing import DynaBox

settings: DynaBox = Dynaconf(
    env_switcher="APP_ENV",
    default_env="default",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=False,
    envvars=True,
    envvar_prefix=False,
    PROJECT_NAME="API de Autos de Infração - IBAMA",
    ALGORITHM="HS256",
)

settings.validators.register(
    Validator(
        "database_url",
        "secret_key",
        "algorithm",
        "access_token_expire_minutes",
        must_exist=True,
    ),
    Validator(
        "secret_key",
        len_min=32,
        messages={"len_min": "secret_key precisa ter pelo menos 32 caracteres."}
    ),
    Validator(
        "database_url",
        cont="asyncmy",
        messages={"cont": "database_url deve usar o driver 'asyncmy'"}
    )
)

settings.validators.validate()
