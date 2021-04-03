from os import getenv
from typing import NamedTuple
from aws_lambda_powertools.utilities import parameters


class SalesforceConfig(NamedTuple):
    username: str
    password: str
    client_id: str
    client_secret: str
    base_url: str
    version: str = "60"


class PPPConfig(NamedTuple):
    dropzone_user: str
    dropzone_password: str
    dropzone_path: str
    dropzone_host: str
    dropzone_port: int
    valid_business_types: list
    sba_proxy_base_url: str
    webbank_vendor_key: str = None
    is_local: bool = False
    queue_name: str = ""


class DBConfig(NamedTuple):
    database_name: str
    host: str
    username: str
    password: str
    driver: str = None


class DropzoneConfig(NamedTuple):
    path: str
    host: str
    port: str
    username: str
    password: str


class DataDogConfig(NamedTuple):
    api_key: str
    app_key: str


def get_ssm_values(path):
    return parameters.get_parameters(path, decrypt=True)


def get_salesforce_config():
    param_name = getenv("SALESFORCE_SSM_PARAM_NAME")
    params = get_ssm_values(param_name)

    return SalesforceConfig(
        username=params["username"],
        password=params["password"],
        client_id=params["client_id"],
        client_secret=params["client_secret"],
        base_url=params["base_url"],
        version=params["api_version"],
    )


def get_ppp_config() -> PPPConfig:
    param_name = getenv("LAMBDA_SSM_PARAM_NAME")
    params = get_ssm_values(param_name)

    is_local = bool(getenv("IS_LOCAL", False))
    queue_name = str(getenv("POLLING_QUEUE_NAME"))

    return PPPConfig(
        dropzone_user=getenv("DROPZONE_USER", params["dropzone_user"]),
        dropzone_password=getenv("DROPZONE_PASSWORD", params["dropzone_password"]),
        dropzone_path=getenv("DROPZONE_PATH", params["dropzone_path"]),
        dropzone_host=getenv("DROPZONE_HOST", params["dropzone_host"]),
        dropzone_port=int(getenv("DROPZONE_PORT", params["dropzone_port"])),
        valid_business_types=getenv(
            "VALID_BUSINESS_TYPES", params["valid_business_types"]
        ).split(","),
        sba_proxy_base_url=getenv("SBA_PROXY_BASE_URL", params["sba_proxy_base_url"]),
        webbank_vendor_key=getenv("WEBBANK_VENDOR_KEY", params["webbank_vendor_key"]),
        is_local=is_local,
        queue_name=queue_name,
    )


def get_datadog_config() -> DataDogConfig:
    param_name = getenv("DATADOG_SSM_PARAM_NAME")
    params = get_ssm_values(param_name)

    return DataDogConfig(params["api_key"], params["app_key"])


def get_database_config() -> DBConfig:
    param_name = getenv("LAMBDA_DB_SSM_PARAM_NAME")
    params = get_ssm_values(param_name)

    database_name = getenv("DATABASE_NAME", params["database_name"])
    host = getenv("DATABASE_HOST", params["host"])
    username = getenv("DATABASE_USER", params["username"])
    password = getenv("DATABASE_PASSWORD", params["password"])

    driver = getenv("PYODBC_DRIVER", "{ODBC Driver 17 for SQL Server}")

    return DBConfig(database_name, host, username, password, driver)


def get_dropzone_config() -> DropzoneConfig:
    ppp_config = get_ppp_config()

    dz_path = getenv("DROPZONE_PATH", ppp_config.dropzone_path)
    dz_host = getenv("DROPZONE_HOST", ppp_config.dropzone_host)
    dz_port = getenv("DROPZONE_PORT", ppp_config.dropzone_port)
    if dz_port is not None:
        dz_port = int(dz_port)
    else:
        raise Exception("Missing DropZone PORT value")
    dz_user = getenv("DROPZONE_USER", ppp_config.dropzone_user)
    dz_pass = getenv("DROPZONE_PASSWORD", ppp_config.dropzone_password)

    return DropzoneConfig(dz_path, dz_host, dz_port, dz_user, dz_pass)
