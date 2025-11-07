from fastapi import APIRouter, HTTPException
from services.HiddenMarkovModel import HiddenMarkovModel
from schemas.symbol_properties import SymbolProperties
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
@router.post("/markov_regimes")
def get_markov_regimes(props: SymbolProperties, n_regimes: int):
    """
    Retorna os regimes de mercado identificados pelo modelo Hidden Markov.
    """
    try:
        hmm_service = HiddenMarkovModel()
        result = hmm_service.GetRegimes(
            symbolInfos=props,
            n_regimes=n_regimes
        )

        if isinstance(result, str):
            raise HTTPException(status_code=400, detail=result)
        
        return {
            "symbol": props.symbol,
            "regimes": result.reset_index().to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"Erro ao obter regimes de {props.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))