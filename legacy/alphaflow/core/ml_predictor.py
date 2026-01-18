"""ML Predictor for Version 6 Trading App."""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Optional, Tuple

from .config import SKLEARN_AVAILABLE, TradingConfig

if SKLEARN_AVAILABLE:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split


class MLPredictor:
    """Machine Learning price prediction."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.classifier = None
        self.regressor = None
        self.scaler = None
        self.is_trained = False
        self.last_trained = None
        self.feature_columns = []
        self.training_accuracy = 0.0
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare features for ML model."""
        
        df = df.copy()
        
        # Create target: 1 if price goes up next period, 0 otherwise
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        
        # Create return target for regression
        df['return_target'] = df['close'].pct_change(1).shift(-1) * 100
        
        # Select features
        feature_cols = [
            'rsi', 'macd', 'macd_histogram', 'bb_percent',
            'stoch_k', 'stoch_d', 'adx', 'cci', 'williams_r',
            'momentum', 'roc', 'volume_ratio', 'atr'
        ]
        
        # Filter to available columns
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols
        
        # Drop NaN rows
        df_clean = df.dropna(subset=available_cols + ['target', 'return_target'])
        
        if len(df_clean) < TradingConfig.ML_MIN_SAMPLES:
            return None, None, None
        
        X = df_clean[available_cols].values
        y_class = df_clean['target'].values
        y_reg = df_clean['return_target'].values
        
        return X, y_class, y_reg
    
    def train(self, df: pd.DataFrame) -> bool:
        """Train the ML models."""
        
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn not available")
            return False
        
        X, y_class, y_reg = self.prepare_features(df)
        
        if X is None:
            self.logger.warning("Insufficient data for training")
            return False
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_class, test_size=0.2, shuffle=False
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train classifier
            self.classifier = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.classifier.fit(X_train_scaled, y_train)
            
            # Evaluate
            self.training_accuracy = self.classifier.score(X_test_scaled, y_test)
            
            # Train regressor for return prediction
            _, _, y_reg_train, _ = train_test_split(
                X, y_reg, test_size=0.2, shuffle=False
            )
            
            self.regressor = RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
            self.regressor.fit(X_train_scaled, y_reg_train[:len(X_train_scaled)])
            
            self.is_trained = True
            self.last_trained = datetime.now()
            
            self.logger.info(f"ML models trained. Accuracy: {self.training_accuracy:.2%}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training ML models: {e}")
            return False
    
    def predict(self, df: pd.DataFrame) -> dict:
        """Make predictions on latest data."""
        
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return {
                'direction': 0.5,
                'confidence': 0.0,
                'expected_return': 0.0,
                'signal': 'HOLD'
            }
        
        try:
            # Get latest row features
            available_cols = [col for col in self.feature_columns if col in df.columns]
            
            if len(available_cols) != len(self.feature_columns):
                return {
                    'direction': 0.5,
                    'confidence': 0.0,
                    'expected_return': 0.0,
                    'signal': 'HOLD'
                }
            
            latest = df[available_cols].iloc[-1:].values
            
            # Check for NaN
            if np.any(np.isnan(latest)):
                return {
                    'direction': 0.5,
                    'confidence': 0.0,
                    'expected_return': 0.0,
                    'signal': 'HOLD'
                }
            
            # Scale and predict
            latest_scaled = self.scaler.transform(latest)
            
            # Classification prediction
            direction_prob = self.classifier.predict_proba(latest_scaled)[0]
            up_prob = direction_prob[1] if len(direction_prob) > 1 else 0.5
            
            # Regression prediction
            expected_return = self.regressor.predict(latest_scaled)[0]
            
            # Calculate confidence
            confidence = abs(up_prob - 0.5) * 2  # 0 to 1
            
            # Determine signal
            if up_prob > 0.6 and confidence > 0.3:
                signal = 'BUY'
            elif up_prob < 0.4 and confidence > 0.3:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            return {
                'direction': up_prob,
                'confidence': confidence,
                'expected_return': expected_return,
                'signal': signal
            }
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return {
                'direction': 0.5,
                'confidence': 0.0,
                'expected_return': 0.0,
                'signal': 'HOLD'
            }
    
    def retrain_if_needed(self, df: pd.DataFrame, hours_threshold: int = 24) -> bool:
        """Retrain model if it's been too long since last training."""
        
        if not self.is_trained:
            return self.train(df)
        
        if self.last_trained:
            hours_since = (datetime.now() - self.last_trained).total_seconds() / 3600
            if hours_since > hours_threshold:
                self.logger.info(f"Retraining ML models (last trained {hours_since:.1f}h ago)")
                return self.train(df)
        
        return True
    
    def get_feature_importance(self) -> dict:
        """Get feature importance from trained model."""
        
        if not self.is_trained or self.classifier is None:
            return {}
        
        try:
            importances = self.classifier.feature_importances_
            return dict(zip(self.feature_columns, importances))
        except Exception:
            return {}
