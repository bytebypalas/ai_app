"""
=============================================================================
STEP 9: Enhanced SHAP Explanation Display with Waterfall & Summary
=============================================================================
File: app/components/explanation.py
Purpose:
  - Display enhanced SHAP explanations with visualizations
  - Show waterfall plot for feature contributions
  - Show summary/global feature importance
  - Generate human-readable explanation text
  - Display recommendation engine results
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from xai.shap_analysis import explain_prediction, get_global_feature_importance, load_artifacts
from xai.explanation import generate_explanation, generate_recommendations
from xai.feature_importance import get_feature_importance_df, load_model_for_importance


def create_waterfall_chart(contributions, title="Feature Contributions"):
    """
    Create a waterfall chart showing feature contributions.

    Parameters:
    -----------
    contributions : dict
        Dictionary of feature contributions (from SHAP)
    title : str
        Chart title

    Returns:
    --------
    plotly Figure: Waterfall chart
    """
    if not contributions:
        return None

    # Sort by absolute contribution
    sorted_items = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
    features = [k.replace('_', ' ').title() for k, v in sorted_items]
    values = [v for k, v in sorted_items]

    # Create waterfall
    fig = go.Figure(go.Waterfall(
        name=title,
        orientation="v",
        measure=["relative"] * len(values),
        x=features,
        y=values,
        text=[f"{'+' if v > 0 else ''}{v:.3f}" for v in values],
        textposition="outside",
        connector={"line": {"color": "rgba(99,102,241,0.3)"}},
        increasing={"marker": {"color": "#10B981"}},
        decreasing={"marker": {"color": "#F43F5E"}},
    ))

    fig.update_layout(
        title={
            'text': title,
            'font': {'color': '#F1F5F9', 'size': 16}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#94A3B8'},
        xaxis={'tickfont': {'color': '#94A3B8', 'size': 11},
               'gridcolor': 'rgba(99,102,241,0.1)'},
        yaxis={'gridcolor': 'rgba(99,102,241,0.1)'},
        margin=dict(l=20, r=40, t=40, b=80),
        height=400,
        showlegend=False
    )

    return fig


def create_contribution_bar_chart(positive_factors, negative_factors):
    """
    Create a grouped bar chart showing positive and negative contributions.

    Parameters:
    -----------
    positive_factors : dict
        Features with positive SHAP values
    negative_factors : dict
        Features with negative SHAP values

    Returns:
    --------
    plotly Figure: Bar chart
    """
    # Prepare positive data
    pos_items = sorted(positive_factors.items(), key=lambda x: x[1], reverse=True)[:5]
    neg_items = sorted(negative_factors.items(), key=lambda x: x[1])[:5]

    pos_features = [k.replace('_', ' ').title() for k, v in pos_items]
    pos_values = [v for k, v in pos_items]

    neg_features = [k.replace('_', ' ').title() for k, v in neg_items]
    neg_values = [v for k, v in neg_items]

    fig = go.Figure()

    # Positive bars
    if pos_features:
        fig.add_trace(go.Bar(
            x=pos_features,
            y=pos_values,
            name='Positive Impact',
            marker_color='#10B981',
            marker_line_color='rgba(16,185,129,0.5)',
            marker_line_width=1,
            text=[f'+{v:.3f}' for v in pos_values],
            textposition='outside',
            textfont={'color': '#10B981'}
        ))

    # Negative bars
    if neg_features:
        fig.add_trace(go.Bar(
            x=neg_features,
            y=neg_values,
            name='Negative Impact',
            marker_color='#F43F5E',
            marker_line_color='rgba(244,63,94,0.5)',
            marker_line_width=1,
            text=[f'{v:.3f}' for v in neg_values],
            textposition='outside',
            textfont={'color': '#F43F5E'}
        ))

    fig.update_layout(
        title={'text': 'Feature Contributions', 'font': {'color': '#F1F5F9', 'size': 16}},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#94A3B8'},
        xaxis={'tickfont': {'color': '#94A3B8', 'size': 11},
               'gridcolor': 'rgba(99,102,241,0.1)'},
        yaxis={'gridcolor': 'rgba(99,102,241,0.1)'},
        margin=dict(l=20, r=20, t=40, b=80),
        height=350,
        legend={'font': {'color': '#94A3B8'}, 'orientation': 'h', 'y': -0.2},
        barmode='group',
        bargap=0.3
    )

    return fig


def display_shap_explanation(result, student_input=None):
    """
    Display enhanced SHAP explanation with visualizations.

    Parameters:
    -----------
    result : dict
        Result from explain_prediction() containing SHAP values
    student_input : dict, optional
        Original student input for recommendations
    """
    if not result:
        st.warning("No explanation data available.")
        return

    if 'note' in result:
        st.info(result['note'])
        return

    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(99,102,241,0.05); padding:15px; border-radius:16px;
                border:1px solid rgba(99,102,241,0.15); margin-bottom:20px;">
        <h3 style="color:#F1F5F9; margin:0; display:flex; align-items:center; gap:10px;">
            🔍 Explainable AI (XAI) Analysis
        </h3>
        <p style="color:#94A3B8; margin:5px 0 0; font-size:13px;">
            SHAP (SHapley Additive exPlanations) shows how each feature contributed to this prediction
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Base value and prediction info
    prediction = result.get('prediction', 'N/A')
    confidence = result.get('confidence', 0)
    base_value = result.get('base_value', 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:12px;">
            <p style="color:#94A3B8; font-size:12px;">Prediction</p>
            <p style="color:#818CF8; font-size:24px; font-weight:700; margin:5px 0;">{prediction}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:12px;">
            <p style="color:#94A3B8; font-size:12px;">Base Value</p>
            <p style="color:#F1F5F9; font-size:24px; font-weight:700; margin:5px 0;">{base_value:.4f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:rgba(30,41,59,0.5);
                    border-radius:12px;">
            <p style="color:#94A3B8; font-size:12px;">Confidence</p>
            <p style="color:#10B981; font-size:24px; font-weight:700; margin:5px 0;">{confidence*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature contribution waterfall
    contributions = result.get('all_contributions', {})
    if contributions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Feature Contribution Analysis")

        waterfall_fig = create_waterfall_chart(contributions)
        if waterfall_fig:
            st.plotly_chart(waterfall_fig, width='stretch', key="shap_waterfall")

        # Also show as detailed table
        contrib_df = pd.DataFrame([
            {"Feature": k.replace('_', ' ').title(),
             "SHAP Value": v,
             "Impact": "✅ Positive" if v > 0 else "⚠️ Negative",
             "Absolute Impact": abs(v)}
            for k, v in sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        ])
        st.dataframe(contrib_df, width='stretch', hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Positive and Negative factors
    positive = result.get('positive_factors', {})
    negative = result.get('negative_factors', {})

    if positive or negative:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            if positive:
                st.markdown("### ✅ Positive Contributing Factors")
                st.markdown("These features **improved** the prediction score:")
                for feat, val in list(positive.items())[:7]:
                    clean_name = feat.replace('_', ' ').title()
                    st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.1); padding:10px 14px;
                                margin:6px 0; border-radius:10px;
                                border-left:4px solid #10B981;">
                        <span style="color:#F1F5F9; font-weight:500;">{clean_name}</span>
                        <span style="float:right; color:#10B981; font-weight:600;">
                            +{abs(val):.4f}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

        with cols[1]:
            if negative:
                st.markdown("### ⚠️ Negative Contributing Factors")
                st.markdown("These features **pulled down** the prediction score:")
                for feat, val in list(negative.items())[:7]:
                    clean_name = feat.replace('_', ' ').title()
                    st.markdown(f"""
                    <div style="background:rgba(244,63,94,0.1); padding:10px 14px;
                                margin:6px 0; border-radius:10px;
                                border-left:4px solid #F43F5E;">
                        <span style="color:#F1F5F9; font-weight:500;">{clean_name}</span>
                        <span style="float:right; color:#F43F5E; font-weight:600;">
                            {val:.4f}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Contribution bar chart
    if positive or negative:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        bar_fig = create_contribution_bar_chart(positive, negative)
        if bar_fig:
            st.plotly_chart(bar_fig, width='stretch', key="shap_bars")
        st.markdown('</div>', unsafe_allow_html=True)

    # Human-readable explanation
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 💬 Summary Explanation")

    explanation = generate_explanation(result, {
        'all_contributions': contributions,
        'positive_factors': positive,
        'negative_factors': negative
    })

    # Render explanation
    summary_text = explanation.get('summary', '')
    st.markdown(f'<div style="background:rgba(99,102,241,0.05); padding:16px; '
                f'border-radius:12px; border:1px solid rgba(99,102,241,0.1); '
                f'line-height:1.8; color:#CBD5E1;">{summary_text}</div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Simple explanations
    simple_exps = explanation.get('simple_explanations', [])
    if simple_exps:
        st.markdown("**Simple Explanations:**")
        for exp in simple_exps:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; padding:5px 0;">
                <span style="color:#10B981;">•</span>
                <span style="color:#94A3B8;">{exp}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Recommendations
    if student_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Personalized Recommendations")

        from xai.explanation import generate_recommendations
        recommendations = generate_recommendations(student_input, result)

        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                'High': '#F43F5E',
                'Medium': '#F59E0B',
                'Low': '#10B981'
            }.get(rec.get('priority', 'Medium'), '#6366F1')

            st.markdown(f"""
            <div style="background:rgba(30,41,59,0.4); padding:10px 14px;
                        margin:6px 0; border-radius:10px;
                        border-left:4px solid {priority_color};">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span>{rec.get('icon', '📌')}</span>
                    <strong style="color:#F1F5F9;">{rec.get('category', 'General')}</strong>
                    <span style="background:{priority_color}22; color:{priority_color};
                                padding:1px 8px; border-radius:8px; font-size:10px;">
                        {rec.get('priority', 'Medium')}
                    </span>
                </div>
                <p style="color:#94A3B8; margin:5px 0 0 30px; font-size:12px;">
                    {rec.get('advice', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
    <div style="background:rgba(245,158,11,0.05); padding:12px 16px; border-radius:10px;
                border:1px solid rgba(245,158,11,0.1); margin-top:20px;">
        <p style="color:#F59E0B; font-size:12px; margin:0;">
            ⚠️ <strong>Important Note:</strong> SHAP values show which features influenced
            the model's prediction. They do not necessarily represent real-world causation.
            This is a decision-support tool, not an absolute authority on student capability.
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_global_feature_importance(global_importance):
    """
    Display global feature importance using Plotly.

    Parameters:
    -----------
    global_importance : dict
        Dictionary of feature names and their importance values
    """
    if not global_importance:
        st.info("Global feature importance not available.")
        return

    st.markdown("""
    <div style="background:rgba(99,102,241,0.05); padding:15px; border-radius:16px;
                border:1px solid rgba(99,102,241,0.15); margin-bottom:20px;">
        <h3 style="color:#F1F5F9; margin:0; display:flex; align-items:center; gap:10px;">
            🌍 Global Feature Importance
        </h3>
        <p style="color:#94A3B8; margin:5px 0 0; font-size:13px;">
            Overall feature importance across the entire dataset (based on SHAP values)
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create DataFrame
    importance_df = pd.DataFrame([
        {"Feature": k.replace('_', ' ').title(), "Importance": v}
        for k, v in global_importance.items()
    ]).head(12)

    # Plotly horizontal bar chart
    fig = px.bar(
        importance_df,
        x='Importance',
        y='Feature',
        orientation='h',
        title='Top Features Influencing Predictions',
        color='Importance',
        color_continuous_scale=['#6366F1', '#8B5CF6', '#A78BFA'],
        text='Importance'
    )

    fig.update_traces(
        texttemplate='%{text:.4f}',
        textposition='outside',
        marker_line_color='rgba(99,102,241,0.3)',
        marker_line_width=1
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#94A3B8'},
        title_font={'color': '#F1F5F9', 'size': 16},
        xaxis={'gridcolor': 'rgba(99,102,241,0.1)'},
        yaxis={'gridcolor': 'rgba(99,102,241,0.1)',
               'tickfont': {'color': '#94A3B8', 'size': 11}},
        margin=dict(l=20, r=60, t=40, b=20),
        height=400,
        showlegend=False,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, width='stretch', key="global_fi_chart")

    # Model-based feature importance comparison
    try:
        model, feat_names, X_sample = load_model_for_importance()
        model_fi_df = get_feature_importance_df(model, feat_names)

        st.markdown("### Model-Based Feature Importance Comparison")
        st.markdown("Comparison of SHAP-based vs Model-based importance:")

        comparison_df = model_fi_df.head(10).copy()
        comparison_df.columns = ['Feature', 'Model Importance']
        comparison_df['Feature'] = comparison_df['Feature'].str.replace('_', ' ').str.title()
        comparison_df['Model Importance'] = comparison_df['Model Importance'].round(4)

        st.dataframe(comparison_df, width='stretch', hide_index=True)

    except Exception:
        pass

