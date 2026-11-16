# Sarthak Nivesh - IPO Prediction Engine
# Machine Learning-based IPO performance prediction
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import os
import pickle
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from config import *


class IPOPredictionEngine:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.setup_models()
        self.load_models()
        print("🤖 IPO Prediction Engine initialized")

    def setup_models(self):
        """Setup machine learning models for IPO prediction."""
        self.models["performance_30d"] = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.models["performance_90d"] = GradientBoostingRegressor(
            n_estimators=100, max_depth=6, random_state=42
        )
        self.models["liquidity"] = RandomForestRegressor(
            n_estimators=50, max_depth=8, random_state=42
        )

        self.scalers["features"] = StandardScaler()
        self.label_encoders["sector"] = LabelEncoder()
        self.label_encoders["market_cap"] = LabelEncoder()

        print("✅ ML models initialized for IPO prediction")

    def prepare_training_data(self):
        """Prepare training data for IPO prediction models (real data only)."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.read_sql_query(
                """
                SELECT * FROM ipo_intelligence
                WHERE performance_30d IS NOT NULL
                  AND performance_90d IS NOT NULL
                  AND liquidity_score IS NOT NULL
                """,
                conn,
            )
            conn.close()

            if df.empty or len(df) < 10:
                print("⚠️ Not enough real IPO data to train models.")
                return None, None

            features = self.engineer_features(df)
            targets = {
                "performance_30d": df["performance_30d"].values,
                "performance_90d": df["performance_90d"].values,
                "liquidity": df["liquidity_score"].values,
            }

            return features, targets

        except Exception as e:
            print(f"❌ Error preparing training data: {str(e)}")
            return None, None

    def engineer_features(self, df):
        """Engineer features for IPO prediction."""
        features_df = df.copy()

        if "sector" in features_df.columns:
            if not hasattr(self.label_encoders["sector"], "classes_"):
                features_df["sector_encoded"] = self.label_encoders["sector"].fit_transform(
                    features_df["sector"].fillna("Unknown")
                )
            else:
                features_df["sector_encoded"] = self.label_encoders["sector"].transform(
                    features_df["sector"].fillna("Unknown")
                )

        if "market_cap_category" in features_df.columns:
            if not hasattr(self.label_encoders["market_cap"], "classes_"):
                features_df["market_cap_encoded"] = self.label_encoders["market_cap"].fit_transform(
                    features_df["market_cap_category"].fillna("Unknown")
                )
            else:
                features_df["market_cap_encoded"] = self.label_encoders["market_cap"].transform(
                    features_df["market_cap_category"].fillna("Unknown")
                )

        features_df["log_issue_size"] = np.log(features_df["issue_size_crores"].fillna(0) + 1)
        features_df["log_subscription"] = np.log(features_df["subscription_times"].fillna(0) + 1)
        features_df["price_to_size_ratio"] = (
            features_df["issue_price"].fillna(0) / features_df["issue_size_crores"].replace(0, np.nan)
        ).fillna(0)

        feature_columns = [
            "issue_price",
            "issue_size_crores",
            "subscription_times",
            "sector_encoded",
            "market_cap_encoded",
            "log_issue_size",
            "log_subscription",
            "price_to_size_ratio",
        ]
        available = [col for col in feature_columns if col in features_df.columns]
        return features_df[available].fillna(0)

    def train_prediction_models(self):
        """Train IPO prediction models."""
        try:
            features, targets = self.prepare_training_data()
            if features is None or targets is None:
                return None

            features_scaled = self.scalers["features"].fit_transform(features)
            model_performance = {}

            for target_name, target_values in targets.items():
                X_train, X_test, y_train, y_test = train_test_split(
                    features_scaled, target_values, test_size=0.2, random_state=42
                )
                model = self.models[target_name]
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                model_performance[target_name] = {
                    "mae": round(mae, 3),
                    "r2_score": round(r2, 3),
                    "accuracy": round(max(0, r2 * 100), 1),
                }

            self.save_models()
            return model_performance

        except Exception as e:
            print(f"❌ Error training models: {str(e)}")
            return None

    def predict_ipo_performance(self, ipo_features):
        """Predict IPO performance using trained models."""
        try:
            if not self.models:
                return None
            if not hasattr(self.scalers["features"], "mean_"):
                return None

            features_df = pd.DataFrame([ipo_features])
            engineered_features = self.engineer_features(features_df)
            features_scaled = self.scalers["features"].transform(engineered_features)

            predictions = {}
            for target_name, model in self.models.items():
                prediction = model.predict(features_scaled)[0]
                predictions[target_name] = round(float(prediction), 2)

            return predictions

        except Exception as e:
            print(f"❌ Error predicting IPO performance: {str(e)}")
            return None

    def save_models(self):
        try:
            os.makedirs("models", exist_ok=True)

            for name, model in self.models.items():
                with open(f"models/ipo_{name}_model.pkl", "wb") as f:
                    pickle.dump(model, f)

            with open("models/ipo_scaler.pkl", "wb") as f:
                pickle.dump(self.scalers["features"], f)

            for name, encoder in self.label_encoders.items():
                with open(f"models/ipo_{name}_encoder.pkl", "wb") as f:
                    pickle.dump(encoder, f)

            print("✅ IPO prediction models saved successfully")

        except Exception as e:
            print(f"❌ Error saving models: {str(e)}")

    def load_models(self):
        try:
            for name in list(self.models.keys()):
                model_path = f"models/ipo_{name}_model.pkl"
                if os.path.exists(model_path):
                    with open(model_path, "rb") as f:
                        self.models[name] = pickle.load(f)

            scaler_path = "models/ipo_scaler.pkl"
            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    self.scalers["features"] = pickle.load(f)

            for name in self.label_encoders.keys():
                encoder_path = f"models/ipo_{name}_encoder.pkl"
                if os.path.exists(encoder_path):
                    with open(encoder_path, "rb") as f:
                        self.label_encoders[name] = pickle.load(f)

            return True

        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            return False


if __name__ == "__main__":
    predictor = IPOPredictionEngine()
    metrics = predictor.train_prediction_models()
    if metrics:
        print(metrics)
