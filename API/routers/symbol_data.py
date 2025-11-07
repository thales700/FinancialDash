from fastapi import APIRouter, HTTPException
from services.Quotations import Quotations
from schemas.symbol_properties import SymbolProperties
import logging
logger = logging.getLogger(__name__)

router = APIRouter()
@router.post("/data")
def get_symbol_data(props: SymbolProperties):
    """
    Retorna cotações históricas com base nas propriedades enviadas.
    """
    try:
        quotation_service = Quotations()
        df = quotation_service.Get(
            props.symbol,
            props.start_date,
            props.end_date,
            props.granularity
        )

        if isinstance(df, str):
            raise HTTPException(status_code=400, detail=df)
        
        return {
            "symbol": props.symbol,
            "data": df.reset_index().to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"Erro ao obter dados de {props.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))