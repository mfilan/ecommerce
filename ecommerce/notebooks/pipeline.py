from ecommerce.operations.base.read import ReadOperation
from ecommerce.operations.custom.data_splitter import SplitDataOperation
from ecommerce.operations.custom.feature_extractor import FeatureExtractionOperation
from metaflow import FlowSpec, step, Parameter
from total_sales_predictor import TotalSalesPredictor


class SalesPredictionFlow(FlowSpec):
    
    # Define parameters
    data_path = Parameter('data_path', 
                          default="./data/standardized/df_source.parquet/partner_id=E68029E9BCE099A60571AF757CBB6A08",
                          help="Path to the data file")
    validation_days = Parameter('validation_days', 
                                default=7, 
                                help="Number of days for validation set")
    test_days = Parameter('test_days', 
                          default=7, 
                          help="Number of days for test set")

    @step
    def start(self):
        """
        Starting point of the flow.
        """
        print("Flow started!")
        self.next(self.read_data)

    @step
    def read_data(self):
        """
        Read data from the specified path.
        """
        self.data = ReadOperation(path=self.data_path, object_format='parquet').execute()
        print("Data read successfully.")
        self.next(self.feature_extraction)

    @step
    def feature_extraction(self):
        """
        Perform feature extraction on the raw data.
        """
        self.df_features = FeatureExtractionOperation().execute(df=self.data)
        print("Feature extraction completed.")
        self.next(self.split_data)

    @step
    def split_data(self):
        """
        Split the data into training, validation, and test sets.
        """
        self.df_train, self.df_validation, self.df_test = SplitDataOperation().execute(
            df=self.df_features, 
            validation_days=self.validation_days, 
            test_days=self.test_days
        )
        print("Data splitting completed.")
        self.next(self.train_model)

    @step
    def train_model(self):
        """
        Train the sales prediction model.
        """
        self.predictor = TotalSalesPredictor(self.df_train, self.df_validation, self.df_test)
        self.predictor.train_model()
        print("Model training completed.")
        self.next(self.predict)

    @step
    def predict(self):
        """
        Make predictions on the test dataset.
        """
        self.predictions = self.predictor.predict()
        print("Predictions made successfully.")
        self.next(self.end)

    @step
    def end(self):
        """
        End of the flow.
        """
        print("Flow finished successfully.")
        print(f"Predictions: {self.predictions}")


if __name__ == "__main__":
    SalesPredictionFlow()