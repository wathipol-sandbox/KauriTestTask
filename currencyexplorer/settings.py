from abc import ABC
from typing import Optional, ClassVar, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings, ABC):
    """API abstract settings class
        Declares all variables needed to run the application.
            To create a set of specific settings, you need to create a child class from this
                by initializing the required class attribute in it - CONFIG_ENVIRONMENT to refer to
                    this type by the name of the environment.
        
        CONFIG VARS:
        - DEBUG: bool - Fast-API debug mode.
        - API_AUTHENTICATION_TOKEN: str - Secret token for secure API endoint's.
        - WAIT_SCRAPER_WORKERS_TIMEOUT: float - time in seconds how long we wait before checking
                                                    worker status on application startup.
        - STOP_SCRAPER_WORKERS_TIMEOUT: float - time in seconds how long we wait after send stop
                                                    workers signal after aplication finish api process.
    """
    CONFIG_ENVIRONMENT: ClassVar[str]
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore')
    DEBUG: Optional[bool] = False
    API_AUTHENTICATION_TOKEN: str
    WAIT_SCRAPER_WORKERS_TIMEOUT: Optional[float] = 2
    STOP_SCRAPER_WORKERS_TIMEOUT: Optional[float] = 2
    DEFAULT_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT: Optional[float] = 1
    MAX_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT: Optional[float] = 60
    MIN_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT: Optional[float] = 0.1
    WEBSOCKET_UPDATER_CONNECTION_TIMEOUT_LIMIT: Optional[int] = 3000 # 50min

    @classmethod
    def get_environment_name(CLS):
        """ GET current config type refer env name """
        try:
            config_title = getattr(CLS, "CONFIG_ENVIRONMENT")
        except AttributeError:
            raise NotImplementedError
        else:
            return config_title


class DevelopementSettings(BaseConfig):
    CONFIG_ENVIRONMENT: ClassVar[str] = "DEV"
    DEBUG: bool = True


class ProductionSettings(BaseConfig):
    CONFIG_ENVIRONMENT: ClassVar[str] = "PROD"
    DEBUG: bool = False


class ConfigConstructorMapper:
    """ Make config loader object for specified config environment.
            Call this object for make ready for use API config object
                All passed kwargs will be used to initialize the settings class in the type constructor
    """

    # Make env_name:config_constructor refer dict
    CONFIG_MAPPING: ClassVar[Dict[str, BaseConfig]] = {
        config_type.get_environment_name():
            config_type for config_type in BaseConfig.__subclasses__() if hasattr(
                config_type, "CONFIG_ENVIRONMENT")
    }
    
    def __init__(self, environment_name: str) -> None:
        try:
            self.__CONSTRUCTOR = self.CONFIG_MAPPING[environment_name]
        except KeyError:
            raise NameError("{} config type not found".format(environment_name))
    
    @property
    def CONSTRUCTOR(self):
        return self.__CONSTRUCTOR

    def __call__(self, **settings_kwargs) -> BaseConfig:
        return self.CONSTRUCTOR(**settings_kwargs)
