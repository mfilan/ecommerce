import json
from collections.abc import Callable
from functools import partial
from typing import IO

import pandas as pd
import yaml

from ecommerce.operations.common import AbstractOperation
from typing import Any, Dict, Optional, Union


class ReadOperation(AbstractOperation):
    """Class responsible for reading data from various file formats.

    Supported formats are FCS, JSON, CSV, and GatingML.
    """

    def __init__(self, path: str, object_format: str, **kwargs) -> None:
        self.path = path
        self.format = object_format
        self.kwargs = kwargs

    @property
    def _supported_read_strategies(self) -> dict:
        """Returns a dictionary of supported read strategies.

        Returns:
            dict: Dictionary of supported read strategies.
        """
        return {
            "tsv": partial(pd.read_csv, sep="\t"),
            "json": json.load,
            "csv": pd.read_csv,
            "parquet": pd.read_parquet,
            "yaml": yaml.safe_load,  # Add support for reading YAML
        }

    def _read_strategy(self, object_format: str, kwargs: dict) -> Union[Callable[[IO[bytes]], Any], str]:
        """Returns the appropriate read strategy callable based on the input format.

        Parameters:
            object_format (str): String representing the format of the data source (e.g., "csv", "json").

        Returns:
            callable: Function suitable to read data from the specified format.

        Raises:
            ValueError: If the provided input format is not supported.
        """
        if object_format in self._supported_read_strategies:
            return partial(self._supported_read_strategies[object_format], **kwargs)

        raise ValueError(f"{object_format} is not supported!")

    def execute(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> Any:
        data = self._read_strategy(self.format, self.kwargs)(self.path)
        return data
