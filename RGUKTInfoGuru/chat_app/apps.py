from django.apps import AppConfig
from django.core.cache import cache
cache.clear()



class ChatAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_app'

    def ready(self):
        from .agent.agent_executor import AgentExecutor
        AgentExecutor()
        