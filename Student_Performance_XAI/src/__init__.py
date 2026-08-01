"""
Source Code Module for Student Performance Prediction

This module provides core functionality:
- data_preprocessing.py: Data cleaning, feature engineering, EDA
- train_model.py: Model training, evaluation, comparison
- predict.py: Single student prediction with grade/risk/confidence
- evaluate.py: Comprehensive model evaluation and cross-validation
"""

from .data_preprocessing import (
    load_data,
    check_missing_values,
    check_duplicates,
    handle_outliers,
    feature_engineering,
    encode_target_variable,
    create_preprocessing_pipeline,
    generate_eda_visualizations
)

from .train_model import (
    load_processed_data,
    prepare_features_target,
    split_data,
    train_models,
    evaluate_models,
    plot_confusion_matrices,
    cross_validate_models,
    save_best_model,
    plot_feature_importance
)

from .predict import (
    load_model_artifacts,
    predict_student,
    prepare_student_input,
    get_grade,
    get_risk_level,
    get_performance_level,
    estimate_confidence
)

from .evaluate import (
    load_data_and_artifacts,
    evaluate_model,
    cross_validate,
    analyze_errors,
    generate_evaluation_report
)

__all__ = [
    'load_data', 'check_missing_values', 'check_duplicates',
    'handle_outliers', 'feature_engineering', 'encode_target_variable',
    'create_preprocessing_pipeline', 'generate_eda_visualizations',
    'load_processed_data', 'prepare_features_target', 'split_data',
    'train_models', 'evaluate_models', 'plot_confusion_matrices',
    'cross_validate_models', 'save_best_model', 'plot_feature_importance',
    'load_model_artifacts', 'predict_student', 'prepare_student_input',
    'get_grade', 'get_risk_level', 'get_performance_level', 'estimate_confidence',
    'load_data_and_artifacts', 'evaluate_model', 'cross_validate',
    'analyze_errors', 'generate_evaluation_report'
]

