from typing import List

import pandas as pd

import ecommerce.configs.columns as c
from ecommerce.operations.common import AbstractOperation


class SplitDataOperation(AbstractOperation):
    def execute(self, df: pd.DataFrame, validation_days: int, test_days: int) -> List[pd.DataFrame]:
        """Executes the operation."""
        max_date = df[c.DATE].max()
        df_test: pd.DataFrame = df[df[c.DATE] > max_date - pd.Timedelta(days=test_days)]
        df_validation: pd.DataFrame = df[
            (df[c.DATE] > max_date - pd.Timedelta(days=validation_days + test_days))
            & (df[c.DATE] < max_date - pd.Timedelta(days=test_days))
        ]
        df_train: pd.DataFrame = df[df[c.DATE] < max_date - pd.Timedelta(days=validation_days + test_days)]
        return [df_train, df_validation, df_test]
