"""
This module implements feature extraction operations for ecommerce data processing, focusing on transforming raw event
data into structured features suitable for analysis or machine learning models. The features extracted include date
and time components, product-specific attributes, and sales metrics. The operations are encapsulated within a class
that extends from an abstract base class, ensuring that it fits into a larger data processing pipeline with standardized
interfaces.
"""
from functools import partial
from typing import Optional

import pandas as pd

import ecommerce.configs.columns as c
from ecommerce.operations.common import AbstractOperation


class FeatureExtractionOperation(AbstractOperation):
    """
    A class to perform feature extraction on ecommerce data, extending the AbstractOperation base class.

    Methods include extraction of date and time features, creation of a detailed product DataFrame, and the
    processing of monetary attributes. This class is intended to be used within a data processing pipeline where
    raw ecommerce data is transformed into a format ready for analysis or predictive modeling.
    """
    def apply_extract_date_features(self, row: pd.Series, timedelta: dict) -> dict:
        """
        Extracts date and time features from a timestamp.

        Args:
            row (pd.Series): A row of DataFrame.
            timedelta (dict): A dictionary specifying the time adjustments to apply.

        Returns:
            dict: A dictionary containing extracted features such as hour, date, month, and week of the year.
        """
        click_timestamp = row[c.CLICK_TIMESTAMP]
        adjusted_timestamp = pd.to_datetime(int(click_timestamp), unit="s") + pd.Timedelta(**timedelta)
        return {
            c.HOUR: adjusted_timestamp.time().hour,
            c.DATE: adjusted_timestamp.date(),
            c.MONTH: adjusted_timestamp.date().month,
            c.WEEK: adjusted_timestamp.week,
        }

    def add_date_features(self, df: pd.DataFrame, timedelta_kwargs: Optional[dict] = None) -> pd.DataFrame:
        """
        Adds date-related features to a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.
            timedelta_kwargs (Optional[dict]): Parameters to define the timedelta adjustments.

        Returns:
            pd.DataFrame: The DataFrame with new date-related features added.
        """
        if timedelta_kwargs is None:
            timedelta_kwargs = {"hours": 1}
        partial_func = partial(self.apply_extract_date_features, timedelta=timedelta_kwargs)
        df[[c.HOUR, c.DATE, c.MONTH, c.WEEK]] = df.apply(partial_func, axis=1, result_type="expand")
        return df

    @property
    def product_columns(self):
        """
        Property to define the columns related to product details.

        Note: Primary Key (PK) needs better definition.

        Returns:
            list: A list of column names that define product attributes.
        """
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
        """
        Creates a DataFrame focused on product details by expanding product titles and assigning unique product IDs.

        Args:
            df (pd.DataFrame): The input DataFrame containing product data.

        Returns:
            pd.DataFrame: A DataFrame containing detailed product attributes including split product titles.
        """
        df_product = df[self.product_columns].drop_duplicates()
        df_titles = df_product[c.PRODUCT_TITLE].str.split(expand=True).add_prefix("product_title_part_")
        df_product = df_product.join(df_titles)
        df_product[c.UNIQUE_PRODUCT_ID] = range(1, len(df_product) + 1)
        df_product[c.UNIQUE_PRODUCT_ID] = df_product[c.UNIQUE_PRODUCT_ID].astype(str)
        return df_product

    def process_money_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes monetary features in the DataFrame, ensuring that sales and price data are handled as floats and
         cleaned appropriately.

        Args:
            df (pd.DataFrame): The DataFrame to process.

        Returns:
            pd.DataFrame: The DataFrame with monetary features cleaned and processed.
        """
        df.loc[:, c.SALES_AMOUNT_IN_EURO] = df[c.SALES_AMOUNT_IN_EURO].astype(float).apply(lambda x: max(x, 0))
        df.loc[:, c.PRODUCT_PRICE] = df[c.PRODUCT_PRICE].apply(float)
        return df

    def calculate_day_of_campaign(self, df):
        """
        Calculates the day of the campaign for each date in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing date information.

        Returns:
            pd.DataFrame: The DataFrame with an additional column for the campaign day number.
        """
        the_first_day_date = pd.to_datetime(df[c.DATE]).min()
        df.loc[:, c.DAY_OF_CAMPAIGN] = df[c.DATE].apply(lambda x: (pd.to_datetime(x) - the_first_day_date).days)
        return df

    def generate_product_sales_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates a DataFrame aggregating sales amounts and click counts per product and per day.

        Args:
            df (pd.DataFrame): The DataFrame containing sales and product information.

        Returns:
            pd.DataFrame: An aggregated DataFrame with total sales amount and number of clicks for each product per day.
        """
        product_sales = (
            df.groupby([c.DATE, c.UNIQUE_PRODUCT_ID])
            .agg(
                TotalSalesAmountInEuro=pd.NamedAgg(column=c.SALES_AMOUNT_IN_EURO, aggfunc="sum"),
                NumberOfClicks=pd.NamedAgg(column=c.SALES_AMOUNT_IN_EURO, aggfunc="count"),
            )
            .reset_index()
        )

        product_sales[c.PRODUCT_DAY_ID] = product_sales[c.UNIQUE_PRODUCT_ID] + "_" + product_sales[c.DATE].astype(str)
        product_sales[c.PRODUCT_DAY_INDEX] = range(1, len(product_sales) + 1)

        return product_sales

    def calculate_day_of_campaign_for_all(self, unique_dates: list) -> dict:
        """
        Calculates the campaign day number for each unique date provided.

        Args:
            unique_dates (list): A list of dates to calculate campaign days for.

        Returns:
            dict: A dictionary mapping each date to its respective day number in the campaign.
        """
        the_first_day_date = pd.to_datetime(unique_dates).min()
        day_of_campaign = {date: (pd.to_datetime(date) - the_first_day_date).days for date in unique_dates}
        return day_of_campaign

    def merge_with_zeros_and_campaign_info(
        self, product_sales: pd.DataFrame, unique_product_ids: list, unique_dates: list, day_of_campaign: dict
    ) -> pd.DataFrame:
        """
        Merges the product sales data with a complete grid of product-date combinations, filling missing days with zero
         sales and clicks.

        Args:
            product_sales (pd.DataFrame): DataFrame with sales data.
            unique_product_ids (list): A list of unique product IDs.
            unique_dates (list): A list of unique dates.
            day_of_campaign (dict): A dictionary mapping dates to campaign days.

        Returns:
            pd.DataFrame: A DataFrame including all combinations of product and date, enriched with sales data and
            zero-filled where no data exists.
        """

        all_combinations = pd.MultiIndex.from_product(
            [unique_product_ids, unique_dates], names=[c.UNIQUE_PRODUCT_ID, c.DATE]
        ).to_frame(index=False)

        all_combinations[c.DAY_OF_CAMPAIGN] = all_combinations[c.DATE].map(day_of_campaign)

        product_sales_with_zeros = pd.merge(
            all_combinations, product_sales, on=[c.UNIQUE_PRODUCT_ID, c.DATE], how="left"
        )
        product_sales_with_zeros.fillna({c.TOTAL_SALES_AMOUNT_IN_EURO: 0, c.NUMBER_OF_CLICKS: 0}, inplace=True)

        product_sales_with_zeros[c.PRODUCT_DAY_INDEX] = range(1, len(product_sales_with_zeros) + 1)

        return product_sales_with_zeros

    def execute(self, df: pd.DataFrame, timedelta_kwargs: Optional[dict] = None) -> pd.DataFrame:
        """
        Execute the feature extraction operations on the provided DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.
            timedelta_kwargs (Optional[dict]): Optional arguments for time delta adjustments.

        Returns:
            pd.DataFrame: The DataFrame enriched with extracted features and transformed data.
        """
        # Add date-related features
        df = self.add_date_features(df, timedelta_kwargs)

        # Create product dataframe with additional title parts and unique product IDs
        df_product = self.create_product_dataframe(df)
        df = pd.merge(df_product, df, on=self.product_columns)

        # Process monetary features to ensure they are handled correctly
        df = self.process_money_features(df)

        # Calculate the day of the campaign for each record
        df = self.calculate_day_of_campaign(df)

        # Generate product sales DataFrame with aggregated sales data
        product_sales_df = self.generate_product_sales_df(df)

        # Retrieve unique product IDs and dates for campaign mapping
        unique_product_ids = df[c.UNIQUE_PRODUCT_ID].unique()
        unique_dates = df[c.DATE].unique()

        # Calculate campaign days for all dates
        day_of_campaign = self.calculate_day_of_campaign_for_all(unique_dates)

        # Merge product sales data with zeros for missing sales and add campaign info
        final_df = self.merge_with_zeros_and_campaign_info(product_sales_df, unique_product_ids, unique_dates,
                                                           day_of_campaign)

        return final_df
