import pandas as pd
import json
import yaml
from ecommerce.operations.common import AbstractOperation
from typing import Any, Dict, Optional


class WriteOperation(AbstractOperation):
    def __init__(self, path, data_format, data, mode="w", **kwargs):
        """
        Initialize the WriteOperation class with the required parameters.
        :param path: Path to the file where data should be written.
        :param data_format: Format of the data to write ('csv', 'parquet', 'yaml', 'json', 'txt').
        :param data: Data to be written (pandas DataFrame for 'csv' and 'parquet',
                                 dictionary for 'yaml' and 'json', and string for 'txt').
        :param mode: Writing mode ('w' for text, including JSON and YAML; 'wb' for binary, like Parquet).
        :param kwargs: Additional arguments to pass to the writing function.
        """
        self.path = path
        self.data_format = data_format
        self.data = data
        self.mode = mode
        self.kwargs = kwargs

    def execute(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> Any:
        """
        Write the data to a file in the specified format.
        """
        if self.data_format == "csv" or self.data_format == "parquet":
            self._write_dataframe()
        elif self.data_format == "yaml" or self.data_format == "json":
            self._write_dict()
        elif self.data_format == "txt":
            self._write_string()
        else:
            raise ValueError(f"Unsupported format: {self.data_format}")

    def _write_dataframe(self):
        """
        Write pandas DataFrame to either 'csv' or 'parquet'.
        """
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame for 'csv' or 'parquet' format.")

        if self.data_format == "csv":
            self.data.to_csv(self.path, **self.kwargs)
        elif self.data_format == "parquet":
            self.data.to_parquet(self.path, **self.kwargs)

    def _write_dict(self):
        """
        Write dictionary to either 'yaml' or 'json'.
        """
        if not isinstance(self.data, dict):
            raise ValueError("Data must be a dictionary for 'yaml' or 'json' format.")

        with open(self.path, self.mode) as file:
            if self.data_format == "yaml":
                yaml.dump(self.data, file, **self.kwargs)
            elif self.data_format == "json":
                json.dump(self.data, file, **self.kwargs)

    def _write_string(self):
        """
        Write a string to a file.
        """
        if not isinstance(self.data, str):
            raise ValueError("Data must be a string for 'txt' format.")

        with open(self.path, self.mode) as file:
            file.write(self.data)
