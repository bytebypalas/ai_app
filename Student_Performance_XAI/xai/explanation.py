"""
=============================================================================
STEP 4: Human-Readable XAI Explanations & Recommendation Engine
=============================================================================
File: xai/explanation.py
Purpose:
  - Generate human-readable explanations from SHAP values
  - Generate personalized recommendations based on predictions
  - Create natural language summaries
  - Generate PDF report content

Usage:
  from xai.explanation import generate_explanation, generate_recommendations
=============================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime


def generate_explanation(prediction_result, shap_contributions=None):
    """
    Generate human-readable explanation for a prediction.

    Parameters:
    -----------
    prediction_result : dict
        Result from predict_student() or explain_prediction()
    shap_contributions : dict, optional
        Feature contributions from SHAP analysis

    Returns:
    --------
    dict: Natural language explanation components
    """
    prediction = prediction_result.get('prediction', prediction_result.get('prediction_category', 'Unknown'))
    confidence = prediction_result.get('confidence', 0)
    percentage = prediction_result.get('predicted_percentage', 0)
    grade = prediction_result.get('grade', 'N/A')
    risk_level = prediction_result.get('risk_level', 'N/A')
    passed = prediction_result.get('passed', False)

    # Determine positive and negative factors
    if shap_contributions:
        positive_factors = shap_contributions.get('positive_factors', {})
        negative_factors = shap_contributions.get('negative_factors', {})
        all_contributions = shap_contributions.get('all_contributions', {})
    else:
        positive_factors = {}
        negative_factors = {}
        all_contributions = {}

    # Generate summary
    summary_parts = []

    # Opening statement
    summary_parts.append(
        f"The model predicts **{prediction}** performance "
        f"with {confidence:.1f}% confidence."
    )

    # Predicted percentage and grade
    summary_parts.append(
        f"The estimated percentage is **{percentage:.1f}%** "
        f"which corresponds to grade **{grade}**."
    )

    # Risk assessment
    summary_parts.append(f"This indicates **{risk_level.lower()}** for academic challenges.")

    # Pass/Fail
    if passed:
        summary_parts.append("The student is predicted to **pass** the current semester.")
    else:
        summary_parts.append("⚠️ The student is predicted to **fail** and needs immediate intervention.")

    # Factor explanations
    if positive_factors:
        top_positive = list(positive_factors.items())[:3]
        pos_lines = []
        for feat, val in top_positive:
            clean_name = feat.replace('_', ' ').title()
            pos_lines.append(f"  • **{clean_name}** contributed positively (+{abs(val):.3f})")
        summary_parts.append("\n✅ **Factors that improved the prediction:**\n" + "\n".join(pos_lines))

    if negative_factors:
        top_negative = list(negative_factors.items())[:3]
        neg_lines = []
        for feat, val in top_negative:
            clean_name = feat.replace('_', ' ').title()
            neg_lines.append(f"  • **{clean_name}** reduced the prediction ({val:.3f})")
        summary_parts.append("\n⚠️ **Factors that pulled down the prediction:**\n" + "\n".join(neg_lines))

    # Simple explanations for common scenarios
    simple_explanations = []
    if shap_contributions:
        for feat, val in all_contributions.items():
            clean_name = feat.replace('_', ' ').title()
            if val > 0:
                simple_explanations.append(f"{clean_name} increased the prediction.")
            elif val < 0:
                simple_explanations.append(f"Low {clean_name.lower()} reduced the predicted score.")

    if not simple_explanations:
        simple_explanations = [
            "Attendance percentage positively influenced the prediction.",
            "Previous academic marks contributed significantly to the score.",
            "Study hours per day impacted the final prediction.",
        ]

    explanation = {
        'summary': "\n\n".join(summary_parts),
        'simple_explanations': simple_explanations[:5],
        'decision_rationale': (
            f"The model classified this student as '{prediction}' "
            f"because the weighted combination of academic features, "
            f"behavioral factors, and engagement metrics most closely "
            f"matches the profile of other {prediction.lower()} performing students."
        )
    }

    return explanation


def generate_recommendations(student_input, prediction_result):
    """
    Generate personalized recommendations based on prediction and input data.

    Parameters:
    -----------
    student_input : dict
        Original student input features
    prediction_result : dict
        Prediction result

    Returns:
    --------
    list: List of recommendation dictionaries
    """
    recommendations = []

    # Extract values from input
    attendance = student_input.get('Attendance_Percentage', 75)
    study_hours = student_input.get('Study_Hours_Per_Day', 4)
    prev_marks = student_input.get('Previous_Academic_Marks', 65)
    internal_marks = student_input.get('Internal_Assessment_Marks', 60)
    assignment_score = student_input.get('Assignment_Score', 70)
    lab_score = student_input.get('Practical_Lab_Score', 65)
    backlogs = student_input.get('Number_of_Backlogs', 2)
    gpa = student_input.get('Previous_Semester_GPA', 6.5)
    sleep_hours = student_input.get('Sleep_Hours', 7)
    participation = student_input.get('Class_Participation', 55)
    submission_rate = student_input.get('Assignment_Submission_Rate', 75)
    extracurricular = student_input.get('Extracurricular_Activities', 0)

    predicted_pct = prediction_result.get('predicted_percentage', 0)
    risk_level = prediction_result.get('risk_level', 'Medium Risk')

    # 1. Attendance recommendation
    if attendance < 75:
        recommendations.append({
            'category': 'Attendance',
            'priority': 'High' if attendance < 60 else 'Medium',
            'current': f"{attendance}%",
            'target': "90%+",
            'advice': f"Increase attendance from {attendance:.0f}% to above 90%. "
                      f"Regular class attendance is strongly correlated with better performance. "
                      f"Try to attend all classes and participate actively.",
            'impact': 'High',
            'icon': '📅'
        })
    elif attendance < 90:
        recommendations.append({
            'category': 'Attendance',
            'priority': 'Low',
            'current': f"{attendance}%",
            'target': "90%+",
            'advice': f"Your attendance is good at {attendance:.0f}%. "
                      f"Aim for 90%+ to maintain consistent performance.",
            'impact': 'Medium',
            'icon': '📅'
        })

    # 2. Study hours recommendation
    if study_hours < 4:
        recommended_hours = min(study_hours * 2, 8)
        recommendations.append({
            'category': 'Study Habits',
            'priority': 'High' if study_hours < 2 else 'Medium',
            'current': f"{study_hours:.1f} hrs/day",
            'target': f"{recommended_hours:.1f}+ hrs/day",
            'advice': f"Increase study hours from {study_hours:.1f} to "
                      f"{recommended_hours:.1f} hours per day. "
                      f"Consistent daily study is key to academic success.",
            'impact': 'High',
            'icon': '📚'
        })
    elif study_hours < 6:
        recommendations.append({
            'category': 'Study Habits',
            'priority': 'Low',
            'current': f"{study_hours:.1f} hrs/day",
            'target': "6+ hrs/day",
            'advice': f"Your study hours are reasonable at {study_hours:.1f} hrs/day. "
                      f"Increasing to 6+ hours could further boost performance.",
            'impact': 'Medium',
            'icon': '📚'
        })

    # 3. Assignment completion
    if assignment_score < 70:
        recommendations.append({
            'category': 'Assignments',
            'priority': 'High' if assignment_score < 50 else 'Medium',
            'current': f"{assignment_score:.0f}%",
            'target': "90%+",
            'advice': f"Improve assignment scores from {assignment_score:.0f}% to above 90%. "
                      f"Complete all assignments on time and seek feedback for improvement.",
            'impact': 'High',
            'icon': '📝'
        })
    elif assignment_score < 90:
        recommendations.append({
            'category': 'Assignments',
            'priority': 'Low',
            'current': f"{assignment_score:.0f}%",
            'target': "90%+",
            'advice': f"Good assignment scores ({assignment_score:.0f}%). "
                      f"Aim for 90%+ to maximize this factor's positive impact.",
            'impact': 'Medium',
            'icon': '📝'
        })

    # 4. Backlogs
    if backlogs > 2:
        recommendations.append({
            'category': 'Backlogs',
            'priority': 'High',
            'current': f"{backlogs} backlogs",
            'target': "0 backlogs",
            'advice': f"Focus on clearing all {backlogs} backlog subjects. "
                      f"Backlogs significantly impact overall performance. "
                      f"Create a study plan to address each subject systematically.",
            'impact': 'High',
            'icon': '⚠️'
        })
    elif backlogs > 0:
        recommendations.append({
            'category': 'Backlogs',
            'priority': 'Medium',
            'current': f"{backlogs} backlogs",
            'target': "0 backlogs",
            'advice': f"Work on clearing the remaining {backlogs} backlog(s). "
                      f"Even a few backlogs can affect academic progress.",
            'impact': 'Medium',
            'icon': '⚠️'
        })

    # 5. Sleep
    if sleep_hours < 6:
        recommendations.append({
            'category': 'Sleep & Health',
            'priority': 'High',
            'current': f"{sleep_hours:.1f} hrs/night",
            'target': "7-9 hrs/night",
            'advice': f"Your sleep duration ({sleep_hours:.1f} hrs) is too low. "
                      f"Aim for 7-9 hours of quality sleep per night. "
                      f"Proper sleep improves cognitive function and academic performance.",
            'impact': 'Medium',
            'icon': '😴'
        })
    elif sleep_hours > 9:
        recommendations.append({
            'category': 'Sleep & Health',
            'priority': 'Low',
            'current': f"{sleep_hours:.1f} hrs/night",
            'target': "7-9 hrs/night",
            'advice': f"Consider reducing sleep from {sleep_hours:.1f} to 7-9 hours "
                      f"for better academic balance and productivity.",
            'impact': 'Low',
            'icon': '😴'
        })

    # 6. Participation
    if participation < 50:
        recommendations.append({
            'category': 'Participation',
            'priority': 'Medium',
            'current': f"{participation:.0f}%",
            'target': "70%+",
            'advice': f"Increase class participation from {participation:.0f}% to above 70%. "
                      f"Active participation enhances understanding and retention.",
            'impact': 'Medium',
            'icon': '💬'
        })

    # 7. Submission rate
    if submission_rate < 70:
        recommendations.append({
            'category': 'Submissions',
            'priority': 'High' if submission_rate < 50 else 'Medium',
            'current': f"{submission_rate:.0f}%",
            'target': "95%+",
            'advice': f"Improve assignment submission rate from {submission_rate:.0f}% to 95%+. "
                      f"Timely submissions are crucial for academic success.",
            'impact': 'High',
            'icon': '📤'
        })

    # 8. Internal marks
    if internal_marks < 60:
        recommendations.append({
            'category': 'Internal Assessment',
            'priority': 'Medium',
            'current': f"{internal_marks:.0f}%",
            'target': "80%+",
            'advice': f"Focus on improving internal assessment marks from "
                      f"{internal_marks:.0f}% to 80%+. "
                      f"Internals contribute significantly to final grades.",
            'impact': 'Medium',
            'icon': '📊'
        })

    # 9. Practical/Lab score
    if lab_score < 60:
        recommendations.append({
            'category': 'Practical Skills',
            'priority': 'Medium',
            'current': f"{lab_score:.0f}%",
            'target': "80%+",
            'advice': f"Improve practical/lab scores from {lab_score:.0f}% to 80%+. "
                      f"Hands-on practice is essential for technical subjects.",
            'impact': 'Medium',
            'icon': '🔬'
        })

    # 10. GPA specific
    if gpa < 6.0:
        recommendations.append({
            'category': 'Academic Foundation',
            'priority': 'High' if gpa < 4.0 else 'Medium',
            'current': f"{gpa:.1f}/10",
            'target': "7.0+/10",
            'advice': f"Work on improving GPA from {gpa:.1f} to 7.0+. "
                      f"A strong GPA foundation helps in all academic pursuits.",
            'impact': 'High',
            'icon': '🎯'
        })

    # 11. Extracurricular
    if extracurricular == 0:
        recommendations.append({
            'category': 'Extracurricular',
            'priority': 'Low',
            'current': 'Not participating',
            'target': '1-2 activities',
            'advice': "Consider joining 1-2 extracurricular activities. "
                      "They help develop soft skills and provide a balanced academic life.",
            'impact': 'Low',
            'icon': '🎨'
        })

    # Sort by priority
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    recommendations.sort(key=lambda r: priority_order.get(r['priority'], 99))

    # Limit to top recommendations
    top_recommendations = recommendations[:5]

    return top_recommendations


def generate_report_content(student_input, prediction_result, explanation, recommendations):
    """
    Generate complete content for PDF report.

    Parameters:
    -----------
    student_input : dict
        Original student input
    prediction_result : dict
        Prediction result
    explanation : dict
        Generated explanation
    recommendations : list
        Generated recommendations

    Returns:
    --------
    dict: Report sections
    """
    report = {
        'header': {
            'title': 'Student Academic Performance Report',
            'subtitle': 'Generated by Explainable AI Prediction System',
            'date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'report_id': f'XAI-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        },
        'student_info': {
            'attendance': student_input.get('Attendance_Percentage', 'N/A'),
            'study_hours': student_input.get('Study_Hours_Per_Day', 'N/A'),
            'prev_marks': student_input.get('Previous_Academic_Marks', 'N/A'),
            'internal_marks': student_input.get('Internal_Assessment_Marks', 'N/A'),
            'assignment_score': student_input.get('Assignment_Score', 'N/A'),
            'lab_score': student_input.get('Practical_Lab_Score', 'N/A'),
            'backlogs': student_input.get('Number_of_Backlogs', 'N/A'),
            'gpa': student_input.get('Previous_Semester_GPA', 'N/A'),
            'sleep_hours': student_input.get('Sleep_Hours', 'N/A'),
            'participation': student_input.get('Class_Participation', 'N/A'),
            'submission_rate': student_input.get('Assignment_Submission_Rate', 'N/A'),
            'extracurricular': 'Yes' if student_input.get('Extracurricular_Activities', 0) == 1 else 'No'
        },
        'prediction_summary': {
            'predicted_percentage': prediction_result.get('predicted_percentage', 'N/A'),
            'grade': prediction_result.get('grade', 'N/A'),
            'performance_level': prediction_result.get('performance_level', 'N/A'),
            'confidence': prediction_result.get('confidence', 'N/A'),
            'risk_level': prediction_result.get('risk_level', 'N/A'),
            'status': prediction_result.get('status', 'N/A')
        },
        'explanation': {
            'summary': explanation.get('summary', ''),
            'simple_explanations': explanation.get('simple_explanations', []),
            'decision_rationale': explanation.get('decision_rationale', '')
        },
        'recommendations': [
            {
                'category': r['category'],
                'priority': r['priority'],
                'advice': r['advice']
            }
            for r in recommendations
        ]
    }

    return report


def main():
    """Test explanation and recommendation generation."""
    print("=" * 60)
    print("TESTING EXPLANATION & RECOMMENDATION MODULE")
    print("=" * 60)

    # Sample prediction result
    prediction_result = {
        'predicted_percentage': 78.5,
        'grade': 'B+',
        'performance_level': 'Good',
        'confidence': 87.3,
        'risk_level': 'Medium Risk',
        'passed': True,
        'status': 'Pass',
        'prediction_category': 'Good'
    }

    # Sample student input
    student_input = {
        'Attendance_Percentage': 72,
        'Study_Hours_Per_Day': 3,
        'Previous_Academic_Marks': 68,
        'Internal_Assessment_Marks': 60,
        'Assignment_Score': 70,
        'Practical_Lab_Score': 65,
        'Number_of_Backlogs': 3,
        'Previous_Semester_GPA': 6.0,
        'Sleep_Hours': 6.5,
        'Internet_Access': 1,
        'Parental_Education': 2,
        'Extracurricular_Activities': 0,
        'Class_Participation': 50,
        'Assignment_Submission_Rate': 75
    }

    # Sample SHAP contributions
    shap_contributions = {
        'positive_factors': {
            'Previous Academic Marks': 0.2345,
            'Assignment Score': 0.1567,
            'Attendance Percentage': 0.1234
        },
        'negative_factors': {
            'Study Hours Per Day': -0.0891,
            'Number Of Backlogs': -0.0654
        },
        'all_contributions': {
            'Previous Academic Marks': 0.2345,
            'Assignment Score': 0.1567,
            'Attendance Percentage': 0.1234,
            'Study Hours Per Day': -0.0891,
            'Number Of Backlogs': -0.0654
        }
    }

    # Generate explanation
    print("\nGenerating explanation...")
    explanation = generate_explanation(prediction_result, shap_contributions)
    print("\nSummary:")
    print(explanation['summary'])
    print("\nSimple Explanations:")
    for exp in explanation['simple_explanations']:
        print(f"  • {exp}")

    # Generate recommendations
    print("\n" + "-" * 40)
    print("RECOMMENDATIONS")
    print("-" * 40)
    recommendations = generate_recommendations(student_input, prediction_result)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority']}] {rec['category']}")
        print(f"   {rec['advice']}")

    print("\n✓ Explanation & Recommendation module working!")


if __name__ == "__main__":
    main()

