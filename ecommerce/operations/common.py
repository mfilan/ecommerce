from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AbstractOperation(ABC):
    """Abstract class for all operations."""

    @abstractmethod
    def execute(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> Any:
        """Executes the operation."""
        pass
