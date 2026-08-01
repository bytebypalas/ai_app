"""
=============================================================================
STEP 7: Complete Enhanced Streamlit Application
=============================================================================
File: streamlit_app.py (moved to root to avoid package conflict with app/)
Purpose:
  - Main Streamlit web application with premium UI
  - Pages: Home, Prediction, XAI, Analytics, History, About
  - Integrates prediction, XAI, analytics, history, export modules
  - Dark navy theme with glassmorphism

Run: streamlit run streamlit_app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import warnings
import json
from datetime import datetime
from io import BytesIO
import base64

warnings.filterwarnings('ignore')

# ============================================================================
# MODULE IMPORTS - Direct imports to avoid circular imports
# ============================================================================

from xai.shap_analysis import (
    load_artifacts,
    prepare_input_features,
    explain_prediction,
    create_human_readable_explanation,
    get_global_feature_importance
)
from src.predict import predict_student, prepare_student_input
from src.evaluate import evaluate_model, cross_validate, generate_evaluation_report
from xai.explanation import generate_explanation, generate_recommendations, generate_report_content
from xai.feature_importance import get_feature_importance_df, load_model_for_importance

# Import directly from dashboard module (not via app/__init__.py to avoid circular imports)
from app.dashboard import (
    load_custom_css, render_metric_card, render_circular_progress,
    render_status_badge, render_dashboard, render_about,
    render_history_section, init_history, add_to_history, get_history_df,
    create_performance_gauge, create_feature_importance_chart,
    create_performance_distribution_chart, create_radar_chart,
    create_probability_chart, generate_pdf_report, get_pdf_download_link,
    export_history_csv
)
from app.components.prediction import student_input_form, display_prediction_result, validate_inputs
from app.components.explanation import display_shap_explanation, display_global_feature_importance
from app.components.visualization import display_analytics_dashboard, display_model_comparison


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="XAI Student Performance Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar():
    """Render the sidebar with navigation and branding."""
    with st.sidebar:
        # Logo and branding
        st.markdown("""
        <div style="text-align:center; padding:20px 10px;">
            <div style="width:60px;height:60px;border-radius:16px;background:linear-gradient(135deg, #6366F1, #8B5CF6);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;box-shadow:0 4px 20px rgba(99,102,241,0.3);">
                <span style="font-size:28px;">🎓</span>
            </div>
            <h2 style="color:#F1F5F9; margin:0; font-size:20px;">StudentXAI</h2>
            <p style="color:#94A3B8; font-size:11px; margin:2px 0 0;">Explainable AI Prediction</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(99,102,241,0.1);'>", unsafe_allow_html=True)

        if 'prediction_history' in st.session_state:
            total_preds = len(st.session_state.prediction_history)
        else:
            total_preds = 0

        st.markdown(f"""
        <div style="display:flex; justify-content:space-around; text-align:center; margin:10px 0;">
            <div><p style="color:#818CF8; font-size:18px; font-weight:700; margin:0;">{total_preds}</p><p style="color:#64748B; font-size:10px; margin:0;">Predictions</p></div>
            <div><p style="color:#10B981; font-size:18px; font-weight:700; margin:0;">{datetime.now().strftime('%b')}</p><p style="color:#64748B; font-size:10px; margin:0;">Month</p></div>
            <div><p style="color:#F59E0B; font-size:18px; font-weight:700; margin:0;">v2.0</p><p style="color:#64748B; font-size:10px; margin:0;">Version</p></div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(99,102,241,0.1);'>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; padding:10px 0;">
            <p style="color:#475569; font-size:10px;">B.Tech Final Year Project<br>Explainable AI Based Student<br>Academic Performance Prediction</p>
            <p style="color:#334155; font-size:9px; margin-top:5px;">© 2024-2025 | All Rights Reserved</p>
        </div>
        """, unsafe_allow_html=True)

        return "🏠 Home"


# ============================================================================
# MODEL LOADING
# ============================================================================

@st.cache_resource
def load_model_artifacts_cached():
    """Load model artifacts with caching."""
    try:
        model, preprocessor, label_encoder = load_artifacts()
        return model, preprocessor, label_encoder
    except Exception as e:
        return None, None, None


# ============================================================================
# PAGES
# ============================================================================

def home_page():
    """Render the Home page with hero section and features."""
    st.markdown("""
    <div style="background:linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));padding:40px;border-radius:24px;border:1px solid rgba(99,102,241,0.15);text-align:center;margin-bottom:30px;">
        <h1 style="font-size:2.8rem;font-weight:800;color:#F1F5F9;margin:0 0 10px;">Predict Student Academic Performance</h1>
        <h1 style="font-size:2.8rem;font-weight:800;margin:0 0 20px;">Using <span class="gradient-text">Explainable AI</span></h1>
        <p style="color:#94A3B8;font-size:1.1rem;max-width:700px;margin:0 auto 30px;line-height:1.6;">Analyze student academic data, estimate predicted percentage, explain every prediction using Explainable AI (SHAP), and provide personalized recommendations for improvement.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: render_metric_card("Students Analyzed", "1,200+", "+12%", "indigo", "purple")
    with col2: render_metric_card("Average Accuracy", "94.2%", "+5.2%", "emerald", "green")
    with col3: render_metric_card("Predictions Made", str(max(0, len(st.session_state.get('prediction_history', [])))), "+3.8%", "cyan", "blue")
    with col4: render_metric_card("Model Confidence", "96%", "+8.1%", "amber", "orange")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;margin:40px 0 30px;'><h2 style='color:#F1F5F9;font-size:2rem;'>Powerful Features for <span class='gradient-text'>Accurate Predictions</span></h2><p style='color:#94A3B8;max-width:600px;margin:10px auto 0;'>Our platform combines cutting-edge ML with transparent SHAP explanations to deliver actionable insights.</p></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='glass-card' style='text-align:center;padding:30px 20px;'><div style='width:56px;height:56px;border-radius:14px;background:linear-gradient(135deg,#06B6D4,#3B82F6);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;'><span style='font-size:24px;'>⚡</span></div><h3 style='color:#F1F5F9;margin:0 0 8px;'>Instant Prediction</h3><p style='color:#94A3B8;font-size:13px;line-height:1.5;'>Get real-time academic performance predictions with our trained ML model. Results in milliseconds.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='glass-card' style='text-align:center;padding:30px 20px;'><div style='width:56px;height:56px;border-radius:14px;background:linear-gradient(135deg,#10B981,#34D399);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;'><span style='font-size:24px;'>🛡️</span></div><h3 style='color:#F1F5F9;margin:0 0 8px;'>Transparent AI</h3><p style='color:#94A3B8;font-size:13px;line-height:1.5;'>Every prediction comes with SHAP-based explanations. Understand exactly which factors influenced the result.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='glass-card' style='text-align:center;padding:30px 20px;'><div style='width:56px;height:56px;border-radius:14px;background:linear-gradient(135deg,#8B5CF6,#EC4899);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;'><span style='font-size:24px;'>💡</span></div><h3 style='color:#F1F5F9;margin:0 0 8px;'>Actionable Insights</h3><p style='color:#94A3B8;font-size:13px;line-height:1.5;'>Receive personalized recommendations to improve academic performance. Know exactly what areas need attention.</p></div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;margin:50px 0 30px;'><h2 style='color:#F1F5F9;font-size:2rem;'>How It <span class='gradient-text'>Works</span></h2><p style='color:#94A3B8;max-width:500px;margin:10px auto 0;'>Three simple steps to get transparent, explainable predictions.</p></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    for col, icon, title, desc in [
        (col1, "📝", "Input Student Data", "Enter academic records, study habits, and personal factors through our intuitive form with sliders and dropdowns."),
        (col2, "⚡", "Predict & Explain", "Our ML model analyzes 14+ features to generate predictions. SHAP explains every factor's contribution."),
        (col3, "🎯", "Get Recommendations", "Receive personalized, actionable recommendations to improve performance based on identified weak areas.")
    ]:
        with col:
            st.markdown(f"<div style='text-align:center;padding:20px;'><div style='width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#8B5CF6);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;'><span style='font-size:32px;'>{icon}</span></div><h3 style='color:#F1F5F9;margin:0 0 8px;'>{title}</h3><p style='color:#94A3B8;font-size:13px;'>{desc}</p></div>", unsafe_allow_html=True)


def prediction_page():
    """Render the Prediction page with form and results."""
    st.markdown("<div style='background:rgba(99,102,241,0.05);padding:15px 20px;border-radius:16px;border:1px solid rgba(99,102,241,0.15);margin-bottom:25px;'><h2 style='color:#F1F5F9;margin:0;display:flex;align-items:center;gap:10px;'>🎯 Predict Performance</h2><p style='color:#94A3B8;margin:5px 0 0;'>Enter student details below to get an instant, explainable performance prediction</p></div>", unsafe_allow_html=True)

    model, preprocessor, label_encoder = load_model_artifacts_cached()

    if model is None:
        st.error("⚠️ Model artifacts not found! Run the pipeline first.")
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        student_data = student_input_form()
        st.markdown("<br>", unsafe_allow_html=True)
        predict_clicked = st.button("🎯 Predict Performance", type="primary", width='stretch')

    with col2:
        if predict_clicked and student_data:
            with st.spinner("🔍 Analyzing student data with ML model..."):
                try:
                    prediction_result = predict_student(student_data, model, preprocessor, label_encoder)
                    shap_result = explain_prediction(model, preprocessor, label_encoder, student_data)

                    init_history()
                    add_to_history(student_data, prediction_result)

                    st.session_state['last_prediction'] = prediction_result
                    st.session_state['last_student_input'] = student_data
                    st.session_state['last_shap_result'] = shap_result

                    # Display student name header
                    student_name = student_data.get('Student_Name', 'Unnamed Student')
                    st.markdown(f"""
                    <div style="background:rgba(99,102,241,0.08); padding:12px 20px; border-radius:16px;
                                border:1px solid rgba(99,102,241,0.2); margin-bottom:15px;
                                display:flex; align-items:center; gap:12px;">
                        <div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#6366F1,#8B5CF6);
                                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                            <span style="font-size:20px;">👤</span>
                        </div>
                        <div>
                            <p style="color:#94A3B8; font-size:12px; margin:0;">Student</p>
                            <p style="color:#F1F5F9; font-size:20px; font-weight:700; margin:0;">{student_name}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    display_prediction_result(prediction_result, student_data)

                    st.markdown("<br><div class='glass-card'>", unsafe_allow_html=True)
                    st.markdown("### 📄 Generate Report")
                    explanation = generate_explanation(prediction_result, shap_result)
                    recommendations = generate_recommendations(student_data, prediction_result)
                    explanation_text = explanation.get('summary', 'N/A')

                    if st.button("📄 Download PDF Report", width='stretch'):
                        pdf_bytes = generate_pdf_report(student_data, prediction_result, explanation_text, recommendations)
                        if pdf_bytes:
                            pdf_link = get_pdf_download_link(pdf_bytes)
                            st.markdown(pdf_link, unsafe_allow_html=True)
                        else:
                            st.error("PDF generation failed. Check fpdf2 installation.")

                    st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.markdown("<div class='glass-card' style='display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:400px;text-align:center;padding:40px;'><div style='width:80px;height:80px;border-radius:50%;background:rgba(99,102,241,0.1);display:flex;align-items:center;justify-content:center;margin-bottom:20px;'><span style='font-size:36px;'>🎯</span></div><h3 style='color:#F1F5F9;margin:0 0 10px;'>Ready to Predict</h3><p style='color:#94A3B8;max-width:350px;margin:0;'>Fill in the student details on the left and click <strong>Predict Performance</strong>.</p></div>", unsafe_allow_html=True)


def xai_page():
    """Render the Explainable AI page."""
    st.markdown("<div style='background:rgba(99,102,241,0.05);padding:15px 20px;border-radius:16px;border:1px solid rgba(99,102,241,0.15);margin-bottom:25px;'><h2 style='color:#F1F5F9;margin:0;display:flex;align-items:center;gap:10px;'>🔍 Explainable AI Analysis</h2></div>", unsafe_allow_html=True)

    if 'last_prediction' not in st.session_state:
        st.info("💡 No recent prediction found. Make a prediction first on the Predict page.")
        return

    prediction_result = st.session_state['last_prediction']
    shap_result = st.session_state['last_shap_result']
    student_input = st.session_state['last_student_input']

    col1, col2, col3, col4 = st.columns(4)
    with col1: render_metric_card("Predicted %", f"{prediction_result.get('predicted_percentage', 0):.1f}%", None, "indigo", "purple")
    with col2: render_metric_card("Grade", prediction_result.get('grade', 'N/A'), None, "emerald", "green")
    with col3: render_metric_card("Confidence", f"{prediction_result.get('confidence', 0):.1f}%", None, "cyan", "blue")
    with col4:
        risk = prediction_result.get('risk_level', 'N/A')
        risk_color = "emerald" if "Low" in risk else ("amber" if "Medium" in risk else "rose")
        render_metric_card("Risk Level", risk, None, risk_color, "orange")

    st.markdown("<br>", unsafe_allow_html=True)
    display_shap_explanation(shap_result, student_input)

    try:
        model, preprocessor, label_encoder = load_model_artifacts_cached()
        if model:
            data_path = os.path.join('dataset', 'processed', 'student_data_cleaned.csv')
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
                numerical_features = ['Attendance_Percentage', 'Study_Hours_Per_Day', 'Previous_Academic_Marks', 'Internal_Assessment_Marks', 'Assignment_Score', 'Practical_Lab_Score', 'Number_of_Backlogs', 'Previous_Semester_GPA', 'Sleep_Hours', 'Class_Participation', 'Assignment_Submission_Rate', 'Academic_Consistency', 'Overall_Academic_Score', 'Engagement_Score', 'Study_Efficiency']
                categorical_features = ['Internet_Access', 'Extracurricular_Activities']
                feature_cols = numerical_features + categorical_features
                X_sample = preprocessor.transform(df[feature_cols][:100])
                global_importance = get_global_feature_importance(model, preprocessor, X_sample)
                display_global_feature_importance(global_importance)
    except Exception as e:
        st.info(f"Global feature importance: {e}")


def analytics_page():
    """Render the Analytics dashboard page."""
    display_analytics_dashboard()
    st.markdown("---")
    display_model_comparison()


def history_page():
    """Render the Prediction History page."""
    st.markdown("<div style='background:rgba(99,102,241,0.05);padding:15px 20px;border-radius:16px;border:1px solid rgba(99,102,241,0.15);margin-bottom:25px;'><h2 style='color:#F1F5F9;margin:0;display:flex;align-items:center;gap:10px;'>📋 Prediction History</h2></div>", unsafe_allow_html=True)

    init_history()
    render_history_section()

    history_df = get_history_df()
    if not history_df.empty:
        st.markdown("<br><div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📤 Export Options")
        export_link = export_history_csv()
        if export_link:
            st.markdown(export_link, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def about_page():
    """Render the About page."""
    render_about()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application controller with top navigation tabs."""
    init_history()

    # Render sidebar branding
    render_sidebar()

    # Top navigation tabs
    st.markdown("<div style='margin-bottom:20px;'>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Home", "🎯 Predict", "🔍 Explainable AI", "📊 Analytics", "📋 History", "📚 About"])

    with tab1:
        home_page()
    with tab2:
        prediction_page()
    with tab3:
        xai_page()
    with tab4:
        analytics_page()
    with tab5:
        history_page()
    with tab6:
        about_page()
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
