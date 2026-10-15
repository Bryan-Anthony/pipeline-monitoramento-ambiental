from pydantic import BaseModel, ConfigDict, ValidationError


class ChannelContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    description: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    created_at: str
    updated_at: str

    last_entry_id: int | None = None


class FeedContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    entry_id: int
    created_at: str

    field1: float | None = None
    field2: float | None = None
    field3: float | None = None
    field4: float | None = None
    field5: float | None = None
    field6: float | None = None
    field7: float | None = None
    field8: float | None = None


class ApiResponseContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    channel: ChannelContract
    feeds: list[FeedContract]


def validar_data_contract(dados: dict) -> dict:
    """
    Valida a estrutura e os tipos dos dados da API.
    Retorna a resposta original para preservar
    o formato esperado pelo IngestionService.
    """

    contrato = ApiResponseContract.model_validate(dados)

    return dados
