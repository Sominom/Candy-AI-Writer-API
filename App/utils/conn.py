from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.orm import declarative_base # type: ignore

import urllib
from App.data.settings import Settings


settings = Settings.get_instance()
mysql_config = settings.mysql_config


Engine = create_engine(f"mysql+pymysql://{mysql_config['user']}:{urllib.parse.quote_plus(mysql_config['password'])}@{mysql_config['host']}/{mysql_config['database']}",
                       pool_pre_ping=True)
Session = sessionmaker(bind=Engine)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
