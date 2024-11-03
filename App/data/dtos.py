from pydantic import BaseModel  # type: ignore


class DaysDTO(BaseModel):
    days: int


class DomainCountDTO(BaseModel):
    count: int


class DomainDTO(BaseModel):
    domain: str


class StatusDTO(BaseModel):
    status: int


class CreditsDTO(BaseModel):
    credits: int


class OpenAIRequestDTO(BaseModel):
    prompt: str
    reference: str = ""


class APISubscriptionResponse(BaseModel):
    message: str
    subscribed: bool


class DomainListResponse(BaseModel):
    message: str
    domain_list: list


class CreditsResponse(BaseModel):
    message: str
    credits: int


class ExpirationDateResponse(BaseModel):
    message: str
    expiration_date: str


class ApiKeyResponse(BaseModel):
    api_key: str
    message: str


class SuccessMessageResponse(BaseModel):
    message: str
