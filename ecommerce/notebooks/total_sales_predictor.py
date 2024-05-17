import optuna
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class TotalSalesPredictor:
    def __init__(self, train_df, val_df, test_df):
        self.train_df = train_df.copy()
        self.val_df = val_df.copy()
        self.test_df = test_df.copy()
        self.model = None

    def preprocess_data(self, df):
        df = df.copy()  # Ensure we are working on a copy to avoid warnings

        # Ensure the 'date' column is datetime type
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Check if there are any NaT values after conversion
        if df['date'].isnull().any():
            raise ValueError("NaT values found in 'date' column after conversion. Please check the input data.")

        # Ensure the 'date' column is of datetime type
        if df['date'].dtype != 'datetime64[ns]':
            raise ValueError('Date conversion failed. Date column is not of type datetime64[ns].')

        # Extract the day of the week
        df['day_of_week'] = df['date'].dt.dayofweek

        # Prepare feature matrix X and target vector y
        X = df.drop(['TotalSalesAmountInEuro', 'product_day_id', 'date'], axis=1)
        y = df['TotalSalesAmountInEuro']

        return X, y

    def objective(self, trial, X_train, y_train):
        pipeline = Pipeline([('scaler', StandardScaler()), ('regressor', RandomForestRegressor(random_state=42))])

        param_grid = {
            'regressor__n_estimators': trial.suggest_int('regressor__n_estimators', 50, 200),
            'regressor__max_depth': trial.suggest_int('regressor__max_depth', 10, 30),
            'regressor__min_samples_split': trial.suggest_int('regressor__min_samples_split', 2, 10),
            'regressor__min_samples_leaf': trial.suggest_int('regressor__min_samples_leaf', 1, 4),
        }

        pipeline.set_params(**param_grid)
        n_splits = 5
        cv_results = []

        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

        for train_index, val_index in kf.split(X_train):
            X_t, X_v = X_train.iloc[train_index], X_train.iloc[val_index]
            y_t, y_v = y_train.iloc[train_index], y_train.iloc[val_index]
            pipeline.fit(X_t, y_t)
            y_pred = pipeline.predict(X_v)
            rmse = mean_squared_error(y_v, y_pred, squared=False)
            cv_results.append(rmse)

        return sum(cv_results) / n_splits

    def hyperparameter_optimization(self, X_train, y_train):
        study = optuna.create_study(direction='minimize')
        study.optimize(lambda trial: self.objective(trial, X_train, y_train), n_trials=50)

        best_params = study.best_params
        best_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            (
                'regressor',
                RandomForestRegressor(
                    n_estimators=best_params['regressor__n_estimators'],
                    max_depth=best_params['regressor__max_depth'],
                    min_samples_split=best_params['regressor__min_samples_split'],
                    min_samples_leaf=best_params['regressor__min_samples_leaf'],
                    random_state=42,
                ),
            ),
        ])

        best_pipeline.fit(X_train, y_train)
        return best_pipeline

    def train_model(self):
        # Preprocess the data
        X_train, y_train = self.preprocess_data(self.train_df)
        X_val, y_val = self.preprocess_data(self.val_df)

        # Hyperparameter optimization
        self.model = self.hyperparameter_optimization(X_train, y_train)

        # Evaluate the model
        y_pred = self.model.predict(X_val)
        rmse = mean_squared_error(y_val, y_pred, squared=False)
        print(f'Validation RMSE: {rmse}')

    def predict(self):
        # Preprocess the test data
        X_test, _ = self.preprocess_data(self.test_df)

        # Predict using the trained model
        predictions = self.model.predict(X_test)

        return predictions
