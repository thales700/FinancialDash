import sys
import os
import json
import pandas as pd
import logging
from datetime import datetime, timedelta

# Configuração de logging
logger = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# Importações dos seus módulos
from entities.Distribution import DistributionType
from schemas.symbol_properties import SymbolProperties
from services.GarchLevels import GarchLevels
from services.HiddenMarkovModel import HiddenMarkovModel
from services.Quotations import Quotations
from entities.Granularity import Granularity
from entities.ArchModels import ArchModelType
from entities.Symbols import Symbols

def dataframe_to_dict(df):
    """Converte DataFrame para dicionário preservando todos os dados"""
    if isinstance(df, str):
        return {"error": df}
    
    # Verifica se o DataFrame está vazio
    if df.empty:
        logger.warning("DataFrame vazio retornado")
        return []
    
    # Reset index para incluir datas como coluna
    df_copy = df.copy()
    if df_copy.index.name or not isinstance(df_copy.index, pd.RangeIndex):
        df_copy = df_copy.reset_index()
    
    # Converte para dicionário mantendo precisão
    return df_copy.to_dict(orient='records')

def generate_quotations_data():
    """Gera dados de cotações usando o serviço Quotations"""
    logger.info("Gerando dados de Quotations...")
    quotations_data = {}
    quotation_service = Quotations()
    
    # Calcula datas válidas para dados intradiários (últimos 7 dias)
    end_date = datetime.now()
    start_date_15min = end_date - timedelta(days=7)
    start_date_15min_str = start_date_15min.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    for symbol in Symbols:
        logger.info(f"Processando cotações para {symbol.value}...")
        quotations_data[symbol.value] = {}
        
        # Dados diários (pode usar período longo)
        symbol_props_daily = SymbolProperties(
            symbol=symbol,
            start_date="2023-10-01",
            end_date=end_date_str,
            granularity=Granularity.ONE_DAY
        )
        df_daily = quotation_service.Get(symbol_props_daily)
        quotations_data[symbol.value]["daily"] = dataframe_to_dict(df_daily)
        
        # Dados de 15 minutos (limitado aos últimos 7 dias)
        symbol_props_15min = SymbolProperties(
            symbol=symbol,
            start_date=start_date_15min_str,
            end_date=end_date_str,
            granularity=Granularity.FIFTEEN_MINUTES
        )
        df_15min = quotation_service.Get(symbol_props_15min)
        quotations_data[symbol.value]["15min"] = dataframe_to_dict(df_15min)
    
    logger.info("Dados de Quotations gerados com sucesso!")
    return quotations_data

def generate_garch_levels_data():
    """Gera dados de níveis GARCH usando o serviço GarchLevels"""
    logger.info("Gerando dados de GARCH Levels...")
    garch_data = {}
    
    # Calcula datas válidas para dados intradiários (últimos 30 dias)
    # Yahoo Finance limita dados de 15min a ~60 dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    for symbol in Symbols:
        logger.info(f"Processando GARCH para {symbol.value}...")
        garch_data[symbol.value] = {}
        
        for model_type in ArchModelType:
            garch_data[symbol.value][model_type.value] = {}
            
            for distribution in DistributionType:
                logger.info(f"  Modelo: {model_type.value}, Distribuição: {distribution.value}")
                
                symbol_props = SymbolProperties(
                    symbol=symbol,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    granularity=Granularity.FIFTEEN_MINUTES
                )
                
                df = GarchLevels.GetLevels(
                    symbolInfos=symbol_props,
                    modelType=model_type,
                    distribution=distribution,
                    levels=3
                )
                
                garch_data[symbol.value][model_type.value][distribution.value] = dataframe_to_dict(df)
    
    logger.info("Dados de GARCH Levels gerados com sucesso!")
    return garch_data

def generate_hmm_data():
    """Gera dados de Hidden Markov Model usando o serviço HiddenMarkovModel"""
    logger.info("Gerando dados de Hidden Markov Model...")
    hmm_data = {}
    
    # Para HMM, usar dados diários com período adequado
    end_date = datetime.now()
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    for symbol in Symbols:
        logger.info(f"Processando HMM para {symbol.value}...")
        hmm_data[symbol.value] = {}
        
        for n_regimes in [2, 3]:
            logger.info(f"  Estados: {n_regimes}")
            
            symbol_props = SymbolProperties(
                symbol=symbol,
                start_date="2023-01-01",
                end_date=end_date_str,
                granularity=Granularity.ONE_DAY
            )
            
            df = HiddenMarkovModel.GetRegimes(
                symbolInfos=symbol_props,
                n_regimes=n_regimes
            )
            
            hmm_data[symbol.value][f"{n_regimes}_states"] = dataframe_to_dict(df)
    
    logger.info("Dados de Hidden Markov Model gerados com sucesso!")
    return hmm_data

def main():
    """Função principal para gerar todos os dados de mock"""
    logger.info("="*60)
    logger.info("INICIANDO GERAÇÃO DE DADOS DE MOCK")
    logger.info("="*60)
    
    mock_data = {}
    
    # Gera dados de Quotations
    try:
        mock_data["quotations"] = generate_quotations_data()
    except Exception as e:
        logger.error(f"Erro ao gerar dados de Quotations: {e}")
        mock_data["quotations"] = {"error": str(e)}
    
    # Gera dados de GARCH Levels
    try:
        mock_data["garch_levels"] = generate_garch_levels_data()
    except Exception as e:
        logger.error(f"Erro ao gerar dados de GARCH Levels: {e}")
        mock_data["garch_levels"] = {"error": str(e)}
    
    # Gera dados de Hidden Markov Model
    try:
        mock_data["hidden_markov_model"] = generate_hmm_data()
    except Exception as e:
        logger.error(f"Erro ao gerar dados de HMM: {e}")
        mock_data["hidden_markov_model"] = {"error": str(e)}
    
    # Cria diretório para os arquivos mock
    mock_dir = 'mock_data'
    if not os.path.exists(mock_dir):
        os.makedirs(mock_dir)
        logger.info(f"Diretório '{mock_dir}' criado")
    
    # Salva cada tipo de dado em arquivo separado
    logger.info("Salvando dados em arquivos separados...")
    
    quotations_file = os.path.join(mock_dir, 'quotations.json')
    with open(quotations_file, 'w') as f:
        json.dump(mock_data["quotations"], f, indent=2, default=str)
    logger.info(f"  ✓ Quotations salvo em '{quotations_file}'")
    
    garch_file = os.path.join(mock_dir, 'garch_levels.json')
    with open(garch_file, 'w') as f:
        json.dump(mock_data["garch_levels"], f, indent=2, default=str)
    logger.info(f"  ✓ GARCH Levels salvo em '{garch_file}'")
    
    hmm_file = os.path.join(mock_dir, 'hidden_markov_model.json')
    with open(hmm_file, 'w') as f:
        json.dump(mock_data["hidden_markov_model"], f, indent=2, default=str)
    logger.info(f"  ✓ Hidden Markov Model salvo em '{hmm_file}'")
    
    logger.info("="*60)
    logger.info(f"✅ DADOS GERADOS COM SUCESSO EM '{mock_dir}/'")
    logger.info("="*60)
    
    # Estatísticas
    print("\n=== ESTATISTICAS ===")
    print(f"  - Simbolos processados: {len(Symbols)}")
    print(f"  - Modelos GARCH: {len(ArchModelType)}")
    print(f"  - Distribuicoes: {len(DistributionType)}")
    print(f"  - Estados HMM: 2 e 3")
    print(f"\n=== Total de combinacoes ===")
    print(f"  - Quotations: {len(Symbols)} x 2 timeframes = {len(Symbols) * 2}")
    print(f"  - GARCH Levels: {len(Symbols)} x {len(ArchModelType)} x {len(DistributionType)} = {len(Symbols) * len(ArchModelType) * len(DistributionType)}")
    print(f"  - HMM: {len(Symbols)} x 2 estados = {len(Symbols) * 2}")

if __name__ == "__main__":
    main()