from fastapi import APIRouter, HTTPException
from services.GarchLevels import GarchLevels
from schemas.symbol_properties import SymbolProperties
from entities.ArchModels import ArchModelType
from entities.Distribution import DistributionType
import numpy as np
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/garch_levels")
def get_garch_levels(props: SymbolProperties, modelType: ArchModelType, distribution: DistributionType, levels: int):
    """
    Retorna os níveis de volatilidade estimados pelo modelo GARCH.
    """
    try:
        garch_service = GarchLevels()
        result = garch_service.GetLevels(
            symbolInfos=props,
            modelType=modelType,
            distribution=distribution,
            levels=levels
            )

        if isinstance(result, str):
            raise HTTPException(status_code=400, detail=result)
        
        # Substituir NaN por None (que é convertido para null em JSON)
        result_cleaned = result.replace([np.nan, np.inf, -np.inf], None)
        
        return {
            "symbol": props.symbol,
            "garch_levels": result_cleaned.reset_index().to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"Erro ao obter níveis GARCH de {props.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))