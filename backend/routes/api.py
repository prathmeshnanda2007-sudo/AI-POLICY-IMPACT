"""API Routes for Policy Simulator."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging

from services.auth import get_current_user

from models.ml_model import (
    predict_policy, load_model, train_and_select_best,
    get_feature_importance, sensitivity_analysis, recommend_policy
)
from services.database import (
    save_scenario, get_all_scenarios, delete_scenario as db_delete_scenario,
    save_simulation, get_history as db_get_history, log_training
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Load model on startup (trains if not found)
try:
    model, _, metadata = load_model()
except Exception as _load_err:
    import logging as _log
    _log.getLogger(__name__).error(f"Model load failed at import: {_load_err}. Will retry on first request.")
    model, metadata = None, {}


# --- Request Schemas ---

class PolicyInput(BaseModel):
    Inflation_CPI: float = Field(ge=0, le=20, default=5)
    Tax_Revenue_Pct_GDP: float = Field(ge=5, le=30, default=15)
    Unemployment_Pct: float = Field(ge=2, le=20, default=7)
    CO2_Emissions: float = Field(ge=100000, le=5000000, default=2500000)
    FDI_Net_Inflows_Pct_GDP: float = Field(ge=-2, le=10, default=2)


class CompareRequest(BaseModel):
    scenarios: List[Dict]


class ScenarioCreate(BaseModel):
    name: str
    inputs: Dict
    results: Dict


class SensitivityRequest(BaseModel):
    inputs: Optional[Dict] = None
    target_variable: str = 'gdp_growth'


class RecommendRequest(BaseModel):
    gdp_growth: Optional[float] = 4.0


# --- Prediction Endpoints ---

@router.post("/predict")
async def predict(inputs: PolicyInput, current_user: dict = Depends(get_current_user)):
    """Run policy simulation and return predicted outcomes."""
    global model, metadata
    try:
        # Lazy load: train if model wasn't available at startup
        if model is None:
            logger.info("Model not loaded, training now...")
            model, _, metadata = train_and_select_best()

        input_dict = inputs.model_dump()
        result = predict_policy(input_dict, model)

        # Save to database
        save_simulation(
            inputs=input_dict,
            results=result,
            model_type=metadata.get('model_type', 'RandomForest'),
            confidence=result.get('confidence')
        )

        logger.info(f"Prediction: GDP={result['gdp_growth']:.2f}")
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare(request: CompareRequest, current_user: dict = Depends(get_current_user)):
    """Compare multiple policy scenarios."""
    try:
        results = []
        for scenario_inputs in request.scenarios:
            result = predict_policy(scenario_inputs, model)
            results.append(result)
        return results
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train(current_user: dict = Depends(get_current_user)):
    """Retrain the ML model with fresh synthetic data."""
    global model, metadata
    try:
        model, _, metadata = train_and_select_best()
        log_training(
            model_type=metadata['model_type'],
            rmse=metadata['rmse'],
            r2=metadata['r2_score'],
            samples=metadata['training_samples']
        )
        return {
            "status": "success",
            "model_type": metadata['model_type'],
            "rmse": metadata['rmse'],
            "r2_score": metadata['r2_score'],
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Model Info ---

@router.get("/model/info")
async def model_info():
    """Get current model information."""
    return metadata


@router.get("/model/feature-importance")
async def feature_importance():
    """Get feature importance from trained model."""
    return get_feature_importance()


# --- Scenarios CRUD ---

@router.get("/scenarios")
async def list_scenarios(current_user: dict = Depends(get_current_user)):
    """List all saved scenarios for the current user."""
    return get_all_scenarios(current_user['id'])


@router.post("/scenarios")
async def create_scenario(scenario: ScenarioCreate, current_user: dict = Depends(get_current_user)):
    """Save a new scenario for the current user."""
    try:
        saved = save_scenario(scenario.name, scenario.inputs, scenario.results, current_user['id'])
        return saved
    except Exception as e:
        logger.error(f"Save scenario error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/scenarios/{scenario_id}")
async def remove_scenario(scenario_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a saved scenario."""
    success = db_delete_scenario(scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "deleted"}


# --- History ---

@router.get("/history")
async def history(current_user: dict = Depends(get_current_user)):
    """Get simulation history for the current user."""
    return db_get_history(50, current_user['id'])


# --- Advanced ML ---

@router.post("/sensitivity")
async def run_sensitivity(request: SensitivityRequest, current_user: dict = Depends(get_current_user)):
    """Run sensitivity analysis on policy inputs."""
    try:
        base = request.inputs or {
            'Inflation_CPI': 5.0, 'Tax_Revenue_Pct_GDP': 15.0, 
            'Unemployment_Pct': 7.0, 'CO2_Emissions': 2500000.0, 
            'FDI_Net_Inflows_Pct_GDP': 2.0
        }
        result = sensitivity_analysis(base, request.target_variable)
        return result
    except Exception as e:
        logger.error(f"Sensitivity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def recommend(request: RecommendRequest, current_user: dict = Depends(get_current_user)):
    """Get AI policy recommendation for desired outcomes."""
    try:
        targets = {k: v for k, v in request.model_dump().items() if v is not None}
        result = recommend_policy(targets)
        return result
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
