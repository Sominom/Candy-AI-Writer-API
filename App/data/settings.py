import json


class Settings:
    _instance = None

    def __init__(
        self,
        secret=None,
        api_key_prefix=None,
        mysql_config=None,
        schema=None,
        openai_api_key=None,
        openai_chat_model=None,
    ):
        self._secret = secret
        self._api_key_prefix = api_key_prefix
        self._mysql_config = mysql_config
        self._schema = schema
        self._openai_api_key = openai_api_key
        self._openai_chat_model = openai_chat_model

    @property
    def secret(self):
        return self._secret

    @property
    def api_key_prefix(self):
        return self._api_key_prefix

    @property
    def mysql_config(self):
        return self._mysql_config

    @property
    def schema(self):
        return self._schema

    @property
    def openai_api_key(self):
        return self._openai_api_key

    @property
    def openai_chat_model(self):
        return self._openai_chat_model

    @staticmethod
    def load_config(file_path="settings.json"):
        try:
            with open(file_path, "r") as file:
                config = json.load(file)
                return config
        except FileNotFoundError:
            print(f"{file_path}를 찾을 수 없습니다.")
            return None
        except json.JSONDecodeError as e:
            print(f"올바른 JSON 형식이 아닙니다. {e}")
            return None

    @classmethod
    def initialize(cls):
        config = cls.load_config()
        if config:
            return cls(
                secret=config.get("secret"),
                api_key_prefix=config.get("api_key_prefix"),
                mysql_config=config.get("mysql_config"),
                schema=config.get("schema"),
                openai_api_key=config.get("openai_api_key"),
                openai_chat_model=config.get("openai_chat_model")
            )
        return cls()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.initialize()
        return cls._instance
