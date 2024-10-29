from pydantic import BaseModel  # type: ignore


class RequestData(BaseModel):
    """
    Attributes:
        api_key (str)
    """

    api_key: str


class RequestDataStr(BaseModel):
    """
    Attributes:
        api_key (str)
        request (str)
    """

    api_key: str
    request: str


class OpenAiRequestData(BaseModel):

    api_key: str
    reference: str
    prompt: str


class AdminRequestDataStr(BaseModel):
    """
    Attributes:
        api_key (str)
        secret (str): 관리자 비밀번호
        str (str)
    """

    api_key: str
    secret: str
    str: str


class AdminRequestDataInt(BaseModel):
    """
    Attributes:
        api_key (str)
        secret (str): 관리자 비밀번호
        int (int)
    """

    api_key: str
    secret: str
    int: int


class GenerateApiKeyData(BaseModel):
    """
    Attributes:
        days (int)
        secret (str): 관리자 비밀번호
    """

    days: int
    secret: str


class ExtendApiKeyData(BaseModel):
    """
    Attributes:
        days (int)
        secret (str): 관리자 비밀번호
        api_key (str)
    """

    days: int
    secret: str
    api_key: str


class DeleteApiKeyData(BaseModel):
    """
    Attributes:
        secret (str): 관리자 비밀번호
        api_key (str)
    """

    secret: str
    api_key: str
