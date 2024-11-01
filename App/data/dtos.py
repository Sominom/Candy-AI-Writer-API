from pydantic import BaseModel #type: ignore

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