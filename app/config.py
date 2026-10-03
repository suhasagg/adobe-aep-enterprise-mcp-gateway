from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url:str="postgresql+asyncpg://postgres:postgres@localhost:5432/mcp"
    redis_url:str="redis://localhost:6379/0"
    adobe_client_id:str=""
    adobe_client_secret:str=""
    adobe_scopes:str=""
    adobe_org_id:str=""
    adobe_sandbox_name:str="prod"
    adobe_ims_token_url:str="https://ims-na1.adobelogin.com/ims/token/v3"
    adobe_platform_base_url:str="https://platform.adobe.io"
    gateway_api_key:str="change-me"
    environment:str="local"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
