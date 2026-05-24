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
    model, scaler, metadata = load_model()
except Exception as _load_err:
    import logging as _log
    _log.getLogger(__name__).error(f"Model load failed at import: {_load_err}. Will retry on first request.")
    model, scaler, metadata = None, None, {}


# --- Request Schemas ---

class PolicyInput(BaseModel):
    tax_rate: float = Field(ge=0, le=60, default=25)
    fuel_price: float = Field(ge=1, le=10, default=3.5)
    subsidy: float = Field(ge=0, le=50, default=15)
    public_spending: float = Field(ge=10, le=60, default=30)
    interest_rate: float = Field(ge=0, le=20, default=5)
    environmental_regulation: float = Field(ge=0, le=100, default=50)


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
    inflation: Optional[float] = 2.5
    employment_rate: Optional[float] = 96.0
    environment_score: Optional[float] = 80.0
    public_satisfaction: Optional[float] = 75.0


# --- Prediction Endpoints ---

@router.post("/predict")
async def predict(inputs: PolicyInput, current_user: dict = Depends(get_current_user)):
    """Run policy simulation and return predicted outcomes."""
    global model, scaler, metadata
    try:
        # Lazy load: train if model wasn't available at startup
        if model is None or scaler is None:
            logger.info("Model not loaded, training now...")
            model, scaler, metadata = train_and_select_best()

        input_dict = inputs.model_dump()
        result = predict_policy(input_dict, model, scaler)

        # Save to database
        save_simulation(
            inputs=input_dict,
            results=result,
            model_type=metadata.get('model_type', 'RandomForest'),
            confidence=result.get('confidence')
        )

        logger.info(f"Prediction: GDP={result['gdp_growth']:.2f}, Inflation={result['inflation']:.2f}")
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
            result = predict_policy(scenario_inputs, model, scaler)
            results.append(result)
        return results
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train(current_user: dict = Depends(get_current_user)):
    """Retrain the ML model with fresh synthetic data."""
    global model, scaler, metadata
    try:
        model, scaler, metadata = train_and_select_best()
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
            'tax_rate': 25, 'fuel_price': 3.5, 'subsidy': 15,
            'public_spending': 30, 'interest_rate': 5, 'environmental_regulation': 50
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
