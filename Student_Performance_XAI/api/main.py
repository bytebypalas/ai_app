"""
=============================================================================
FIX: FastAPI Backend - Serve Real ML Model to React Frontend
=============================================================================
File: api/main.py
Purpose:
  - Expose trained ML model as a REST API so the React frontend uses
    REAL model predictions instead of simulated/heuristic calculations
  - /api/health: health check
  - /api/predict: real prediction + SHAP explanation
  - CORS enabled for React dev server

Usage:
  cd Student_Performance_XAI
  python -m api.main
  # or
  uvicorn api.main:app --reload --port 8000

Dependencies: pip install fastapi uvicorn
=============================================================================
"""

import os
import sys
import warnings
from typing import Optional

warnings.filterwarnings('ignore')

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.predict import predict_student, load_model_artifacts
from xai.shap_analysis import explain_prediction


# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="Student Performance XAI API",
    description="Real ML predictions + SHAP explanations for EduPredict AI",
    version="2.0.0"
)

# Allow all origins for development (React dev server on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# INPUT SCHEMA
# ============================================================================

class StudentInput(BaseModel):
    Student_Name: Optional[str] = "Unnamed Student"
    Attendance_Percentage: float = 75
    Study_Hours_Per_Day: float = 4.0
    Previous_Academic_Marks: float = 65
    Internal_Assessment_Marks: float = 60
    Assignment_Score: float = 70
    Practical_Lab_Score: float = 65
    Number_of_Backlogs: int = 2
    Previous_Semester_GPA: float = 6.5
    Sleep_Hours: float = 7.0
    Internet_Access: int = 1
    Parental_Education: int = 2
    Extracurricular_Activities: int = 1
    Class_Participation: float = 55
    Assignment_Submission_Rate: float = 75


# ============================================================================
# MODEL CACHE
# ============================================================================

_model = None
_preprocessor = None
_label_encoder = None


def get_artifacts():
    """Load and cache model artifacts once."""
    global _model, _preprocessor, _label_encoder
    if _model is None:
        _model, _preprocessor, _label_encoder = load_model_artifacts()
    return _model, _preprocessor, _label_encoder


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "student-performance-xai"}


@app.get("/api/stats")
def get_stats():
    """
    Return REAL aggregate stats computed from the processed dataset
    and the model comparison CSV. Used by the React dashboard so the
    Home/Analytics cards show actual numbers instead of hardcoded demos.
    """
    import pandas as pd

    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, 'dataset', 'processed', 'student_data_cleaned.csv')
    comp_path = os.path.join(base_dir, 'models', 'model_comparison.csv')

    if not os.path.exists(data_path):
        return {"error": "processed dataset not found - run data_preprocessing.py first"}

    df = pd.read_csv(data_path)

    stats = {
        'total_students': int(len(df)),
        'avg_attendance': round(float(df['Attendance_Percentage'].mean()), 1),
        'avg_study_hours': round(float(df['Study_Hours_Per_Day'].mean()), 1),
        'avg_gpa': round(float(df['Previous_Semester_GPA'].mean()), 1),
        'avg_prev_marks': round(float(df['Previous_Academic_Marks'].mean()), 1),
        'avg_internal': round(float(df['Internal_Assessment_Marks'].mean()), 1),
        'avg_assignment': round(float(df['Assignment_Score'].mean()), 1),
        'avg_lab': round(float(df['Practical_Lab_Score'].mean()), 1),
        'avg_backlogs': round(float(df['Number_of_Backlogs'].mean()), 1),
        'avg_sleep': round(float(df['Sleep_Hours'].mean()), 1),
        'avg_participation': round(float(df['Class_Participation'].mean()), 1),
        'avg_submission': round(float(df['Assignment_Submission_Rate'].mean()), 1),
    }

    # Performance distribution (real counts from dataset)
    if 'Performance_Category' in df.columns:
        counts = df['Performance_Category'].value_counts()
        stats['performance_distribution'] = {
            str(k): int(v) for k, v in counts.items()
        }

    # Best model info from comparison CSV
    if os.path.exists(comp_path):
        try:
            comp = pd.read_csv(comp_path)
            if not comp.empty:
                best = comp.iloc[0]
                stats['best_model'] = str(best['Model'])
                stats['model_accuracy'] = round(float(best['Accuracy']) * 100, 1)
                stats['model_f1'] = round(float(best['F1-Score (Weighted)']) * 100, 1)
        except Exception:
            pass

    return stats


@app.post("/api/predict")
def predict(data: StudentInput):
    """Run real ML prediction + SHAP explanation for a student."""
    model, preprocessor, label_encoder = get_artifacts()

    # pydantic v2 uses model_dump(); v1 uses dict()
    if hasattr(data, 'model_dump'):
        student_input = data.model_dump()
    else:
        student_input = data.dict()

    # Real prediction from trained model
    result = predict_student(student_input, model, preprocessor, label_encoder)

    # Real SHAP explanation
    try:
        shap = explain_prediction(model, preprocessor, label_encoder, student_input)
        result['explanation'] = {
            'base_value': shap.get('base_value', 0),
            'positive_factors': shap.get('positive_factors', {}),
            'negative_factors': shap.get('negative_factors', {}),
            'all_contributions': shap.get('all_contributions', {}),
            'feature_names': shap.get('feature_names', []),
        }
    except Exception as e:
        result['explanation'] = {'error': str(e)}

    return result


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

