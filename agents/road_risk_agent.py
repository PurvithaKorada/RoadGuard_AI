
import os
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix


class RoadRiskAgent:
    """
    Analyzes historical accident and road feature data
    to assign risk scores to road segments.

    Uses RandomForestClassifier on demo/synthetic data.
    """

    FEATURES = [
        'length_km',
        'num_accidents',
        'num_fatal_accidents',
        'num_injuries',
        'avg_speed_kmph',
        'num_potholes',
        'night_lighting_score',
        'road_type_enc',
        'num_lanes'
    ]

    ROAD_TYPE_MAPPING = {
        'urban': 0,
        'highway': 1,
        'rural': 2,
        'residential': 3
    }

    def __init__(
        self,
        data_path='data/sample_accidents.csv',
        model_path='models/risk_model.pkl'
    ):
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        self.df = None

    def load_data(self):
        self.df = pd.read_csv(self.data_path)
        return self.df

    def preprocess(self, df=None):

        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No dataset loaded. Call load_data() first.")

        d = df.copy()

        # Check required columns
        required = [
            'length_km',
            'num_accidents',
            'num_fatal_accidents',
            'num_injuries',
            'avg_speed_kmph',
            'num_potholes',
            'night_lighting_score',
            'road_type',
            'num_lanes'
        ]

        missing = [col for col in required if col not in d.columns]

        if missing:
            raise ValueError(f"Missing dataset columns: {missing}")

        # Create risk labels
        d['risk_label'] = d.apply(
            lambda r: (
                'critical'
                if r['num_fatal_accidents'] > 0
                or r['num_accidents'] > 10
                else 'high'
                if r['num_accidents'] > 5
                else 'moderate'
                if r['num_accidents'] > 0
                else 'low'
            ),
            axis=1
        )

        # Encode road type
        d['road_type_enc'] = (
            d['road_type']
            .astype(str)
            .str.strip()
            .str.lower()
            .map(self.ROAD_TYPE_MAPPING)
            .fillna(4)
            .astype(int)
        )

        # Select only numeric model features
        X = d[self.FEATURES].copy()

        # Handle missing and invalid numeric values
        X = X.apply(pd.to_numeric, errors='coerce')

        X = X.replace(
            [np.inf, -np.inf],
            np.nan
        ).fillna(0)

        y = d['risk_label']

        return X, y, d

    def train_model(self, save=True):

        if self.df is None:
            self.load_data()

        X, y, d = self.preprocess()

        # Split dataset
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.3,
                random_state=42,
                stratify=y
            )

        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.3,
                random_state=42
            )

        # Train Random Forest
        clf = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        clf.fit(X_train, y_train)

        # Evaluate
        preds = clf.predict(X_test)

        report = classification_report(
            y_test,
            preds,
            output_dict=True,
            zero_division=0
        )

        cm = confusion_matrix(
            y_test,
            preds
        )

        self.model = clf

        # Save model
        if save:
            model_dir = os.path.dirname(self.model_path)

            if model_dir:
                os.makedirs(model_dir, exist_ok=True)

            joblib.dump(clf, self.model_path)

        return report, cm

    def load_model(self):

        try:
            self.model = joblib.load(self.model_path)
            return True

        except (FileNotFoundError, OSError, EOFError, ValueError):
            return False

    def _prepare_segment(self, segment_row):

        if isinstance(segment_row, pd.DataFrame):
            segment_row = segment_row.iloc[0]

        values = {}

        for feature in self.FEATURES:

            if feature == 'road_type_enc':

                road_type = segment_row.get('road_type', None)

                if road_type is not None:
                    value = self.ROAD_TYPE_MAPPING.get(
                        str(road_type).strip().lower(),
                        4
                    )
                else:
                    value = segment_row.get('road_type_enc', 4)

            else:
                value = segment_row.get(feature, 0)

            try:
                value = float(value)

                if not np.isfinite(value):
                    value = 0

            except (TypeError, ValueError):
                value = 0

            values[feature] = value

        return pd.DataFrame(
            [values],
            columns=self.FEATURES
        )

    def predict_segment_risk(self, segment_row):
        """
        Returns predicted risk category and confidence score.
        """

        if self.model is None:

            if not self.load_model():
                raise ValueError(
                    "Model not trained or available. "
                    "Call train_model() first."
                )

        X = self._prepare_segment(segment_row)

        pred = self.model.predict(X)[0]

        probs = self.model.predict_proba(X)[0]

        classes = list(self.model.classes_)

        score = float(
            probs[classes.index(pred)]
        )

        return pred, score

    def explain_segment(self, segment_row):
        """
        Returns the top five important features
        for a road segment.
        """

        if self.model is None:

            if not self.load_model():
                raise ValueError(
                    "Model not trained or available. "
                    "Call train_model() first."
                )

        X = self._prepare_segment(segment_row)

        importances = self.model.feature_importances_

        contributions = []

        for feature, importance, value in zip(
            self.FEATURES,
            importances,
            X.iloc[0].values
        ):

            contributions.append(
                (
                    feature,
                    float(importance),
                    float(value)
                )
            )

        contributions.sort(
            key=lambda x: x[1] * abs(x[2]),
            reverse=True
        )

        explanation = [
            {
                'feature': feature,
                'importance': importance,
                'value': value
            }
            for feature, importance, value
            in contributions[:5]
        ]

        return explanation

    def get_all_segments_with_risk(self):

        df = self.load_data()

        X, y, d = self.preprocess(df)

        if self.model is None:

            if not self.load_model():
                self.train_model(save=True)

        preds = self.model.predict(X)

        probs = self.model.predict_proba(X)

        classes = list(self.model.classes_)

        d['predicted_risk'] = preds

        d['risk_score'] = [
            float(
                probs[i, classes.index(preds[i])]
            )
            for i in range(len(preds))
        ]

        return d
