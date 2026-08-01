# 🎓 Explainable AI Based Student Academic Performance Prediction

A **production-quality** Final Year B.Tech AI & ML project that combines **Machine Learning** with **Explainable AI (XAI)** to create a transparent and interpretable student performance prediction system.

## 🚀 Features

### Machine Learning
- **Multiple Models**: Logistic Regression, Decision Tree, Random Forest, XGBoost
- **Automatic Best Model Selection**: Compares all models and selects the best performer
- **Real Predictions**: Uses actual ML model, not simulated scoring
- **14+ Features**: Attendance, GPA, Study Hours, Backlogs, Participation, etc.

### Explainable AI (SHAP)
- **Global Explanations**: Feature importance across the entire dataset
- **Local Explanations**: Per-prediction feature contributions
- **Waterfall Charts**: Visual feature contribution breakdown
- **Natural Language Explanations**: Human-readable prediction summaries

### Recommendation Engine
- **Personalized Suggestions**: Based on individual student's weak areas
- **Priority-Based**: High, Medium, Low priority recommendations
- **Actionable Advice**: Specific, measurable improvement targets

### Interactive Dashboard
- **Premium UI**: Dark navy theme with glassmorphism design
- **Plotly Charts**: Interactive performance distribution, feature importance, correlations
- **Prediction History**: Search, sort, delete, and export records
- **PDF Reports**: Downloadable student performance reports

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Backend** | Python 3.13 |
| **ML Models** | Scikit-learn, XGBoost |
| **XAI** | SHAP (SHapley Additive exPlanations) |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Plotly, Seaborn |
| **Model Persistence** | Joblib |
| **PDF Generation** | fpdf2 |

## 📁 Project Structure

```
Student_Performance_XAI/
├── dataset/
│   ├── raw/                    # Raw generated data
│   └── processed/              # Cleaned and processed data
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py   # Data cleaning & feature engineering
│   ├── train_model.py          # ML model training & comparison
│   ├── predict.py              # Single prediction with grade/risk/confidence
│   └── evaluate.py             # Model evaluation metrics
├── models/
│   ├── student_performance_model.pkl  # Best trained model
│   ├── preprocessor.pkl              # Feature preprocessor
│   ├── label_encoder.pkl             # Target label encoder
│   └── model_comparison.csv          # Model performance comparison
├── xai/
│   ├── __init__.py
│   ├── shap_analysis.py        # Core SHAP analysis
│   ├── explanation.py          # Human-readable explanations
│   └── feature_importance.py   # Feature importance analysis
├── app/
│   ├── __init__.py
│   ├── app.py                  # Main Streamlit application
│   ├── dashboard.py            # Dashboard components & exports
│   └── components/
│       ├── __init__.py
│       ├── prediction.py       # Input form & prediction display
│       ├── explanation.py      # SHAP explanation display
│       └── visualization.py    # Analytics charts
├── reports/                    # Generated report images
├── screenshots/                # Application screenshots
├── requirements.txt
└── README.md
```

## 📊 Dataset

- **1,200 student records** with 14+ features
- Features include academic, behavioral, and engagement factors
- Target: Performance categories (Poor, Average, Good, Excellent)
- Balanced distribution across all categories
- Synthetic data generated with realistic correlations

## 🎯 Models Compared

| Model | Description |
|---|---|
| **Logistic Regression** | Baseline linear model |
| **Decision Tree** | Interpretable tree-based model |
| **Random Forest** | Ensemble of decision trees (usually best) |
| **XGBoost** | Gradient boosting (optional) |

## 📈 Prediction Output

- **Predicted Percentage**: 0-100% estimated score
- **Grade**: A+, A, B+, B, C, F
- **Performance Level**: Excellent, Good, Above Average, Average, Poor
- **Confidence Score**: 60-99% based on prediction probability
- **Risk Level**: Low Risk, Medium Risk, High Risk
- **Pass/Fail Status**: Based on 50% threshold

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository**
```bash
cd Student_Performance_XAI
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate dataset**
```bash
python dataset/generate_data.py
```

5. **Preprocess data**
```bash
python src/data_preprocessing.py
```

6. **Train the model**
```bash
python src/train_model.py
```

7. **Run the application**
```bash
streamlit run app/app.py
```

### Quick Start (All Steps)
```bash
python dataset/generate_data.py && python src/data_preprocessing.py && python src/train_model.py && streamlit run app/app.py
```

## 🖥️ Application Pages

### 🏠 Home
- Project overview and key features
- Statistics cards
- How it works section

### 🎯 Predict
- Student input form with sliders and dropdowns
- Real-time prediction with grade, confidence, risk
- Circular progress indicator
- Personalized recommendations
- PDF report generation

### 🔍 Explainable AI
- SHAP waterfall chart
- Feature contribution analysis
- Positive and negative factors
- Natural language explanations
- Global feature importance

### 📊 Analytics
- Performance distribution charts
- Feature correlation heatmap
- Attendance vs Performance scatter
- Study hours box plots
- GPA and participation analysis
- Model comparison

### 📋 History
- Search and sort predictions
- Delete individual records
- Clear all history
- Export to CSV
- Summary report

### 📚 About
- Project information
- Technology stack
- Methodology

## 📦 Dependencies

```
pandas, numpy, matplotlib, seaborn, plotly,
scikit-learn, xgboost, shap, joblib,
streamlit, fpdf2, jupyter
```

## ⚠️ Disclaimer

This is a **decision-support tool only**. It does not measure actual student intelligence or guarantee future success. The SHAP explanations show model behavior, not real-world causation. The model is trained on synthetic data and should be validated with real-world data before deployment.

## 📝 License

This project is created for educational purposes as a B.Tech Final Year Project.

## 👥 Team

- **B.Tech AI & ML** Final Year Project
- Guide: [Professor Name]
- Institution: [Your Institution]

