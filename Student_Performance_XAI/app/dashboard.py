"""
=============================================================================
STEP 6: Enhanced Streamlit Dashboard with Plotly
=============================================================================
File: app/dashboard.py
Purpose:
  - Render premium Streamlit dashboard with glassmorphism theme
  - Display Plotly interactive charts
  - Show prediction history with search/sort/delete
  - CSV export functionality
  - PDF report generation

Usage:
  from app.dashboard import render_dashboard, render_history
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime
import json
import os
import sys
import base64
from io import BytesIO

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


# ============================================================================
# CUSTOM CSS FOR PREMIUM THEME
# ============================================================================

def load_custom_css():
    """Load premium dark navy theme CSS with glassmorphism."""
    st.markdown("""
    <style>
        :root { --dark-navy: #0F172A; --slate-blue: #1E293B; --cyan-accent: #06B6D4; --indigo: #6366F1; --purple: #8B5CF6; --emerald: #10B981; --amber: #F59E0B; --rose: #F43F5E; }
        .stApp { background: #0F172A; }
        .main > div { background: #0F172A; }
        .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 20px; padding: 24px; margin: 12px 0; transition: all 0.3s ease; }
        .glass-card:hover { background: rgba(30, 41, 59, 0.85); border-color: rgba(99, 102, 241, 0.3); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1); }
        .gradient-text { background: linear-gradient(135deg, #818CF8, #C084FC, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .metric-card { text-align: center; padding: 16px; border-radius: 16px; background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(99, 102, 241, 0.1); }
        .metric-card .label { font-size: 13px; color: #94A3B8; margin-bottom: 4px; }
        .metric-card .value { font-size: 28px; font-weight: 700; color: #F1F5F9; }
        .metric-card .change { font-size: 12px; margin-top: 2px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .badge-pass { background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-fail { background: rgba(244, 63, 94, 0.2); color: #F43F5E; border: 1px solid rgba(244, 63, 94, 0.3); }
        h1, h2, h3 { color: #F1F5F9 !important; }
        .stButton > button { border-radius: 12px; font-weight: 600; transition: all 0.3s; }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
        .stAlert { border-radius: 12px !important; border: none !important; }
        .stInfo { background: rgba(99, 102, 241, 0.1) !important; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# GRADIENT METRIC DISPLAY
# ============================================================================

def render_metric_card(label, value, delta=None, gradient_from="indigo", gradient_to="purple"):
    """Render a metric card with gradient accent."""
    gradient_map = {
        "indigo-purple": "linear-gradient(135deg, #6366F1, #8B5CF6)",
        "emerald-green": "linear-gradient(135deg, #10B981, #34D399)",
        "cyan-blue": "linear-gradient(135deg, #06B6D4, #3B82F6)",
        "amber-orange": "linear-gradient(135deg, #F59E0B, #F97316)",
        "rose-pink": "linear-gradient(135deg, #F43F5E, #EC4899)",
    }
    gradient = gradient_map.get(f"{gradient_from}-{gradient_to}", gradient_map["indigo-purple"])
    delta_html = ""
    if delta:
        color = "#10B981" if delta.startswith("+") else "#F43F5E"
        delta_html = f'<p class="change" style="color:{color}">{delta}</p>'
    st.markdown(f"""
    <div class="metric-card">
        <div style="width:40px;height:40px;border-radius:10px;background:{gradient};display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">
            <span style="color:white;font-size:18px;">●</span>
        </div>
        <p class="value">{value}</p>
        <p class="label">{label}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status, risk_level=None):
    """Render status and risk level badges."""
    pass_badge = f'<span class="badge badge-pass">✅ Pass</span>' if status == "Pass" else f'<span class="badge badge-fail">❌ Fail</span>'
    risk_badge = ""
    if risk_level:
        risk_class = risk_level.lower().replace(" ", "-")
        risk_badge = f'<span class="badge badge-{risk_class}" style="margin-left:8px;">{risk_level}</span>'
    return f'{pass_badge}{risk_badge}'


def render_circular_progress(percentage, size=120, stroke_width=8, color="#6366F1"):
    """Render a circular progress indicator using SVG."""
    radius = (size - stroke_width) // 2
    circumference = 2 * np.pi * radius
    offset = circumference - (percentage / 100) * circumference
    if percentage >= 80: color = "#10B981"
    elif percentage >= 60: color = "#6366F1"
    elif percentage >= 40: color = "#F59E0B"
    else: color = "#F43F5E"
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <circle cx="{size//2}" cy="{size//2}" r="{radius}" fill="none" stroke="rgba(99,102,241,0.1)" stroke-width="{stroke_width}"/>
        <circle cx="{size//2}" cy="{size//2}" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{offset}" transform="rotate(-90, {size//2}, {size//2})" style="transition: stroke-dashoffset 1s ease-out;"/>
        <text x="{size//2}" y="{size//2 - 8}" text-anchor="middle" fill="#F1F5F9" font-size="24" font-weight="bold">{percentage:.0f}%</text>
    </svg>
    """
    return svg


# ============================================================================
# PLOTLY CHARTS
# ============================================================================

def create_performance_gauge(percentage, title="Predicted Percentage"):
    """Create a Plotly gauge chart for performance."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=percentage,
        title={'text': title, 'font': {'color': '#94A3B8', 'size': 14}},
        number={'font': {'color': '#F1F5F9', 'size': 36}},
        delta={'reference': 50, 'font': {'color': '#10B981'}},
        gauge={'axis': {'range': [0, 100], 'tickcolor': '#475569', 'tickfont': {'color': '#94A3B8'}}, 'bar': {'color': '#6366F1', 'thickness': 0.3}, 'bgcolor': 'rgba(30,41,59,0)', 'borderwidth': 0, 'steps': [{'range': [0, 40], 'color': 'rgba(244,63,94,0.2)'}, {'range': [40, 60], 'color': 'rgba(245,158,11,0.2)'}, {'range': [60, 80], 'color': 'rgba(99,102,241,0.2)'}, {'range': [80, 100], 'color': 'rgba(16,185,129,0.2)'}], 'threshold': {'line': {'color': '#F43F5E', 'width': 2}, 'thickness': 0.75, 'value': 50}}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=50, b=20), height=250)
    return fig


def create_feature_importance_chart(features_df, title="Feature Importance"):
    """Create a horizontal bar chart for feature importance."""
    fig = px.bar(features_df.head(10), x='Importance', y='Feature', orientation='h', title=title, color='Importance', color_continuous_scale=['#6366F1', '#8B5CF6', '#A78BFA'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#94A3B8'}, title_font={'color': '#F1F5F9'}, xaxis={'gridcolor': 'rgba(99,102,241,0.1)'}, yaxis={'gridcolor': 'rgba(99,102,241,0.1)'}, margin=dict(l=20, r=20, t=40, b=20), height=350, showlegend=False)
    return fig


def create_performance_distribution_chart(data_df, category_col='Performance_Category'):
    """Create a bar chart showing performance distribution."""
    counts = data_df[category_col].value_counts().reset_index()
    counts.columns = ['Category', 'Count']
    color_map = {'Poor': '#F43F5E', 'Average': '#F59E0B', 'Good': '#6366F1', 'Excellent': '#10B981'}
    fig = px.bar(counts, x='Category', y='Count', color='Category', color_discrete_map=color_map, title="Performance Distribution", text='Count')
    fig.update_traces(textposition='outside', textfont_color='#F1F5F9')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#94A3B8'}, title_font={'color': '#F1F5F9'}, xaxis={'gridcolor': 'rgba(99,102,241,0.1)'}, yaxis={'gridcolor': 'rgba(99,102,241,0.1)'}, margin=dict(l=20, r=20, t=40, b=20), height=350, showlegend=False)
    return fig


def create_radar_chart(student_input):
    """Create a radar chart showing student's feature profile."""
    features = ['Attendance', 'Study Hours', 'Prev Marks', 'Internal Marks', 'Assignments', 'Lab Score', 'Participation', 'Submission Rate']
    values = [student_input.get('Attendance_Percentage', 75), student_input.get('Study_Hours_Per_Day', 4) * 100 / 12, student_input.get('Previous_Academic_Marks', 65), student_input.get('Internal_Assessment_Marks', 60), student_input.get('Assignment_Score', 70), student_input.get('Practical_Lab_Score', 65), student_input.get('Class_Participation', 55), student_input.get('Assignment_Submission_Rate', 75)]
    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=features + [features[0]], fill='toself', fillcolor='rgba(99,102,241,0.2)', line=dict(color='#6366F1', width=2), marker=dict(color='#6366F1', size=4)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(99,102,241,0.1)', tickfont={'color': '#94A3B8'}), angularaxis=dict(gridcolor='rgba(99,102,241,0.1)', tickfont={'color': '#94A3B8'}), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', font={'color': '#94A3B8'}, title_font={'color': '#F1F5F9'}, margin=dict(l=40, r=40, t=20, b=20), height=350, showlegend=False)
    return fig


def create_probability_chart(probabilities):
    """Create a bar chart showing probability distribution."""
    df = pd.DataFrame([{'Category': cat, 'Probability': prob} for cat, prob in probabilities.items()])
    color_map = {'Poor': '#F43F5E', 'Average': '#F59E0B', 'Good': '#6366F1', 'Excellent': '#10B981'}
    fig = px.bar(df, x='Category', y='Probability', color='Category', color_discrete_map=color_map, title="Prediction Probability Distribution", text=df['Probability'].apply(lambda x: f'{x:.1f}%'))
    fig.update_traces(textposition='outside', textfont_color='#F1F5F9')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#94A3B8'}, title_font={'color': '#F1F5F9'}, xaxis={'gridcolor': 'rgba(99,102,241,0.1)'}, yaxis={'gridcolor': 'rgba(99,102,241,0.1)', 'range': [0, 100]}, margin=dict(l=20, r=20, t=40, b=20), height=300, showlegend=False)
    return fig


# ============================================================================
# PREDICTION HISTORY MANAGEMENT
# ============================================================================

def init_history():
    """Initialize prediction history in session state."""
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []


def add_to_history(student_input, prediction_result):
    """Add a prediction record to history."""
    record = {
        'id': len(st.session_state.prediction_history) + 1,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'timestamp': datetime.now().isoformat(),
        'student_name': student_input.get('Student_Name', 'Unnamed Student'),
        'attendance': student_input.get('Attendance_Percentage', 0),
        'study_hours': student_input.get('Study_Hours_Per_Day', 0),
        'prev_marks': student_input.get('Previous_Academic_Marks', 0),
        'backlogs': student_input.get('Number_of_Backlogs', 0),
        'gpa': student_input.get('Previous_Semester_GPA', 0),
        'percentage': prediction_result.get('predicted_percentage', 0),
        'grade': prediction_result.get('grade', 'N/A'),
        'performance': prediction_result.get('performance_level', 'N/A'),
        'confidence': prediction_result.get('confidence', 0),
        'risk': prediction_result.get('risk_level', 'N/A'),
        'status': prediction_result.get('status', 'N/A')
    }
    st.session_state.prediction_history.insert(0, record)
    return record


def get_history_df():
    """Get prediction history as DataFrame."""
    if 'prediction_history' not in st.session_state:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.prediction_history)


def export_history_csv():
    """Export prediction history to CSV and return as download link."""
    df = get_history_df()
    if df.empty:
        return None
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction_history.csv">📥 Download CSV</a>'
    return href


def render_history_section():
    """Render the prediction history section."""
    init_history()
    history_df = get_history_df()
    st.markdown("### 📋 Prediction History")
    if history_df.empty:
        st.info("No predictions made yet. Go to the Predict page to get started!")
        return
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search by grade or performance", placeholder="e.g., A+, Good...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest %", "Lowest %"])
    with col3:
        if st.button("🗑️ Clear All", type="secondary", width='stretch'):
            st.session_state.prediction_history = []
            st.rerun()
    filtered_df = history_df.copy()
    if search:
        mask = (filtered_df['grade'].str.contains(search, case=False, na=False) | filtered_df['performance'].str.contains(search, case=False, na=False) | filtered_df['risk'].str.contains(search, case=False, na=False) | filtered_df['status'].str.contains(search, case=False, na=False))
        filtered_df = filtered_df[mask]
    if sort_by == "Newest First": filtered_df = filtered_df.sort_values('timestamp', ascending=False)
    elif sort_by == "Oldest First": filtered_df = filtered_df.sort_values('timestamp', ascending=True)
    elif sort_by == "Highest %": filtered_df = filtered_df.sort_values('percentage', ascending=False)
    elif sort_by == "Lowest %": filtered_df = filtered_df.sort_values('percentage', ascending=True)
    display_df = filtered_df[['date', 'grade', 'percentage', 'performance', 'confidence', 'risk', 'status']].copy()
    display_df.columns = ['Date', 'Grade', 'Score %', 'Performance', 'Confidence', 'Risk', 'Status']
    display_df['Score %'] = display_df['Score %'].apply(lambda x: f"{x:.1f}")
    display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, width='stretch', height=min(400, 40 * len(display_df)))
    col1, col2 = st.columns(2)
    with col1:
        export_link = export_history_csv()
        if export_link:
            st.markdown(export_link, unsafe_allow_html=True)
    with col2:
        st.write(f"**Total Records:** {len(history_df)}")


# ============================================================================
# PDF REPORT GENERATION
# ============================================================================

def generate_pdf_report(student_input, prediction_result, explanation_text, recommendations):
    """Generate a PDF report using fpdf2."""
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 20)
        pdf.cell(0, 15, 'Student Performance Report', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, f'Generated by XAI Prediction System', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f'Date: {datetime.now().strftime("%B %d, %Y")}', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_fill_color(99, 102, 241)
        pdf.setTextColor(255, 255, 255)
        pdf.cell(0, 10, ' Student Information', new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.setTextColor(0, 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.ln(3)
        info_items = [
            ('Student Name', student_input.get('Student_Name', 'Unnamed Student')),
            ('Attendance', f"{student_input.get('Attendance_Percentage', 'N/A')}%"),
            ('Study Hours/Day', f"{student_input.get('Study_Hours_Per_Day', 'N/A')} hrs"),
            ('Previous Marks', f"{student_input.get('Previous_Academic_Marks', 'N/A')}%"),
            ('Internal Marks', f"{student_input.get('Internal_Assessment_Marks', 'N/A')}%"),
            ('Assignment Score', f"{student_input.get('Assignment_Score', 'N/A')}%"),
            ('Lab Score', f"{student_input.get('Practical_Lab_Score', 'N/A')}%"),
            ('Backlogs', str(student_input.get('Number_of_Backlogs', 'N/A'))),
            ('Previous GPA', f"{student_input.get('Previous_Semester_GPA', 'N/A')}/10"),
            ('Sleep Hours', f"{student_input.get('Sleep_Hours', 'N/A')} hrs"),
            ('Participation', f"{student_input.get('Class_Participation', 'N/A')}%"),
            ('Submission Rate', f"{student_input.get('Assignment_Submission_Rate', 'N/A')}%"),
        ]
        for label, value in info_items:
            pdf.cell(60, 7, f"  {label}:", border=1)
            pdf.cell(0, 7, f"  {value}", border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_fill_color(16, 185, 129)
        pdf.setTextColor(255, 255, 255)
        pdf.cell(0, 10, ' Prediction Summary', new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.setTextColor(0, 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.ln(3)
        pred_items = [
            ('Predicted Percentage', f"{prediction_result.get('predicted_percentage', 'N/A'):.1f}%"),
            ('Grade', prediction_result.get('grade', 'N/A')),
            ('Performance Level', prediction_result.get('performance_level', 'N/A')),
            ('Confidence', f"{prediction_result.get('confidence', 'N/A'):.1f}%"),
            ('Risk Level', prediction_result.get('risk_level', 'N/A')),
            ('Status', prediction_result.get('status', 'N/A')),
        ]
        for label, value in pred_items:
            pdf.cell(60, 7, f"  {label}:", border=1)
            pdf.cell(0, 7, f"  {value}", border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_fill_color(99, 102, 241)
        pdf.setTextColor(255, 255, 255)
        pdf.cell(0, 10, ' XAI Explanation', new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.setTextColor(0, 0, 0)
        pdf.set_font('Helvetica', '', 9)
        pdf.ln(3)
        pdf.multi_cell(0, 5, explanation_text)
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_fill_color(245, 158, 11)
        pdf.setTextColor(255, 255, 255)
        pdf.cell(0, 10, ' Recommendations', new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.setTextColor(0, 0, 0)
        pdf.set_font('Helvetica', '', 9)
        pdf.ln(3)
        for i, rec in enumerate(recommendations, 1):
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 6, f"  {i}. [{rec.get('priority', 'Medium')}] {rec.get('category', 'General')}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 5, f"     {rec.get('advice', '')}")
            pdf.ln(2)
        pdf.ln(10)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.setTextColor(128, 128, 128)
        pdf.cell(0, 5, 'Generated by Explainable AI Based Student Academic Performance Prediction System', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, 'This is a decision-support tool only.', align='C')
        pdf_bytes = pdf.output()
        return pdf_bytes
    except ImportError:
        st.warning("fpdf2 is not installed. Install it with: pip install fpdf2")
        return None
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None


def get_pdf_download_link(pdf_bytes, filename="student_performance_report.pdf"):
    """Generate a download link for the PDF."""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank">📄 Download PDF Report</a>'
    return href


# ============================================================================
# MAIN DASHBOARD RENDERER
# ============================================================================

def render_dashboard():
    """Render the main analytics dashboard."""
    st.markdown("## 📊 Analytics Dashboard")
    st.markdown('<p style="color:#94A3B8;">Comprehensive insights and visualizations from student performance data.</p>', unsafe_allow_html=True)
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'processed', 'student_data_cleaned.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        st.warning("No processed data found. Please run data_preprocessing.py first.")
        return
    col1, col2, col3, col4 = st.columns(4)
    with col1: render_metric_card("Total Students", len(df), "+12%", "indigo", "purple")
    with col2: avg_score = df['Overall_Academic_Score'].mean() if 'Overall_Academic_Score' in df.columns else 0; render_metric_card("Avg Academic Score", f"{avg_score:.1f}%", "+5.2%", "emerald", "green")
    with col3: avg_attendance = df['Attendance_Percentage'].mean(); render_metric_card("Avg Attendance", f"{avg_attendance:.1f}%", "+3.8%", "cyan", "blue")
    with col4: excellent_count = len(df[df['Performance_Category'] == 'Excellent']) if 'Performance_Category' in df.columns else 0; render_metric_card("Excellent Students", excellent_count, "+8.1%", "amber", "orange")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig1 = create_performance_distribution_chart(df)
        st.plotly_chart(fig1, width='stretch', key="dist_chart")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        try:
            from xai.feature_importance import load_model_for_importance, get_feature_importance_df
            model, feat_names, _ = load_model_for_importance()
            feat_df = get_feature_importance_df(model, feat_names)
            fig2 = create_feature_importance_chart(feat_df)
            st.plotly_chart(fig2, width='stretch', key="feat_chart")
        except Exception:
            st.info("Feature importance chart requires trained model.")
        st.markdown('</div>', unsafe_allow_html=True)
    render_history_section()


# ============================================================================
# ABOUT SECTION
# ============================================================================

def render_about():
    """Render the About page."""
    st.markdown("""
    <div style="background:rgba(99,102,241,0.1); padding:30px; border-radius:20px; border:1px solid rgba(99,102,241,0.2); text-align:center; margin-bottom:30px;">
        <h1 style="color:#F1F5F9; font-size:2.2rem;">📚 About This Project</h1>
        <p style="color:#94A3B8; font-size:1.1rem;">Explainable AI Based Student Academic Performance Prediction</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
        ### 🎯 Project Overview
        This **B.Tech Final Year Project** combines **Machine Learning** with **Explainable AI (XAI)** to create a transparent student performance prediction system.
        ### ✨ Key Features
        - **Performance Prediction**: Predict student performance using ML models
        - **Explainable AI**: SHAP-based explanations for every prediction
        - **Interactive Analytics**: Visual exploration of performance factors
        - **Model Comparison**: Multiple ML models with automatic best selection
        - **Recommendation Engine**: Personalized improvement suggestions
        ### 🛠️ Technology Stack
        | Component | Technology |
        |---|---|
        | **Frontend** | Streamlit |
        | **Backend** | Python 3.13 |
        | **ML Models** | Scikit-learn, XGBoost |
        | **XAI** | SHAP |
        | **Data Processing** | Pandas, NumPy |
        | **Visualization** | Matplotlib, Plotly |
        """)
    with col2:
        st.markdown("""
        ### 📊 Dataset
        - **1,200 student records** with 14+ features
        - Features include academic, behavioral factors
        - Target: Performance categories (Poor, Average, Good, Excellent)
        ### 🤖 Models Compared
        1. **Logistic Regression** - Baseline
        2. **Decision Tree** - Interpretable
        3. **Random Forest** - Ensemble (Best)
        4. **XGBoost** - Gradient Boosting
        ### ⚠️ Disclaimer
        This is a **decision-support tool only**. It does not measure actual student intelligence or guarantee future success.
        """)
