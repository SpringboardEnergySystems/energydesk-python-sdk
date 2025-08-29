import logging
import pandas as pd
from energydeskapi.sdk.api_connection import ApiConnection
from dataclasses import dataclass
import json
logger = logging.getLogger(__name__)


@dataclass
class Context:
    description: str = None
    context_url: str = None


#  Change
class CopilotApi:
    """Class for Copilot Access to EnergyDesk API
    """
    @staticmethod
    def get_available_contexts(api_connection: ApiConnection, parameters: dict={})->list[Context]:
        data = api_connection.exec_get_url('/ai/contexts/', parameters)
        print(json.dumps(data, indent=2))
        all_contexts = []
        if data:
            for endp in data['contexts']:

                ctx=Context(endp['description'], endp['context_url'])
                all_contexts.append(ctx)
            return all_contexts
        return []
