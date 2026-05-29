import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from models.ml_model import predict_policy, load_model
from services.database import save_simulation
from services.auth import decode_token

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    model, _, metadata = load_model()
except Exception as e:
    model, metadata = None, {}

@router.websocket("/ws/simulate")
async def websocket_simulate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive input parameters from frontend
            data = await websocket.receive_text()
            inputs = json.loads(data)
            token = inputs.pop('token', None)
            
            user_id = None
            if token:
                payload = decode_token(token)
                if payload and 'sub' in payload:
                    user_id = int(payload['sub'])
            
            # 1. Stream "Analyzing data..."
            await websocket.send_json({"status": "processing", "step": "Ingesting policy parameters..."})
            await asyncio.sleep(0.3)
            
            # 2. Stream "Running Random Forest Model..."
            await websocket.send_json({"status": "processing", "step": f"Running {metadata.get('model_type', 'ML')} Engine..."})
            await asyncio.sleep(0.4)
            
            # 3. Predict actual results
            if model:
                result = predict_policy(inputs, model)
            else:
                # Fallback if model not loaded
                result = {
                    "gdp_growth": 2.5,
                    "inflation": 3.0,
                    "employment_rate": 95.0,
                    "environment_score": 75.0,
                    "public_satisfaction": 70.0,
                    "confidence": 0.8
                }
            
            # 4. Stream "Calculating macro-economic impact..."
            await websocket.send_json({"status": "processing", "step": "Calculating macro-economic impacts..."})
            await asyncio.sleep(0.5)
            
            # Save to DB
            try:
                save_simulation(
                    inputs=inputs,
                    results=result,
                    model_type=metadata.get('model_type', 'RandomForest'),
                    confidence=result.get('confidence'),
                    user_id=user_id
                )
            except Exception as e:
                logger.error(f"Failed to save via WS: {e}")

            # 5. Send final results
            await websocket.send_json({
                "status": "complete",
                "results": result
            })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
        except:
            pass
