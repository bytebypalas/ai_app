"""
=============================================================================
STEP 6-9: Model Training, Evaluation & Saving
=============================================================================
File: src/train_model.py
Purpose:
  - Train multiple ML models (Logistic Regression, Decision Tree, Random Forest)
  - Evaluate and compare model performance
  - Save the best model and associated artifacts
  - Generate model comparison report

Input:  dataset/processed/student_data_cleaned.csv
        models/preprocessor.pkl
        models/label_encoder.pkl
Output: models/student_performance_model.pkl (best model)
        models/model_comparison.csv
        reports/confusion_matrices.png
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report,
                             roc_auc_score)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')


def load_processed_data(filepath):
    """Load the preprocessed dataset."""
    print("\n" + "=" * 60)
    print("LOADING PROCESSED DATA")
    print("=" * 60)
    df = pd.read_csv(filepath)
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def prepare_features_target(df):
    """Separate features and target variable."""
    # Features to use (exclude target, labels, and display-only columns)
    exclude_cols = ['Performance_Category', 'Performance_Label',
                    'Parental_Education_Label', 'Composite_Score']
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    X = df[feature_cols]
    y = df['Performance_Label']

    print(f"\nFeature columns ({len(feature_cols)}):")
    for f in feature_cols:
        print(f"  - {f}")
    print(f"\nTarget classes: {sorted(y.unique())}")
    print(f"Target distribution:\n{y.value_counts().sort_index()}")

    return X, y, feature_cols


def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into train and test sets with stratification."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"\nTrain set: {X_train.shape[0]} samples")
    print(f"Test set:  {X_test.shape[0]} samples")
    return X_train, X_test, y_train, y_test


def train_models(X_train, y_train):
    """Train multiple classification models."""
    print("\n" + "=" * 60)
    print("TRAINING MODELS")
    print("=" * 60)

    # Check sklearn version for parameter compatibility
    import sklearn
    sklearn_version = sklearn.__version__
    print(f"  Using sklearn version: {sklearn_version}")

    if sklearn_version >= "1.4":
        lr_params = {'max_iter': 2000, 'random_state': 42}
    else:
        lr_params = {'max_iter': 2000, 'random_state': 42,
                     'multi_class': 'multinomial'}

    models = {
        'Logistic Regression': LogisticRegression(**lr_params),
        'Decision Tree': DecisionTreeClassifier(
            random_state=42, max_depth=10, min_samples_split=5
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=200, random_state=42, max_depth=15,
            min_samples_split=5, n_jobs=-1
        )
    }

    trained_models = {}
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        print(f"  {name} training complete!")

    return trained_models


def evaluate_models(trained_models, X_test, y_test, class_names):
    """Evaluate all trained models and return comparison dataframe."""
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    results = []

    for name, model in trained_models.items():
        y_pred = model.predict(X_test)

        # Get probabilities if available
        y_proba = None
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        results.append({
            'Model': name,
            'Accuracy': round(accuracy, 4),
            'Precision (Weighted)': round(precision, 4),
            'Recall (Weighted)': round(recall, 4),
            'F1-Score (Weighted)': round(f1, 4)
        })

        print(f"\n{'='*40}")
        print(f"MODEL: {name}")
        print(f"{'='*40}")
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred,
                                    target_names=class_names))

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('F1-Score (Weighted)', ascending=False)
    return results_df


def plot_confusion_matrices(trained_models, X_test, y_test, class_names,
                            output_dir):
    """Plot confusion matrices for all models."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for ax, (name, model) in zip(axes, trained_models.items()):
        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                    xticklabels=class_names, yticklabels=class_names)
        ax.set_title(f'{name}\nConfusion Matrix', fontsize=14, fontweight='bold')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/confusion_matrices.png', dpi=100)
    plt.close()
    print(f"\nConfusion matrices saved to: {output_dir}/confusion_matrices.png")


def cross_validate_models(trained_models, X_train, y_train, cv=5):
    """Perform cross-validation for more robust evaluation."""
    print("\n" + "=" * 60)
    print("CROSS-VALIDATION")
    print("=" * 60)

    cv_results = []
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    for name, model in trained_models.items():
        scores = cross_val_score(model, X_train, y_train, cv=skf,
                                 scoring='accuracy')
        cv_results.append({
            'Model': name,
            'CV Mean Accuracy': round(scores.mean(), 4),
            'CV Std': round(scores.std(), 4)
        })
        print(f"{name:25s} | CV Accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")

    return pd.DataFrame(cv_results)


def save_best_model(trained_models, results_df, models_dir):
    """Save the best performing model."""
    best_model_name = results_df.iloc[0]['Model']
    best_model = trained_models[best_model_name]

    model_path = os.path.join(models_dir, 'student_performance_model.pkl')
    joblib.dump(best_model, model_path)

    print(f"\n{'='*60}")
    print(f"BEST MODEL: {best_model_name}")
    print(f"Saved to: {model_path}")
    print(f"{'='*60}")
    return best_model, best_model_name


def plot_feature_importance(best_model, feature_names, output_dir):
    """Plot feature importance if the model supports it."""
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1][:15]

        plt.figure(figsize=(12, 8))
        plt.barh(range(len(indices)), importances[indices][::-1],
                 color='steelblue')
        plt.yticks(range(len(indices)),
                   [feature_names[i] for i in indices][::-1])
        plt.xlabel('Feature Importance')
        plt.title('Top 15 Feature Importance (Random Forest)',
                  fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/feature_importance.png', dpi=100)
        plt.close()
        print(f"Feature importance plot saved to: {output_dir}/feature_importance.png")

        print("\nTop 10 Most Important Features:")
        for i, idx in enumerate(indices[:10]):
            print(f"  {i+1}. {feature_names[idx]}: {importances[idx]:.4f}")
    else:
        # For Logistic Regression, use coefficients
        if hasattr(best_model, 'coef_'):
            coef = best_model.coef_
            avg_coef = np.mean(np.abs(coef), axis=0)
            indices = np.argsort(avg_coef)[::-1][:15]

            plt.figure(figsize=(12, 8))
            plt.barh(range(len(indices)), avg_coef[indices][::-1],
                     color='steelblue')
            plt.yticks(range(len(indices)),
                       [feature_names[i] for i in indices][::-1])
            plt.xlabel('Mean |Coefficient|')
            plt.title('Top 15 Feature Importance (Logistic Regression)',
                      fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/feature_importance.png', dpi=100)
            plt.close()
            print(f"Feature importance plot saved to: {output_dir}/feature_importance.png")


def main():
    """Main function to execute model training pipeline."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    processed_file = os.path.join(base_dir, 'dataset', 'processed',
                                  'student_data_cleaned.csv')
    preprocessor_file = os.path.join(base_dir, 'models', 'preprocessor.pkl')
    label_encoder_file = os.path.join(base_dir, 'models', 'label_encoder.pkl')
    models_dir = os.path.join(base_dir, 'models')
    reports_dir = os.path.join(base_dir, 'reports')
    comparison_file = os.path.join(models_dir, 'model_comparison.csv')

    os.makedirs(reports_dir, exist_ok=True)

    print("=" * 60)
    print("EXPLAINABLE AI - STUDENT PERFORMANCE PREDICTION")
    print("MODEL TRAINING & EVALUATION")
    print("=" * 60)

    # Step 1: Load processed data
    df = load_processed_data(processed_file)

    # Step 2: Load preprocessor and label encoder
    preprocessor = joblib.load(preprocessor_file)
    label_encoder = joblib.load(label_encoder_file)
    class_names = label_encoder.classes_
    print(f"Class names: {class_names}")

    # Step 3: Prepare features and target
    X, y, feature_cols = prepare_features_target(df)

    # Step 4: Apply preprocessing (scaling + encoding)
    categorical_features = ['Internet_Access', 'Extracurricular_Activities']
    numerical_features = [c for c in feature_cols if c not in categorical_features]

    X_processed = preprocessor.transform(df[feature_cols])

    # Get feature names after transformation
    num_features = numerical_features
    cat_features = preprocessor.named_transformers_['categorical'] \
        .named_steps['onehot'].get_feature_names_out(categorical_features)
    all_features = list(num_features) + list(cat_features)

    print(f"\nTotal features after preprocessing: {len(all_features)}")
    print(f"  Numerical: {len(num_features)}")
    print(f"  One-hot encoded: {len(cat_features)}")

    # Step 5: Split data
    X_train, X_test, y_train, y_test = split_data(X_processed, y)

    # Step 6: Train models
    trained_models = train_models(X_train, y_train)

    # Step 7: Evaluate models
    results_df = evaluate_models(trained_models, X_test, y_test, class_names)

    print("\n" + "=" * 60)
    print("MODEL COMPARISON TABLE")
    print("=" * 60)
    print(results_df.to_string(index=False))

    # Save comparison
    results_df.to_csv(comparison_file, index=False)
    print(f"\nModel comparison saved to: {comparison_file}")

    # Step 8: Cross-validation
    cv_results = cross_validate_models(trained_models, X_train, y_train)

    # Step 9: Plot confusion matrices
    plot_confusion_matrices(trained_models, X_test, y_test,
                            class_names, reports_dir)

    # Step 10: Save best model
    best_model, best_model_name = save_best_model(trained_models,
                                                  results_df, models_dir)

    # Step 11: Plot feature importance
    plot_feature_importance(best_model, all_features, reports_dir)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE - SUMMARY")
    print("=" * 60)
    print(f"  Models trained: {len(trained_models)}")
    print(f"  Best model: {best_model_name}")
    print(f"  Best F1-Score: {results_df.iloc[0]['F1-Score (Weighted)']:.4f}")
    print(f"  Best Accuracy: {results_df.iloc[0]['Accuracy']:.4f}")
    print("\n  Files saved:")
    print(f"    - models/student_performance_model.pkl (best model)")
    print(f"    - models/model_comparison.csv")
    print(f"    - reports/confusion_matrices.png")
    print(f"    - reports/feature_importance.png")
    print("=" * 60)

    return best_model, results_df


if __name__ == "__main__":
    main()

