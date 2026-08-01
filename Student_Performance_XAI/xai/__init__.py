"""
Explainable AI (XAI) Module for Student Performance Prediction

This module provides SHAP-based explainability features:
- shap_analysis.py: Core SHAP analysis, prediction explanations
- explanation.py: Human-readable explanations and recommendation engine
- feature_importance.py: Global and local feature importance analysis
"""

from .shap_analysis import (
    load_artifacts,
    prepare_input_features,
    explain_prediction,
    get_global_feature_importance,
    create_human_readable_explanation
)

from .explanation import (
    generate_explanation,
    generate_recommendations,
    generate_report_content
)

from .feature_importance import (
    load_model_for_importance,
    get_feature_importance_df,
    get_top_features,
    get_model_feature_importance,
    compute_shap_feature_importance,
    compare_feature_importance,
    plot_feature_importance,
    get_local_feature_importance
)

__all__ = [
    'load_artifacts',
    'prepare_input_features',
    'explain_prediction',
    'get_global_feature_importance',
    'create_human_readable_explanation',
    'generate_explanation',
    'generate_recommendations',
    'generate_report_content',
    'load_model_for_importance',
    'get_feature_importance_df',
    'get_top_features',
    'get_model_feature_importance',
    'compute_shap_feature_importance',
    'compare_feature_importance',
    'plot_feature_importance',
    'get_local_feature_importance'
]

