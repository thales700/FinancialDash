import logging
import pandas as pd
from services.Quotations import Quotations
from sklearn.preprocessing import StandardScaler
from hmmlearn import hmm
from typing import Union, Tuple
import numpy as np
from schemas.symbol_properties import SymbolProperties

logger = logging.getLogger(__name__)

class HiddenMarkovModel:    
    @staticmethod
    def _Features(df: pd.DataFrame) -> Union[pd.DataFrame, str]:
        try:
            df = df.copy()
            df['returns'] = df['Close'].pct_change()

            # Volatilidade realizada (janelas diferentes)
            df['volatility_5'] = df['returns'].rolling(5).std()
            df['volatility_21'] = df['returns'].rolling(21).std()
            df['volatility_63'] = df['returns'].rolling(63).std()

            # Range de preço (High-Low normalizado)
            df['price_range'] = (df['High'] - df['Low']) / df['Close']

            # Volume normalizado
            df['volume_norm'] = df['Volume'] / df['Volume'].rolling(21).mean()

            # ATR (Average True Range)
            df['tr'] = np.maximum(
                df['High'] - df['Low'],
                np.maximum(
                    abs(df['High'] - df['Close'].shift(1)),
                    abs(df['Low'] - df['Close'].shift(1))
                )
            )
            df['atr_14'] = df['tr'].rolling(14).mean()

            # Remover NaNs iniciais
            data = df.dropna()
            logger.info(f"Features calculated successfully.")
            return data
        
        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            return str(e)

    @staticmethod
    def _Normalization(df: pd.DataFrame) -> Union[Tuple[StandardScaler, np.ndarray], str]:
        try:
            features = df[['volatility_21', 'price_range', 'atr_14']].values
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            logger.info("Features normalized successfully.")
            return (scaler, features_scaled)

        except Exception as e:
            logger.error(f"Error normalizing features: {e}")
            return str(e)

    @staticmethod
    def _ModelTrain(features_scaled: np.ndarray, n_regimes: int) -> Union[hmm.GaussianHMM, str]:
        try:
            model = hmm.GaussianHMM(
                n_components=n_regimes,
                covariance_type="full",
                n_iter=1000,
                random_state=42
            )
            model.fit(features_scaled)
            logger.info("HMM model trained successfully.")
            return model

        except Exception as e:
            logger.error(f"Error training HMM model: {e}")
            return str(e)
    
    @staticmethod
    def _ModelPredict(features_scaled: np.ndarray, model: hmm.GaussianHMM) -> Union[np.ndarray, str]:
        try:
            regimes = model.predict(features_scaled)
            logger.info("Regimes predicted successfully.")
            return regimes

        except Exception as e:
            logger.error(f"Error predicting regimes: {e}")
            return str(e)
    
    @staticmethod
    def _RegimeMapping(regime_raw: np.ndarray, data: pd.DataFrame) -> Union[pd.DataFrame, str]:
        try:
            data['regime_raw'] = regime_raw
            means = data.groupby('regime_raw')['volatility_21'].mean().sort_values()
            regime_mapping = {old: new for new, old in enumerate(means.index)}
            data['regime'] = data['regime_raw'].map(regime_mapping).astype(int)
            logger.info("Regime mapping created successfully.")
            return data

        except Exception as e:
            logger.error(f"Error creating regime mapping: {e}")
            return str(e)

    @staticmethod
    def GetRegimes(symbolInfos: SymbolProperties, n_regimes: int) -> Union[str, pd.DataFrame]:
        try:
            data = Quotations().Get(symbolInfos)
            if isinstance(data, str):
                return data

            features_df = HiddenMarkovModel._Features(data)
            if isinstance(features_df, str):
                return features_df

            normalizationResult  = HiddenMarkovModel._Normalization(features_df)
            if isinstance(normalizationResult, str):
                return normalizationResult

            scaler, normalized = normalizationResult
            model = HiddenMarkovModel._ModelTrain(normalized, n_regimes)
            if isinstance(model, str):
                return model

            if isinstance(model, str):
                return model
            
            regimes = HiddenMarkovModel._ModelPredict(normalized, model)
            if isinstance(regimes, str):
                return regimes
            
            ##RESULTADOS DE REGIME_MAPPED_DF IGUAIS AOS DE REGIMES
            regime_mapped_df = HiddenMarkovModel._RegimeMapping(regimes, features_df)
            if isinstance(regime_mapped_df, str):
                return regime_mapped_df
            
            logger.info(f"HMM analysis completed successfully for {symbolInfos.symbol}.")
            return regime_mapped_df

        except Exception as e:
            logger.error(f"Error during HMM analysis for {symbolInfos.symbol}: {e}")
            return str(e)
