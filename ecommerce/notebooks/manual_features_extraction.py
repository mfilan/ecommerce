import argparse

import pandas as pd

from get_data import get_df_from_gdrive

# Constants
PRODUCT_IDENTIFYING_COLUMNS = ['product_id', "product_brand", 'product_age_group', 'product_gender',
                               'product_category_1', 'product_category_2', 'product_category_3',
                               'product_category_4', 'product_category_5', 'product_category_6',
                               'product_category_7', "product_title"]
PERFORMANCE_IDENTIFYING_COLUMNS = ["date", "unique_product_id", "SalesAmountInEuro", "product_price", "device_type",
                                   "audience_id"]
TEMP_MAPPING = {'"-1"': 0.0, -1.0: 0.0, '-1.0': 0.0, "-1": 0.0}
TARGET_VARIABLE_NAME = "TotalSalesAmountInEuro"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--partner_gdownlink',
                        default="https://drive.google.com/uc?export=download&id=1xips2aDt0WisXUvrXHGoABhx7_CuoaEl",
                        help='From where to take the data')
    parser.add_argument('--timedelta_hours', type=int, default=14, help='How many hours back to take the data')
    parser.add_argument('--timedelta_days', type=int, default=0, help='How many days back to take the data')
    return parser.parse_args()


def get_df_from_gdown(gdownlink):
    return get_df_from_gdrive(gdownlink, 'tsv')


def add_dates_column(df, timedelta_hours):
    df['hour'] = df['click_timestamp'].apply(
        lambda x: str((pd.to_datetime(int(x), unit='s') + pd.Timedelta(hours=timedelta_hours)).time().hour))
    df['date'] = df['click_timestamp'].apply(
        lambda x: str((pd.to_datetime(int(x), unit='s') + pd.Timedelta(hours=timedelta_hours)).date()))
    return df


def get_product_df(partner_df):
    product = partner_df[PRODUCT_IDENTIFYING_COLUMNS]
    product_title_split = product['product_title'].str.split(expand=True).rename(
        columns=lambda x: f"product_title_part_{x}")
    product = pd.concat([product, product_title_split], axis=1).drop_duplicates(keep='first')
    product['unique_product_id'] = range(1, len(product) + 1)
    product['unique_product_id'] = product['unique_product_id'].astype('str')
    return product


def preprocess_performance_df(performance_df):
    {'"-1"': 0.0, -1.0: 0.0, '-1.0': 0.0, "-1": 0.0}
    performance_df.loc[:, 'SalesAmountInEuro'] = performance_df['SalesAmountInEuro'].replace(TEMP_MAPPING).apply(float)
    performance_df.loc[:, 'product_price'] = performance_df['product_price'].apply(float)
    return performance_df


def calculate_day_of_campaign(performance_df):
    the_first_day_date = pd.to_datetime(performance_df["date"]).min()
    performance_df.loc[:, 'dayofcampaign'] = performance_df['date'].apply(
        lambda x: (pd.to_datetime(x) - the_first_day_date).days)
    return performance_df


def create_test_validation_sets(performance_df):
    last_day = performance_df["dayofcampaign"].max()
    one_week_before_end = last_day - 7
    two_weeks_before_end = last_day - 14

    one_week_before_end_mask = performance_df["dayofcampaign"] > one_week_before_end
    one_week_before_last_week_mask = (performance_df["dayofcampaign"] > two_weeks_before_end) & (
            performance_df["dayofcampaign"] <= one_week_before_end)
    two_weeks_before_end_mask = performance_df["dayofcampaign"] > two_weeks_before_end

    return two_weeks_before_end_mask, one_week_before_last_week_mask, one_week_before_end_mask


def generate_product_sales_df(performance_df):
    # Aggregate sales and clicks by product and date
    product_sales = performance_df.groupby(["date", "unique_product_id"]).agg(
        TotalSalesAmountInEuro=pd.NamedAgg(column="SalesAmountInEuro", aggfunc="sum"),
        NumberOfClicks=pd.NamedAgg(column="SalesAmountInEuro", aggfunc="count")
    ).reset_index()

    # Generate unique IDs for product-day combinations
    product_sales['product_day_id'] = product_sales['unique_product_id'] + "_" + product_sales['date'].astype('str')
    product_sales['product_day_index'] = range(1, len(product_sales) + 1)

    return product_sales


def calculate_day_of_campaign_for_all(unique_dates):
    the_first_day_date = pd.to_datetime(unique_dates).min()
    dayofcampaign = {date: (pd.to_datetime(date) - the_first_day_date).days for date in unique_dates}
    return dayofcampaign


def merge_with_zeros_and_campaign_info(product_sales, unique_product_ids, unique_dates, dayofcampaign):
    # Creating a complete grid of product-date combinations to include days with zero sales
    all_combinations = pd.MultiIndex.from_product([unique_product_ids, unique_dates],
                                                  names=['unique_product_id', 'date']).to_frame(index=False)

    # Add dayofcampaign to all_combinations
    all_combinations['dayofcampaign'] = all_combinations['date'].map(dayofcampaign)

    product_sales_with_zeros = pd.merge(all_combinations, product_sales, on=["unique_product_id", "date"], how="left")
    product_sales_with_zeros.fillna({'TotalSalesAmountInEuro': 0, 'NumberOfClicks': 0}, inplace=True)

    # Assign a new product_day_index to each row in the DataFrame
    product_sales_with_zeros['product_day_index'] = range(1, len(product_sales_with_zeros) + 1)

    return product_sales_with_zeros


def save_to_parquet(df, file_name):
    df.to_parquet(f"{file_name}.parquet", index=False)


def main():
    args = parse_args()

    partner_df = get_df_from_gdown(args.partner_gdownlink)
    partner_df = add_dates_column(partner_df, args.timedelta_hours)
    product_df = get_product_df(partner_df)

    partial_df = pd.merge(partner_df, product_df, on=PRODUCT_IDENTIFYING_COLUMNS)
    performance_df = preprocess_performance_df(partial_df[PERFORMANCE_IDENTIFYING_COLUMNS])
    performance_df = calculate_day_of_campaign(performance_df)

    unique_product_ids = product_df['unique_product_id'].unique()
    unique_dates = performance_df['date'].unique()

    dayofcampaign = calculate_day_of_campaign_for_all(unique_dates)
    product_sales_df = generate_product_sales_df(performance_df)

    product_sales_with_zeros_df = merge_with_zeros_and_campaign_info(product_sales_df, unique_product_ids, unique_dates,
                                                                     dayofcampaign)

    # Save the final DataFrame to a Parquet file
    save_to_parquet(product_sales_with_zeros_df, "manual_features")

    print("final_shape:", product_sales_with_zeros_df.shape)
    save_to_parquet(product_df, "product_data")
    save_to_parquet(performance_df, "performance_data")


if __name__ == '__main__':
    main()
