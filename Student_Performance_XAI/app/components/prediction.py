"""
=============================================================================
STEP 8: Enhanced Student Input Form & Prediction Display
=============================================================================
File: app/components/prediction.py
Purpose:
  - Render enhanced input form with validation
  - Display prediction results with premium UI
  - Show circular progress, grade, risk badges
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from xai.shap_analysis import prepare_input_features
from src.predict import predict_student
from app.dashboard import (
    render_circular_progress, render_status_badge,
    render_metric_card, create_performance_gauge,
    create_probability_chart
)


def validate_inputs(attendance, study_hours, prev_marks, internal_marks,
                    assignment_score, lab_score, backlogs, gpa,
                    sleep_hours, participation, submission_rate):
    """
    Validate all input fields and return list of error messages.
    """
    errors = []

    if not (0 <= attendance <= 100):
        errors.append("Attendance must be between 0 and 100%")
    if not (0.5 <= study_hours <= 12):
        errors.append("Study hours must be between 0.5 and 12 hours/day")
    if not (0 <= prev_marks <= 100):
        errors.append("Previous marks must be between 0 and 100%")
    if not (0 <= internal_marks <= 100):
        errors.append("Internal marks must be between 0 and 100%")
    if not (0 <= assignment_score <= 100):
        errors.append("Assignment score must be between 0 and 100%")
    if not (0 <= lab_score <= 100):
        errors.append("Lab score must be between 0 and 100%")
    if not (0 <= backlogs <= 10):
        errors.append("Backlogs must be between 0 and 10")
    if not (0 <= gpa <= 10):
        errors.append("GPA must be between 0 and 10")
    if not (4 <= sleep_hours <= 10):
        errors.append("Sleep hours must be between 4 and 10 hours")
    if not (0 <= participation <= 100):
        errors.append("Participation must be between 0 and 100%")
    if not (0 <= submission_rate <= 100):
        errors.append("Submission rate must be between 0 and 100%")

    return errors


def student_input_form():
    """
    Render enhanced student input form with validation.

    Returns:
    --------
    dict: Student input data if valid, None otherwise
    """
    st.markdown("""
    <div style="background:rgba(99,102,241,0.05); padding:20px; border-radius:16px;
                border:1px solid rgba(99,102,241,0.1); margin-bottom:20px;">
        <h3 style="display:flex; align-items:center; gap:10px; color:#F1F5F9; margin:0;">
            📝 Enter Student Details
        </h3>
        <p style="color:#94A3B8; margin:5px 0 0 0; font-size:14px;">
            Fill in all fields below to get an accurate prediction
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Student Name input
    student_name = st.text_input(
        "👤 Student Name",
        value="",
        placeholder="e.g., John Doe",
        help="Enter the full name of the student"
    )

    # Create two columns for the form
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p style="color:#94A3B8; font-size:13px; font-weight:600;">📊 ACADEMIC PARAMETERS</p>', unsafe_allow_html=True)

        attendance = st.slider(
            "📅 Attendance Percentage (%)",
            min_value=0, max_value=100, value=75, step=1,
            help="Percentage of classes attended during the semester"
        )

        study_hours = st.slider(
            "⏰ Study Hours Per Day",
            min_value=0.5, max_value=12.0, value=4.0, step=0.5,
            help="Average number of hours spent studying outside class per day"
        )

        prev_marks = st.slider(
            "📄 Previous Academic Marks (%)",
            min_value=0, max_value=100, value=65, step=1,
            help="Average marks obtained in the previous academic year"
        )

        internal_marks = st.slider(
            "📋 Internal Assessment Marks (%)",
            min_value=0, max_value=100, value=60, step=1,
            help="Marks from internal assessments, quizzes, and mid-terms"
        )

        assignment_score = st.slider(
            "📝 Assignment Score (%)",
            min_value=0, max_value=100, value=70, step=1,
            help="Average score on assignments and homework"
        )

        lab_score = st.slider(
            "🔬 Practical/Lab Score (%)",
            min_value=0, max_value=100, value=65, step=1,
            help="Performance in practical sessions and laboratory work"
        )

    with col2:
        st.markdown('<p style="color:#94A3B8; font-size:13px; font-weight:600;">🎯 BEHAVIORAL & PERSONAL FACTORS</p>', unsafe_allow_html=True)

        backlogs = st.number_input(
            "⚠️ Number of Backlogs",
            min_value=0, max_value=10, value=2, step=1,
            help="Number of subjects currently backlogged/failed"
        )

        gpa = st.slider(
            "🎓 Previous Semester GPA (out of 10)",
            min_value=0.0, max_value=10.0, value=6.5, step=0.1,
            help="Grade Point Average from the previous semester"
        )

        sleep_hours = st.slider(
            "😴 Sleep Hours Per Day",
            min_value=4.0, max_value=10.0, value=7.0, step=0.5,
            help="Average hours of sleep per night"
        )

        internet_access = st.selectbox(
            "🌐 Internet Access",
            options=["Yes", "No"],
            index=0,
            help="Whether the student has reliable internet access at home"
        )

        extracurricular = st.selectbox(
            "🎨 Extracurricular Activities",
            options=["Yes", "No"],
            index=0,
            help="Participation in sports, clubs, or other activities"
        )

        participation = st.slider(
            "💬 Class Participation (%)",
            min_value=0, max_value=100, value=55, step=1,
            help="Level of engagement in class discussions and activities"
        )

        submission_rate = st.slider(
            "📤 Assignment Submission Rate (%)",
            min_value=0, max_value=100, value=75, step=1,
            help="Percentage of assignments submitted on time"
        )

    # Validate inputs
    errors = validate_inputs(
        attendance, study_hours, prev_marks, internal_marks,
        assignment_score, lab_score, backlogs, gpa,
        sleep_hours, participation, submission_rate
    )

    if errors:
        st.error("⚠️ Please fix the following errors:")
        for error in errors:
            st.warning(error)
        return None

    # Return student input dictionary
    return {
        'Student_Name': student_name if student_name else "Unnamed Student",
        'Attendance_Percentage': attendance,
        'Study_Hours_Per_Day': study_hours,
        'Previous_Academic_Marks': prev_marks,
        'Internal_Assessment_Marks': internal_marks,
        'Assignment_Score': assignment_score,
        'Practical_Lab_Score': lab_score,
        'Number_of_Backlogs': backlogs,
        'Previous_Semester_GPA': gpa,
        'Sleep_Hours': sleep_hours,
        'Internet_Access': 1 if internet_access == "Yes" else 0,
        'Parental_Education': 2,
        'Extracurricular_Activities': 1 if extracurricular == "Yes" else 0,
        'Class_Participation': participation,
        'Assignment_Submission_Rate': submission_rate
    }


def display_prediction_result(result, student_input=None):
    """
    Display prediction result with premium UI including circular progress,
    grade display, risk badge, and probability breakdown.

    Parameters:
    -----------
    result : dict
        Prediction result from predict_student()
    student_input : dict, optional
        Original student input for radar chart
    """
    percentage = result.get('predicted_percentage', 0)
    grade = result.get('grade', 'N/A')
    performance = result.get('performance_level', 'N/A')
    confidence = result.get('confidence', 0)
    risk_level = result.get('risk_level', 'N/A')
    status = result.get('status', 'N/A')
    probabilities = result.get('probabilities', {})

    # Color based on performance
    perf_colors = {
        'Excellent': '#10B981',
        'Good': '#6366F1',
        'Above Average': '#F59E0B',
        'Average': '#F59E0B',
        'Poor': '#F43F5E'
    }
    perf_color = perf_colors.get(performance, '#6366F1')

    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(99,102,241,0.05); padding:15px; border-radius:16px;
                border:1px solid rgba(99,102,241,0.15); margin-bottom:20px;">
        <h3 style="color:#F1F5F9; margin:0; display:flex; align-items:center; gap:10px;">
            🎯 Prediction Result
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Main result cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:16px; border:1px solid rgba(99,102,241,0.15);">
            <p style="color:#94A3B8; font-size:12px; margin:0;">Predicted Percentage</p>
            {render_circular_progress(percentage, 100, 8)}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:16px; border:1px solid rgba(99,102,241,0.15); height:100%;">
            <p style="color:#94A3B8; font-size:12px; margin:0;">Grade</p>
            <p style="font-size:56px; font-weight:800; color:{perf_color}; margin:5px 0;">{grade}</p>
            <p style="color:#F1F5F9; font-size:14px; margin:0;">{performance}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:16px; border:1px solid rgba(99,102,241,0.15);">
            <p style="color:#94A3B8; font-size:12px; margin:0;">Confidence</p>
            <p style="font-size:36px; font-weight:700; color:#818CF8; margin:5px 0;">{confidence:.1f}%</p>
            <p style="color:#F1F5F9; font-size:14px; margin:0;">{render_status_badge(status, risk_level)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:16px; border:1px solid rgba(99,102,241,0.15); height:100%;">
            <p style="color:#94A3B8; font-size:12px; margin:0;">Risk Level</p>
            <p style="font-size:28px; font-weight:700; color:{'#10B981' if 'Low' in risk_level else '#F59E0B' if 'Medium' in risk_level else '#F43F5E'}; margin:10px 0;">
                {risk_level}
            </p>
            <p style="color:#F1F5F9; font-size:14px; margin:0;">{'✅ Pass' if status == 'Pass' else '❌ Fail'}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Probability breakdown
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Prediction Probability Distribution")

    if probabilities:
        # Create a probability chart
        prob_fig = create_probability_chart(probabilities)
        st.plotly_chart(prob_fig, width='stretch', key="pred_prob_chart")

        # Also show as a table
        prob_data = [
            {"Category": cat, "Probability": f"{prob:.1f}%"}
            for cat, prob in probabilities.items()
        ]
        prob_df = pd.DataFrame(prob_data)

        # Color rows
        color_map = {'Poor': 'rgba(244,63,94,0.1)', 'Average': 'rgba(245,158,11,0.1)',
                    'Good': 'rgba(99,102,241,0.1)', 'Excellent': 'rgba(16,185,129,0.1)'}

        styled_df = prob_df.style.applymap(
            lambda x: f'background-color: {color_map.get(x, "transparent")}',
            subset=['Category']
        )
        st.dataframe(styled_df, width='stretch', hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Performance gauge
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    gauge_fig = create_performance_gauge(percentage)
    st.plotly_chart(gauge_fig, width='stretch', key="pred_gauge")
    st.markdown('</div>', unsafe_allow_html=True)

    # Recommendations section (if student_input provided)
    if student_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Personalized Recommendations")
        try:
            from xai.explanation import generate_recommendations
            recommendations = generate_recommendations(student_input, result)

            for i, rec in enumerate(recommendations, 1):
                priority_color = {
                    'High': '#F43F5E',
                    'Medium': '#F59E0B',
                    'Low': '#10B981'
                }.get(rec.get('priority', 'Medium'), '#6366F1')

                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.5); padding:12px 16px;
                            border-radius:12px; border-left:4px solid {priority_color};
                            margin:8px 0;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span>{rec.get('icon', '📌')}</span>
                        <strong style="color:#F1F5F9;">{rec.get('category', 'General')}</strong>
                        <span style="background:{priority_color}22; color:{priority_color};
                                    padding:2px 8px; border-radius:10px; font-size:11px;">
                            {rec.get('priority', 'Medium')}
                        </span>
                    </div>
                    <p style="color:#94A3B8; margin:5px 0 0 30px; font-size:13px;">
                        {rec.get('advice', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.info(f"Recommendations: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

