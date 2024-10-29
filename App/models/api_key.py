from sqlalchemy import Column, String, Integer, Date, Boolean  
from App.utils.conn import Base  
from datetime import datetime
import pytz

class APIKey(Base):  
    __tablename__ = 'api_keys'  

    api_key = Column(String(255), primary_key=True)  
    expiration_date = Column(Date)  
    domain_list = Column(String(512), default='')  
    max_domain_count = Column(Integer)  
    credits = Column(Integer)  
    user_id = Column(String(255))  
    created_date = Column(Date)  
    is_subscribed = Column(Boolean)  

    def __init__(self, api_key, expiration_date=None, domain_list=None, max_domain_count=1, credits=0, user_id=None, is_subscribed=0):  
        self.api_key = api_key  
        self.expiration_date = expiration_date  
        self.domain_list = domain_list or ''  
        self.max_domain_count = max_domain_count  
        self.credits = credits  
        self.user_id = user_id  
        self.is_subscribed = is_subscribed  
        if self.created_date is None:  
            self.created_date = datetime.now(pytz.utc).date()  

    def is_expired(self):  
        if self.expiration_date is None:  
            return False  
        current_date = datetime.now(pytz.utc).date()  
        return current_date > self.expiration_date  