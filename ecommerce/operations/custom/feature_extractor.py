from functools import partial
from typing import Any, Dict, Optional

import pandas as pd

import ecommerce.configs.columns as c
from ecommerce.operations.common import AbstractOperation


class FeatureExtractionOperation(AbstractOperation):
    def apply_extract_date_features(self, row: pd.Series, timedelta: dict) -> dict:
        click_timestamp = row[c.CLICK_TIMESTAMP]
        adjusted_timestamp = pd.to_datetime(int(click_timestamp), unit="s") + pd.Timedelta(**timedelta)
        return {
            c.HOUR: adjusted_timestamp.time().hour,
            c.DATE: adjusted_timestamp.date(),
            c.MONTH: adjusted_timestamp.date().month,
            c.WEEK: adjusted_timestamp.week,
        }

    def add_date_features(self, df: pd.DataFrame, timedelta_kwargs: Optional[dict] = None) -> pd.DataFrame:
        if timedelta_kwargs is None:
            timedelta_kwargs = {c.HOUR: 1}
        partial_func = partial(self.apply_extract_date_features, timedelta=timedelta_kwargs)
        df[[c.HOUR, c.DATE, c.MONTH, c.WEEK]] = df.apply(partial_func, axis=1, result_type="expand")
        return df

    @property
    def product_columns(self):  # fixme, PK should be defined better, 1:1 with product_id
        return [
            c.PRODUCT_ID,
            c.PRODUCT_BRAND,
            c.PRODUCT_AGE_GROUP,
            c.PRODUCT_GENDER,
            c.PRODUCT_CATEGORY_1,
            c.PRODUCT_CATEGORY_2,
            c.PRODUCT_CATEGORY_3,
            c.PRODUCT_CATEGORY_4,
            c.PRODUCT_CATEGORY_5,
            c.PRODUCT_CATEGORY_6,
            c.PRODUCT_CATEGORY_7,
            c.PRODUCT_TITLE,
        ]

    def create_product_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_product = df[self.product_columns].drop_duplicates()
        df_titles = df_product[c.PRODUCT_TITLE].str.split(expand=True).add_prefix("product_title_part_")
        df_product = df_product.join(df_titles)
        df_product[c.UNIQUE_PRODUCT_ID] = range(1, len(df_product) + 1)
        df_product[c.UNIQUE_PRODUCT_ID] = df_product[c.UNIQUE_PRODUCT_ID].astype(str)
        return df_product

    def execute(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> Any:
        raise NotImplementedError
