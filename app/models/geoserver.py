from pydantic import BaseModel


class Workspace_Response(BaseModel):
    name: str
    dataStore: str
    coverageStores: str
    wmsStores: str
