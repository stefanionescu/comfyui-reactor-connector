"""Index reviewed model capabilities by model key and provider connection."""

from .state.models import ModelDefinition
from .config.models import MODEL_IDENTITIES

MODELS: dict[str, ModelDefinition] = {name: ModelDefinition(**record) for name, record in MODEL_IDENTITIES.items()}
MODELS_BY_CONNECTION: dict[str, ModelDefinition] = {
    definition.connection_name: definition for definition in MODELS.values()
}
