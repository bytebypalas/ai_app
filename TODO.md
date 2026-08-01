# Task: Fix Critical AI Project Problems

## 📋 Steps
### Fix 1: Data Leakage → Realistic Accuracy
- [x] Rewrite `dataset/generate_data.py` - latent ability + overlapping categories + noise
- [x] Regenerate dataset (python dataset/generate_data.py)
- [x] Re-run preprocessing (python src/data_preprocessing.py)
- [x] Re-train model (python src/train_model.py) - accuracy 72.5% (was 100%)

### Fix 2: Hardcoded Percentage → Model-Based
- [x] Edit `src/predict.py` - probability-weighted percentage from predict_proba
- [x] Edit `src/predict.py` - honest confidence floor (60 → 30)

### Fix 3: React Fake Model → Real ML API
- [x] Create `api/__init__.py`
- [x] Create `api/main.py` - FastAPI backend (CORS + /api/predict + /api/health)
- [x] Edit `requirements.txt` - add fastapi, uvicorn
- [x] Rewrite `xai-predictor/src/utils/predictionModel.js` - async API call + deterministic fallback
- [x] Edit `xai-predictor/src/components/Predict.jsx` - async handlePredict

### Extras
- [x] Fix README run command (`streamlit run streamlit_app.py`) + document API usage

