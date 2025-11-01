from dynaconf import Dynaconf, Validator
from dynaconf.utils.boxing import DynaBox

settings: DynaBox = Dynaconf(
    env_switcher="APP_ENV",
    default_env="development",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
    envvar_prefix=False,
    PROJECT_NAME="API de Autos de Infração - IBAMA",
    ALGORITHM="HS256",
)

settings.validators.register(
    Validator(
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        must_exist=True,
    ),
    Validator(
        "SECRET_KEY",
        min_len=32,
        messages={"min_len": "SECRET_KEY precisa ter pelo menos 32 caracteres."}
    ),
    Validator(
        "DATABASE_URL",
        must_contain="asyncmy",
        messages={"must_contain": "DATABASE_URL deve usar o driver 'asyncmy'"}
    )
)

settings.validators.validate()
