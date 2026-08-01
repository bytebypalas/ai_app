"""
=============================================================================
STEP 10: Enhanced Analytics Visualization with Plotly
=============================================================================
File: app/components/visualization.py
Purpose:
  - Display enhanced analytics dashboard with Plotly charts
  - Show performance distribution, feature importance, correlations
  - Model comparison visualization
  - Interactive charts with premium styling
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_data():
    """Load processed student data for analytics."""
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    data_path = os.path.join(base_dir, 'dataset', 'processed', 'student_data_cleaned.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return df
    return None


def get_summary_stats(df):
    """Calculate summary statistics from the data."""
    if df is None:
        return {}
    stats = {
        'total_students': len(df),
        'avg_attendance': round(df['Attendance_Percentage'].mean(), 1),
        'avg_study_hours': round(df['Study_Hours_Per_Day'].mean(), 1),
        'avg_prev_marks': round(df['Previous_Academic_Marks'].mean(), 1),
        'avg_internal': round(df['Internal_Assessment_Marks'].mean(), 1),
        'avg_assignment': round(df['Assignment_Score'].mean(), 1),
        'avg_lab': round(df['Practical_Lab_Score'].mean(), 1),
        'avg_backlogs': round(df['Number_of_Backlogs'].mean(), 1),
        'avg_gpa': round(df['Previous_Semester_GPA'].mean(), 1),
        'avg_sleep': round(df['Sleep_Hours'].mean(), 1),
        'avg_participation': round(df['Class_Participation'].mean(), 1),
        'avg_submission': round(df['Assignment_Submission_Rate'].mean(), 1),
        'excellent_pct': round(len(df[df['Performance_Category'] == 'Excellent']) / len(df) * 100, 1),
        'good_pct': round(len(df[df['Performance_Category'] == 'Good']) / len(df) * 100, 1),
        'average_pct': round(len(df[df['Performance_Category'] == 'Average']) / len(df) * 100, 1),
        'poor_pct': round(len(df[df['Performance_Category'] == 'Poor']) / len(df) * 100, 1),
    }
    if 'Overall_Academic_Score' in df.columns:
        stats['avg_academic_score'] = round(df['Overall_Academic_Score'].mean(), 1)
    return stats


def display_analytics_dashboard():
    """Render enhanced analytics dashboard with Plotly visualizations."""
    df = load_data()
    if df is None:
        st.warning("No processed data found. Please run preprocessing first.")
        st.info("Run: python dataset/generate_data.py && python src/data_preprocessing.py && python src/train_model.py")
        return

    stats = get_summary_stats(df)

    st.markdown(f"""
    <div style="background:rgba(99,102,241,0.05);padding:20px;border-radius:16px;border:1px solid rgba(99,102,241,0.15);margin-bottom:25px;">
        <h2 style="color:#F1F5F9;margin:0;">Analytics Dashboard</h2>
        <p style="color:#94A3B8;margin:5px 0 0;">Explore patterns from {stats['total_students']} student records</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Students", stats['total_students'])
    with col2: st.metric("Avg Attendance", f"{stats['avg_attendance']}%")
    with col3: st.metric("Avg Study Hours", f"{stats['avg_study_hours']} hrs")
    with col4: st.metric("Avg GPA", f"{stats['avg_gpa']}/10")

    col1, col2 = st.columns([3, 2])
    with col1:
        perf_counts = df['Performance_Category'].value_counts().reset_index()
        perf_counts.columns = ['Category', 'Count']
        color_map = {'Poor': '#F43F5E', 'Average': '#F59E0B', 'Good': '#6366F1', 'Excellent': '#10B981'}
        fig = px.bar(perf_counts, x='Category', y='Count', color='Category', color_discrete_map=color_map, text='Count', title="Performance Distribution")
        fig.update_traces(textposition='outside', textfont_size=14)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch', key="dist_bar")

    with col2:
        fig = px.pie(perf_counts, values='Count', names='Category', color='Category', color_discrete_map=color_map, hole=0.4, title="Performance Breakdown")
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_color='white')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch', key="dist_pie")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(df, x='Attendance_Percentage', y='Overall_Academic_Score' if 'Overall_Academic_Score' in df.columns else 'Previous_Academic_Marks', color='Performance_Category', color_discrete_map=color_map, title="Attendance vs Performance", opacity=0.6)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350)
        st.plotly_chart(fig, width='stretch', key="att_scatter")

    with col2:
        fig = px.box(df, x='Performance_Category', y='Study_Hours_Per_Day', color='Performance_Category', color_discrete_map=color_map, title="Study Hours Distribution")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch', key="study_box")

    col1, col2 = st.columns(2)
    with col1:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        exclude_cols = ['Performance_Label', 'Parental_Education']
        corr_cols = [c for c in numeric_cols if c not in exclude_cols][:10]
        corr_matrix = df[corr_cols].corr()
        fig = go.Figure(data=go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns, colorscale='RdBu_r', zmid=0, text=np.round(corr_matrix.values, 2), texttemplate='%{text}', textfont_size=9))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', height=400)
        st.plotly_chart(fig, width='stretch', key="corr_heatmap")

    with col2:
        fig = px.box(df, x='Performance_Category', y='Number_of_Backlogs', color='Performance_Category', color_discrete_map=color_map, title="Backlogs Distribution")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch', key="backlog_box")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.violin(df, x='Performance_Category', y='Previous_Semester_GPA', color='Performance_Category', color_discrete_map=color_map, title="GPA Distribution", box=True, points=False)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch', key="gpa_violin")

    with col2:
        fig = px.box(df, x='Performance_Category', y='Class_Participation', color='Performance_Category', color_discrete_map=color_map, title="Participation Distribution")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch', key="part_box")

    try:
        from xai.feature_importance import load_model_for_importance, get_feature_importance_df
        model, feat_names, X_sample = load_model_for_importance()
        feat_df = get_feature_importance_df(model, feat_names)
        fig = px.bar(feat_df.head(12), x='Importance', y='Feature', orientation='h', title="Feature Importance", color='Importance', color_continuous_scale=['#6366F1', '#8B5CF6', '#A78BFA'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=400, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch', key="feature_imp")
    except Exception as e:
        st.info(f"Feature importance: {e}")


def display_model_comparison():
    """Display model performance comparison."""
    st.markdown("### Model Performance Comparison")
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'models')
    comp_file = os.path.join(models_dir, 'model_comparison.csv')
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'reports')

    if os.path.exists(comp_file):
        comp_df = pd.read_csv(comp_file)
        st.dataframe(comp_df, width='stretch', hide_index=True)

        if 'Model' in comp_df.columns and 'Accuracy' in comp_df.columns:
            fig = px.bar(comp_df, x='Model', y='Accuracy', color='Model', title="Model Accuracy Comparison", text='Accuracy')
            fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#94A3B8', title_font_color='#F1F5F9', height=350, showlegend=False)
            st.plotly_chart(fig, width='stretch', key="model_comp")

        cm_file = os.path.join(reports_dir, 'confusion_matrices.png')
        if os.path.exists(cm_file):
            st.image(cm_file, width='stretch', caption="Confusion Matrices")
    else:
        st.info("Model comparison data not available. Run train_model.py first.")
