from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    postgres_user: str = "rag_user"
    postgres_password: str = "rag_password"
    postgres_db: str = "rag_db"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    
    provider: str = "gigachat"
    deepseek_api_key: Optional[str] = None
    giga_chat_auth_key: Optional[str] = None
    giga_chat_model: str = "GigaChat-2"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    yandex_gpt_folder_id: Optional[str] = None
    yandex_gpt_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    search_limit: int = 7
    min_similarity: float = 0.4
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()

# Логирование загруженных настроек
print("=" * 60)
print("RAG_SDK CONFIG - Settings loaded:")
print(f"PROVIDER: {settings.provider}")
print(f"POSTGRES_HOST: {settings.postgres_host}")
print(f"POSTGRES_PORT: {settings.postgres_port}")
print(f"POSTGRES_DB: {settings.postgres_db}")
print(f"GIGA_CHAT_AUTH_KEY: {'SET' if settings.giga_chat_auth_key else 'NOT SET'}")
print(f"GIGA_CHAT_MODEL: {settings.giga_chat_model}")
print(f"OLLAMA_HOST: {settings.ollama_host}")
print(f"OLLAMA_MODEL: {settings.ollama_model}")
print(f"OPENAI_API_KEY: {'SET' if settings.openai_api_key else 'NOT SET'}")
print(f"OPENAI_MODEL: {settings.openai_model}")
print(f"EMBEDDING_MODEL: {settings.embedding_model}")
print(f"SEARCH_LIMIT: {settings.search_limit}")
print(f"MIN_SIMILARITY: {settings.min_similarity}")
print("=" * 60)

