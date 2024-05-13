from functools import partial
from typing import Optional

import pandas as pd

import ecommerce.configs.columns as c
from ecommerce.operations.common import AbstractOperation
from typing import Any, Dict
import featuretools as ft

class FeatureSynthesisOperation(AbstractOperation):
	def execute(self, df_features: pd.DataFrame) -> Any:

		es = ft.EntitySet(id='entity_set')
		es.add_dataframe(dataframe_name="product_day", dataframe=df_features, index=c.PRODUCT_DAY_INDEX, time_index=c.DATE)
