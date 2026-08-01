"""
Application Components Module

This module provides reusable Streamlit components:
- prediction.py: Student input form and prediction result display
- explanation.py: SHAP explanation display with visualizations
- visualization.py: Analytics dashboard with Plotly charts
"""

from .prediction import (
    student_input_form,
    display_prediction_result,
    validate_inputs
)

from .explanation import (
    display_shap_explanation,
    display_global_feature_importance,
    create_waterfall_chart,
    create_contribution_bar_chart
)

from .visualization import (
    display_analytics_dashboard,
    display_model_comparison,
    get_summary_stats
)

__all__ = [
    'student_input_form', 'display_prediction_result', 'validate_inputs',
    'display_shap_explanation', 'display_global_feature_importance',
    'create_waterfall_chart', 'create_contribution_bar_chart',
    'display_analytics_dashboard', 'display_model_comparison', 'get_summary_stats'
]

