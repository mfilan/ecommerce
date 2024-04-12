from ecommerce.operations.base.read import ReadOperation
import ecommerce.configs.columns as c
from typing import Any, Dict, Optional


class ReadCriteoSearchData(ReadOperation):
    @property
    def data_types(self):
        return {
            c.SALE: "int64",
            c.SALES_AMOUNT_IN_EURO: "string",
            c.TIME_DELAY_FOR_CONVERSION: "string",
            c.CLICK_TIMESTAMP: "int64",
            c.NB_CLICKS_1WEEK: "string",
            c.PRODUCT_PRICE: "string",
            c.PRODUCT_AGE_GROUP: "string",
            c.DEVICE_TYPE: "string",
            c.AUDIENCE_ID: "string",
            c.PRODUCT_GENDER: "string",
            c.PRODUCT_BRAND: "string",
            c.PRODUCT_CATEGORY_1: "string",
            c.PRODUCT_CATEGORY_2: "string",
            c.PRODUCT_CATEGORY_3: "string",
            c.PRODUCT_CATEGORY_4: "string",
            c.PRODUCT_CATEGORY_5: "string",
            c.PRODUCT_CATEGORY_6: "string",
            c.PRODUCT_CATEGORY_7: "string",
            c.PRODUCT_COUNTRY: "string",
            c.PRODUCT_ID: "string",
            c.PRODUCT_TITLE: "string",
            c.PARTNER_ID: "string",
            c.USER_ID: "string",
        }

    def execute(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> Any:
        file_specific_kwargs = {"names": list(self.data_types.keys()), "dtype": self.data_types}
        file_specific_kwargs.update(self.kwargs)
        data = self._read_strategy(self.format, file_specific_kwargs)(self.path)
        return data
