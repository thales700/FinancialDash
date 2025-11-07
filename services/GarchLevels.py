import logging
import numpy as np
import pandas as pd
from arch import arch_model
from arch.univariate import EGARCH
from entities.ArchModels import ArchModelType
from typing import Union, Tuple
from services.Quotations import Quotations
from schemas.symbol_properties import SymbolProperties
from entities.Distribution import DistributionType 
from entities.Granularity import Granularity

logger = logging.getLogger(__name__)

class GarchLevels:
    @staticmethod
    def _FIGarchModel(returns: pd.Series, distribution: DistributionType) -> Union[pd.Series, str]:
        try:
            model = arch_model(returns*100, vol='FIGARCH', p=1, o=1, q=1, dist=distribution.value)
            garch_fitted = model.fit(disp='off')
            volatility = pd.Series(garch_fitted.conditional_volatility/100)
            predicted = pd.Series(np.sqrt(garch_fitted.forecast(horizon=1).variance.values)[0]/100)
            volatility = pd.concat([volatility, predicted])
            logger.info("EGARCH model created successfully.")
            return volatility

        except Exception as e:
            logger.error(f"Error creating FIGARCH model: {e}")
            return str(e)

    @staticmethod
    def _EGarchModel(returns: pd.Series, distribution: DistributionType) -> Union[pd.Series, str]:
        try:
            model = arch_model(returns*100, vol='EGARCH', p=1, o=1, q=1, dist=distribution.value)
            garch_fitted = model.fit(disp='off')
            volatility = pd.Series(garch_fitted.conditional_volatility/100)
            predicted = pd.Series(np.sqrt(garch_fitted.forecast(horizon=1).variance.values)[0]/100)
            volatility = pd.concat([volatility, predicted])
            logger.info("EGARCH model created successfully.")
            return volatility

        except Exception as e:
            logger.error(f"Error creating EGARCH model: {e}")
            return str(e)

    @staticmethod
    def _GarchModel(returns: pd.Series, distribution: DistributionType) -> Union[pd.Series, str]:
        try:
            model = arch_model(returns*100, vol='GARCH', p=1, q=1, dist=distribution.value)
            garch_fitted = model.fit(disp='off')
            volatility = pd.Series(garch_fitted.conditional_volatility/100)
            predicted = pd.Series(np.sqrt(garch_fitted.forecast(horizon=1).variance.values)[0]/100)
            volatility = pd.concat([volatility, predicted])
            volatility.reset_index(inplace=True, drop=True)
            logger.info("GARCH model created successfully.")
            return volatility

        except Exception as e:
            logger.error(f"Error creating GARCH model: {e}")
            return str(e)

    @staticmethod
    def _TrainModel(df: pd.DataFrame, modelType: ArchModelType, distribution: DistributionType, levels: int) -> Union[pd.Series, str]:
        df['returns'] = df['Close'].pct_change()
        df.dropna(inplace=True)
        if modelType == ArchModelType.GARCH:
            return GarchLevels._GarchModel(df['returns'], distribution)
        elif modelType == ArchModelType.EGARCH:
            return GarchLevels._EGarchModel(df['returns'], distribution)
        elif modelType == ArchModelType.FIGARCH:
            return GarchLevels._FIGarchModel(df['returns'], distribution)
        else:
            logger.error(f"Unknown model type: {modelType}")
            return "Unknown model type"

    @staticmethod
    def _CalculateLevels(df: pd.DataFrame, modelType: ArchModelType, distribution: DistributionType, levels: int) -> Union[pd.DataFrame, str]:
        try:
            if levels <= 0:
                logger.error("Levels must be a positive integer.")
                return "Levels must be a positive integer."
            
            # Criar uma cópia explícita do DataFrame para evitar SettingWithCopyWarning
            df = df.copy()
            
            # Treinar o modelo com os dados históricos (excluindo as últimas 2 linhas)
            volatility = GarchLevels._TrainModel(df.iloc[:-1], modelType, distribution, levels)
            #logger.info(f"{volatility}")
            if isinstance(volatility, str):
                return volatility
            
            df = df[1:]
            df['Date'] = df.index
            df.reset_index(inplace=True, drop=True)
            df['volatility'] = volatility
            logger.info(f"{df['volatility']}")
  
            for level in range(1, levels + 1):
                col_pos = f'volatility_level_{level}'
                col_neg = f'volatility_level_-{level}'
                df[col_pos] = df['Close'] * (1 + level*df['volatility'])
                df[col_neg] = df['Close'] * (1 - level*df['volatility'])
                df.loc[df.index[-1], col_pos] = df['Open'].iloc[-1] * (1 + level*df['volatility'].iloc[-1])
                df.loc[df.index[-1], col_neg] = df['Open'].iloc[-1] * (1 - level*df['volatility'].iloc[-1])
            
            df.index = df['Date'] #type: ignore
            logger.info(f"Calculated {levels} volatility levels successfully.")
            return df
        except Exception as e:
            logger.error(f"Error calculating volatility levels: {e}")
            return str(e)


    @staticmethod
    def _MergeDataFrames(df: pd.DataFrame, df_daily: pd.DataFrame) -> Union[pd.DataFrame, str]:
        try:
            df_copy = df.copy()
            df_daily_copy = df_daily.copy()
            
            df_copy['time'] = pd.to_datetime(df_copy.index).date
            df_daily_copy['time'] = pd.to_datetime(df_daily_copy.index).date

            df_merged = df_copy.merge(
                df_daily_copy, 
                on='time',
                suffixes=('', '_diary'), 
                how='left'
            )
            
            df_merged.index = df.index

            logger.info("DataFrames merged successfully.")
            return df_merged
            
        except Exception as e:
            logger.error(f"Error merging DataFrames: {e}")
            return str(e)
    
    @staticmethod
    def _FixDecimalPlaces(df: pd.DataFrame) -> Union[pd.DataFrame, str]:
        try:
            decimal_places = df['Close'].astype(str).str.split('.').str[1].str.len().max()

            for col in df.select_dtypes(include=[np.number]).columns:
                df[col] = df[col].round(decimal_places)

            logger.info("Decimal places fixed successfully.")
            return df

        except Exception as e:
            logger.error(f"Error fixing decimal places: {e}")
            return str(e)

    @staticmethod
    def GetLevels(symbolInfos: SymbolProperties, modelType: ArchModelType, 
                  distribution: DistributionType, levels: int) -> Union[pd.DataFrame, str]:
        try:
            quotation_service = Quotations()
            df = quotation_service.Get(symbolInfos)
            if isinstance(df, str):
                return df

            symbolInfos_daily = symbolInfos
            symbolInfos_daily.granularity = Granularity.ONE_DAY
            symbolInfos_daily.start_date = '2023-01-01'
            df_daily = quotation_service.Get(symbolInfos_daily)

            if isinstance(df_daily, str):
                return df_daily

            df_daily = GarchLevels._CalculateLevels(df_daily, modelType, distribution, levels)
            if isinstance(df_daily, str):
                return df_daily

            df_merged = GarchLevels._MergeDataFrames(df, df_daily)
            if isinstance(df_merged, str):
                return df_merged

            df_merged = GarchLevels._FixDecimalPlaces(df_merged)
            if isinstance(df_merged, str):
                return df_merged

            logger.info("Levels of volatility calculated successfully.")
            return df_merged

        except Exception as e:
            logger.error(f"Error retrieving quotations: {e}")
            return str(e)