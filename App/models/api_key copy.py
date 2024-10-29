from sqlalchemy import Column, String, Integer, Date, Boolean  
from App.utils.conn import Base  
from datetime import datetime, timedelta  

class APIKey(Base):  
    __tablename__ = 'api_keys'  

    api_key = Column(String(255), primary_key=True)  
    expiration_date = Column(Date)  
    domain_list = Column(String(255))  
    max_domain_count = Column(Integer)  
    credits = Column(Integer)  
    user_id = Column(String(255))  
    created_date = Column(Date)  
    is_subscribed = Column(Boolean)  

    def __init__(self, api_key, expiration_date=None, domain_list=None, max_domain_count=1, credits=0, user_id=None, created_date=None, is_subscribed=0):  
        self.api_key = api_key  
        self.expiration_date = expiration_date  
        self.domain_list = domain_list  
        self.max_domain_count = max_domain_count  
        self.credits = credits  
        self.user_id = user_id  
        self.created_date = created_date  
        self.is_subscribed = is_subscribed  
        self.__set_created_date()  

    def is_expired(self):  
        if self.expiration_date is None:  
            return False  
        current_date_str = datetime.now().strftime('%Y-%m-%d')  
        current_date_obj = datetime.strptime(current_date_str, '%Y-%m-%d').date()  
        return current_date_obj > self.expiration_date  

    def set_expiration_date(self, days=14):  
        expiration_datetime = datetime.now() + timedelta(days=days)  
        self.expiration_date = expiration_datetime.date()  

    def add_credit(self, credit):  
        self.credits += credit  

    def subtract_credit(self, credit):  
        self.credits = max(self.credits - credit, 0)  

    def get_credits(self):  
        return self.credits  

    def get_max_domain_count(self):  
        return self.max_domain_count  

    def __set_created_date(self):  
        self.created_date = datetime.now().date()
