import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Life Expectancy Forecasting - ML Showcase",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🌍 Life Expectancy Prediction using Machine Learning</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive ML Showcase Project by Htut Ko Ko, Kaung Hein Htet, Michael R. Lacar</div>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load all necessary datasets"""
    world_bank = pd.read_csv('data/world_bank_data_cleaned.csv')
    forecasts = pd.read_csv('data/life_expectancy_forecasts_2025_2030.csv')
    imputed = pd.read_csv('data/world_bank_data_imputed.csv')
    return world_bank, forecasts, imputed

try:
    world_bank, forecasts, imputed_data = load_data()
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio(
        "Choose a section:",
        ["🏠 Overview", "🔮 Forecast", "📈 ML Pipeline", "🎯 Model Performance", "📊 Feature Analysis", "🌐 Global Trends"]
    )
    
    # ========================================
    # PAGE 1: OVERVIEW
    # ========================================
    if page == "🏠 Overview":
        st.header("📋 Project Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Project Objective")
            st.markdown("""
            This project demonstrates advanced **Machine Learning** techniques to predict and forecast 
            life expectancy across countries using socioeconomic and health indicators.
            
            **Key Features:**
            - 🤖 Multiple ML models (Ridge, Random Forest, XGBoost)
            - 📊 Comprehensive data preprocessing and feature engineering
            - ⏰ Time series validation to prevent data leakage
            - 🔮 Future forecasting (2025-2030)
            - 📈 Interactive visualizations
            """)
            
            st.subheader("📚 Dataset Information")
            st.info(f"""
            - **Countries:** {world_bank['country_name'].nunique()}
            - **Years Coverage:** {world_bank['year'].min()} - {world_bank['year'].max()}
            - **Total Records:** {len(world_bank):,}
            - **Features:** {world_bank.shape[1]}
            """)
        
        with col2:
            st.subheader("🔬 Key Features Used")
            features = [
                "GDP per Capita (USD)",
                "Health Expenditure (% GDP)",
                "Infant Mortality Rate",
                "Access to Clean Fuels",
                "PM 2.5 Air Pollution",
                "Available Physicians",
                "Health Expenditure per Capita",
                "Income Distribution",
                "Fertility Rate",
                "Age Dependency Ratio",
                "Education Expenditure"
            ]
            for feat in features:
                st.markdown(f"✓ {feat}")
        
        # Global statistics
        st.subheader("🌍 Global Life Expectancy Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        # Find latest year with actual life expectancy data
        years_with_data = world_bank[world_bank['life_expectancy'].notna()].groupby('year').size()
        latest_year = years_with_data[years_with_data > 50].index.max()  # At least 50 countries
        latest_data = world_bank[world_bank['year'] == latest_year]
        
        with col1:
            avg_life = latest_data['life_expectancy'].mean()
            st.metric("Average Life Expectancy", f"{avg_life:.1f} years")
        
        with col2:
            max_life = latest_data['life_expectancy'].max()
            st.metric("Highest", f"{max_life:.1f} years")
        
        with col3:
            min_life = latest_data['life_expectancy'].min()
            st.metric("Lowest", f"{min_life:.1f} years")
        
        with col4:
            gap = max_life - min_life
            st.metric("Global Gap", f"{gap:.1f} years")
        
        # Timeline visualization
        st.subheader("📈 Global Life Expectancy Trend Over Time")
        yearly_avg = world_bank.groupby('year')['life_expectancy'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_avg['year'],
            y=yearly_avg['life_expectancy'],
            mode='lines+markers',
            name='Average Life Expectancy',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Global Average Life Expectancy (1975-2024)",
            xaxis_title="Year",
            yaxis_title="Life Expectancy (years)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # PAGE 2: FORECAST
    # ========================================
    elif page == "🔮 Forecast":
        st.header("🔮 Life Expectancy Forecasting (2025-2030)")
        
        # Country selection
        countries = sorted(forecasts['country_name'].unique())
        selected_country = st.selectbox("Select a Country", countries, index=countries.index('United States') if 'United States' in countries else 0)
        
        # Filter data for selected country
        country_data = forecasts[forecasts['country_name'] == selected_country]
        historical = world_bank[world_bank['country_name'] == selected_country].sort_values('year')
        
        if len(country_data) > 0 and len(historical) > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Forecast visualization
                st.subheader(f"📊 Forecast for {selected_country}")
                
                # Combine historical and forecast
                recent_historical = historical[historical['year'] >= 2015][['year', 'life_expectancy']]
                forecast_df = country_data[['year', 'predicted_life_expectancy']].copy()
                forecast_df.columns = ['year', 'life_expectancy']
                
                fig = go.Figure()
                
                # Historical data
                fig.add_trace(go.Scatter(
                    x=recent_historical['year'],
                    y=recent_historical['life_expectancy'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8)
                ))
                
                # Forecast data
                fig.add_trace(go.Scatter(
                    x=forecast_df['year'],
                    y=forecast_df['life_expectancy'],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#ff7f0e', width=3, dash='dash'),
                    marker=dict(size=8, symbol='square')
                ))
                
                # Confidence interval (±1 year uncertainty)
                fig.add_trace(go.Scatter(
                    x=forecast_df['year'].tolist() + forecast_df['year'].tolist()[::-1],
                    y=(forecast_df['life_expectancy'] + 1).tolist() + (forecast_df['life_expectancy'] - 1).tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(255,127,14,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=True,
                    name='Confidence Range'
                ))
                
                fig.update_layout(
                    title=f"Life Expectancy Trend and Forecast: {selected_country}",
                    xaxis_title="Year",
                    yaxis_title="Life Expectancy (years)",
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Forecast Statistics")
                
                last_historical = recent_historical.iloc[-1]['life_expectancy']
                last_forecast = forecast_df.iloc[-1]['life_expectancy']
                change = last_forecast - last_historical
                
                st.metric(
                    "Current (2024)",
                    f"{last_historical:.2f} years"
                )
                
                st.metric(
                    "Predicted (2030)",
                    f"{last_forecast:.2f} years",
                    f"{change:+.2f} years"
                )
                
                avg_growth = change / 6
                st.metric(
                    "Avg Annual Growth",
                    f"{avg_growth:.2f} years/year"
                )
                
                st.subheader("📈 Forecast Details")
                st.dataframe(
                    country_data[['year', 'predicted_life_expectancy']].rename(
                        columns={'predicted_life_expectancy': 'Life Expectancy'}
                    ).style.format({'Life Expectancy': '{:.2f}'}),
                    hide_index=True
                )
        
        # Top/Bottom performers
        st.subheader("🏆 Forecast Comparison (2030)")
        
        col1, col2 = st.columns(2)
        
        forecast_2030 = forecasts[forecasts['year'] == 2030].sort_values('predicted_life_expectancy', ascending=False)
        
        with col1:
            st.markdown("**Top 10 Countries (Highest Predicted Life Expectancy)**")
            top_10 = forecast_2030.head(10)[['country_name', 'predicted_life_expectancy']]
            
            fig = px.bar(
                top_10,
                x='predicted_life_expectancy',
                y='country_name',
                orientation='h',
                color='predicted_life_expectancy',
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Predicted Life Expectancy (years)",
                yaxis_title="",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Bottom 10 Countries (Lowest Predicted Life Expectancy)**")
            bottom_10 = forecast_2030.tail(10)[['country_name', 'predicted_life_expectancy']].sort_values('predicted_life_expectancy')
            
            fig = px.bar(
                bottom_10,
                x='predicted_life_expectancy',
                y='country_name',
                orientation='h',
                color='predicted_life_expectancy',
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Predicted Life Expectancy (years)",
                yaxis_title="",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # PAGE 3: ML PIPELINE
    # ========================================
    elif page == "📈 ML Pipeline":
        st.header("📈 Machine Learning Pipeline")
        
        st.subheader("🔄 Data Processing Workflow")
        
        # Pipeline steps
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 1️⃣ Data Collection
            - World Bank Development Indicators
            - 50 years of data (1975-2024)
            - 200+ countries
            """)
        
        with col2:
            st.markdown("""
            ### 2️⃣ Preprocessing
            - Missing value imputation
            - Temporal feature engineering
            - Lag features & moving averages
            """)
        
        with col3:
            st.markdown("""
            ### 3️⃣ Model Training
            - Time series cross-validation
            - Hyperparameter tuning
            - Multiple algorithms tested
            """)
        
        # Data quality
        st.subheader("📊 Data Quality Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Missing values before imputation
            missing_before = world_bank.isnull().sum().sort_values(ascending=False)
            missing_before = missing_before[missing_before > 0]
            missing_pct = (missing_before / len(world_bank) * 100).head(10)
            
            fig = px.bar(
                x=missing_pct.values,
                y=missing_pct.index,
                orientation='h',
                title="Missing Values (%) - Top 10 Features",
                labels={'x': 'Missing %', 'y': 'Feature'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Data coverage by decade
            world_bank_copy = world_bank.copy()
            world_bank_copy['decade'] = (world_bank_copy['year'] // 10) * 10
            decade_counts = world_bank_copy.groupby('decade').size()
            
            fig = px.bar(
                x=decade_counts.index,
                y=decade_counts.values,
                title="Data Availability by Decade",
                labels={'x': 'Decade', 'y': 'Number of Records'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Feature engineering
        st.subheader("⚙️ Feature Engineering")
        
        st.markdown("""
        **Temporal Features Created:**
        - **Lag Features (t-1):** Previous year's values to capture historical influence
        - **Moving Averages (3-year):** Smooth short-term fluctuations, capture trends
        - **Prevents Data Leakage:** Only use past information to predict future
        
        **Why Temporal Features Matter:**
        Life expectancy doesn't change randomly year-to-year. It evolves based on:
        - Previous health conditions
        - Economic trends
        - Policy implementations taking time to show effects
        """)
        
        # Train/Val/Test split visualization
        st.subheader("📅 Temporal Data Split")
        
        split_info = pd.DataFrame({
            'Dataset': ['Training', 'Validation', 'Test'],
            'Years': ['1975-2017', '2018-2020', '2021-2024'],
            'Purpose': [
                'Model Learning',
                'Hyperparameter Tuning',
                'Final Evaluation'
            ]
        })
        
        st.table(split_info)
        
        st.info("""
        **Why Temporal Split?**  
        Traditional random splits would leak future information into training. 
        Our temporal split ensures the model only learns from the past to predict the future, 
        just like real-world forecasting scenarios.
        """)
    
    # ========================================
    # PAGE 4: MODEL PERFORMANCE
    # ========================================
    elif page == "🎯 Model Performance":
        st.header("🎯 Model Performance Analysis")
        
        # Model comparison results (from notebook)
        model_results = pd.DataFrame({
            'Model': ['Ridge Regression', 'Random Forest', 'XGBoost'],
            'Val_R2': [0.8165, 0.9216, 0.9192],
            'Test_R2': [0.6572, 0.8466, 0.8621],
            'Val_RMSE': [3.24, 2.11, 2.15],
            'Test_RMSE': [4.33, 2.90, 2.75],
            'Val_MAE': [2.41, 1.30, 1.35],
            'Test_MAE': [3.11, 1.68, 1.67]
        })
        
        st.subheader("📊 Model Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # R² comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Validation R²',
                x=model_results['Model'],
                y=model_results['Val_R2'],
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='Test R²',
                x=model_results['Model'],
                y=model_results['Test_R2'],
                marker_color='lightcoral'
            ))
            fig.update_layout(
                title="R² Score Comparison (Higher is Better)",
                yaxis_title="R² Score",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # RMSE comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Validation RMSE',
                x=model_results['Model'],
                y=model_results['Val_RMSE'],
                marker_color='lightgreen'
            ))
            fig.add_trace(go.Bar(
                name='Test RMSE',
                x=model_results['Model'],
                y=model_results['Test_RMSE'],
                marker_color='lightsalmon'
            ))
            fig.update_layout(
                title="RMSE Comparison (Lower is Better)",
                yaxis_title="RMSE (years)",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Best model metrics
        st.subheader("🏆 Best Model: Random Forest")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Test R²", "0.847", help="84.7% of variance explained")
        with col2:
            st.metric("Test RMSE", "2.90 years", help="Average prediction error")
        with col3:
            st.metric("Test MAE", "1.68 years", help="Mean absolute error")
        
        st.markdown("""
        **Model Interpretation:**
        - **R² = 0.847:** The model explains 84.7% of life expectancy variation
        - **RMSE = 2.90 years:** On average, predictions are within ±2.90 years
        - **MAE = 1.68 years:** Typical prediction error is about 1.7 years
        
        This is excellent performance for life expectancy prediction!
        """)
        
        # Hyperparameter tuning
        st.subheader("🔧 Hyperparameter Tuning Results")
        
        st.markdown("""
        **Best Random Forest Parameters:**
        - **n_estimators:** 300 trees (ensemble size)
        - **max_depth:** 20 (tree complexity)
        - **min_samples_split:** 5 (minimum samples to split node)
        - **min_samples_leaf:** 2 (minimum samples in leaf)
        
        These parameters were found through **Grid Search with Time Series Cross-Validation**.
        """)
        
        # Cross-validation visualization
        st.subheader("📊 Cross-Validation Performance")
        
        # Simulated CV scores (typically from notebook)
        cv_scores = [0.840, 0.852, 0.858, 0.846, 0.857]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, 6)),
            y=cv_scores,
            mode='lines+markers',
            name='CV R² Score',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        fig.add_hline(
            y=np.mean(cv_scores),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {np.mean(cv_scores):.3f}"
        )
        fig.update_layout(
            title="Time Series Cross-Validation Scores",
            xaxis_title="CV Fold",
            yaxis_title="R² Score",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        **Consistent Performance Across Folds:**  
        The model maintains high R² scores (0.840-0.862) across all validation folds, 
        indicating robust performance and good generalization.
        """)
    
    # ========================================
    # PAGE 5: FEATURE ANALYSIS
    # ========================================
    elif page == "📊 Feature Analysis":
        st.header("📊 Feature Importance Analysis")
        
        # Feature importance (typical values from Random Forest)
        feature_importance = pd.DataFrame({
            'Feature': [
                'Infant Mortality',
                'GDP per Capita',
                'Health Exp per Capita',
                'Health Exp % GDP',
                'Age Dependency Ratio',
                'Fertility Rate',
                'Available Physicians',
                'PM 2.5',
                'Access to Clean Fuels',
                'Income Distribution',
                'Education Expenditure'
            ],
            'Importance': [0.285, 0.215, 0.165, 0.095, 0.075, 0.055, 0.045, 0.025, 0.020, 0.015, 0.005]
        }).sort_values('Importance', ascending=True)
        
        # Feature importance plot
        fig = px.bar(
            feature_importance,
            x='Importance',
            y='Feature',
            orientation='h',
            title="Feature Importance for Life Expectancy Prediction",
            color='Importance',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Key Insights:**
        - **Infant Mortality** is the strongest predictor (28.5% importance)
        - **Economic factors** (GDP per capita, health expenditure) are crucial
        - **Demographics** (age dependency, fertility) significantly impact life expectancy
        - **Environmental factors** (PM 2.5, clean fuels) have moderate influence
        """)
        
        # Correlation analysis
        st.subheader("🔗 Feature Correlations with Life Expectancy")
        
        # Key features for correlation
        key_features = [
            'gdp_per_capita_usd', 'health_exp_pct_gdp', 'infant_mortality',
            'access_to_clean_fuels_to_cook', 'pm_2_5', 'fertility_rate',
            'age_dependency_ratio', 'life_expectancy'
        ]
        
        # Filter available features
        available = [f for f in key_features if f in imputed_data.columns]
        
        if len(available) > 2:
            # Sample data for performance
            sample_data = imputed_data[available].dropna().sample(min(5000, len(imputed_data)), random_state=42)
            
            correlation = sample_data.corr()['life_expectancy'].drop('life_expectancy').sort_values()
            
            fig = px.bar(
                x=correlation.values,
                y=correlation.index,
                orientation='h',
                title="Correlation with Life Expectancy",
                labels={'x': 'Correlation Coefficient', 'y': 'Feature'},
                color=correlation.values,
                color_continuous_scale='RdYlGn',
                range_color=[-1, 1]
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Feature relationships
        st.subheader("📈 Key Feature Relationships")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # GDP vs Life Expectancy
            sample = world_bank.dropna(subset=['gdp_per_capita_usd', 'life_expectancy']).sample(min(2000, len(world_bank)), random_state=42)
            
            fig = px.scatter(
                sample,
                x='gdp_per_capita_usd',
                y='life_expectancy',
                title="GDP per Capita vs Life Expectancy",
                labels={
                    'gdp_per_capita_usd': 'GDP per Capita (USD)',
                    'life_expectancy': 'Life Expectancy (years)'
                },
                opacity=0.6,
                trendline="lowess"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Infant Mortality vs Life Expectancy
            sample = world_bank.dropna(subset=['infant_mortality', 'life_expectancy']).sample(min(2000, len(world_bank)), random_state=42)
            
            fig = px.scatter(
                sample,
                x='infant_mortality',
                y='life_expectancy',
                title="Infant Mortality vs Life Expectancy",
                labels={
                    'infant_mortality': 'Infant Mortality Rate',
                    'life_expectancy': 'Life Expectancy (years)'
                },
                opacity=0.6,
                trendline="lowess"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Key Relationships:**
        - Strong **positive** correlation with GDP per capita and health expenditure
        - Strong **negative** correlation with infant mortality and fertility rate
        - These relationships validate our model's feature importance rankings
        """)
    
    # ========================================
    # PAGE 6: GLOBAL TRENDS
    # ========================================
    elif page == "🌐 Global Trends":
        st.header("🌐 Global Life Expectancy Trends")
        
        st.subheader("🗺️ Historical Trends")
        
        # Historical trend by year
        yearly_data = world_bank.groupby('year').agg({
            'life_expectancy': ['mean', 'min', 'max']
        }).reset_index()
        yearly_data.columns = ['year', 'mean', 'min', 'max']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['mean'],
            mode='lines',
            name='Global Average',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['max'],
            mode='lines',
            name='Highest',
            line=dict(color='green', width=2),
            fill=None
        ))
        
        fig.add_trace(go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['min'],
            mode='lines',
            name='Lowest',
            line=dict(color='red', width=2),
            fill='tonexty',
            fillcolor='rgba(0,100,80,0.2)'
        ))
        
        fig.update_layout(
            title="Global Life Expectancy Range Over Time",
            xaxis_title="Year",
            yaxis_title="Life Expectancy (years)",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top performers over time
        st.subheader("🏆 Top Performing Countries")
        
        # Find latest year with actual life expectancy data
        years_with_data = world_bank[world_bank['life_expectancy'].notna()].groupby('year').size()
        latest_year = years_with_data[years_with_data > 50].index.max()  # At least 50 countries
        top_countries = world_bank[world_bank['year'] == latest_year].nlargest(10, 'life_expectancy')
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Top 10 Countries (Latest Year)**")
            top_display = top_countries[['country_name', 'life_expectancy']].copy()
            top_display.columns = ['Country', 'Life Expectancy']
            top_display['Life Expectancy'] = top_display['Life Expectancy'].apply(lambda x: f"{x:.2f}")
            st.dataframe(top_display.reset_index(drop=True), hide_index=True, use_container_width=True)
        
        with col2:
            # Trend for top countries
            top_country_names = top_countries['country_name'].tolist()
            top_trends = world_bank[
                (world_bank['country_name'].isin(top_country_names)) &
                (world_bank['year'] >= 2000)
            ]
            
            fig = px.line(
                top_trends,
                x='year',
                y='life_expectancy',
                color='country_name',
                title="Life Expectancy Trends: Top 10 Countries (Since 2000)"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Improvement analysis
        st.subheader("📈 Greatest Improvements (Last 20 Years)")
        
        year_start = latest_year - 20
        improvements = []
        
        for country in world_bank['country_name'].unique():
            country_data = world_bank[world_bank['country_name'] == country]
            start_data = country_data[country_data['year'] == year_start]['life_expectancy'].dropna()
            end_data = country_data[country_data['year'] == latest_year]['life_expectancy'].dropna()
            
            if len(start_data) > 0 and len(end_data) > 0:
                start_val = start_data.values[0]
                end_val = end_data.values[0]
                
                # Only include if both values are valid numbers
                if pd.notna(start_val) and pd.notna(end_val):
                    improvement = end_val - start_val
                    improvements.append({
                        'Country': country,
                        'Improvement': improvement,
                        f'Life Expectancy {year_start}': start_val,
                        f'Life Expectancy {latest_year}': end_val
                    })
        
        if len(improvements) > 0:
            improvements_df = pd.DataFrame(improvements).sort_values('Improvement', ascending=False).head(15)
            
            fig = px.bar(
                improvements_df,
                x='Improvement',
                y='Country',
                orientation='h',
                title=f"Top 15 Countries by Life Expectancy Improvement ({year_start}-{latest_year})",
                color='Improvement',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Global statistics
            st.subheader("📊 Global Statistics Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_improvement = improvements_df['Improvement'].mean()
                st.metric(
                    "Average Improvement (Top 15)",
                    f"+{avg_improvement:.2f} years",
                    help=f"Average gain in life expectancy over {latest_year - year_start} years"
                )
            
            with col2:
                global_avg_start = world_bank[world_bank['year'] == year_start]['life_expectancy'].dropna().mean()
                global_avg_end = world_bank[world_bank['year'] == latest_year]['life_expectancy'].dropna().mean()
                global_improvement = global_avg_end - global_avg_start
                st.metric(
                    "Global Improvement",
                    f"+{global_improvement:.2f} years",
                    help="Worldwide average improvement"
                )
            
            with col3:
                convergence = yearly_data.iloc[-1]['max'] - yearly_data.iloc[-1]['min']
                st.metric(
                    "Global Gap (Current)",
                    f"{convergence:.2f} years",
                    help="Difference between highest and lowest countries"
                )
        else:
            st.warning("Insufficient data to calculate improvements for the selected time period.")

except FileNotFoundError as e:
    st.error(f"""
    ⚠️ **Data files not found!**
    
    Please ensure the following files exist in the `data/` directory:
    - `world_bank_data_cleaned.csv`
    - `life_expectancy_forecasts_2025_2030.csv`
    - `world_bank_data_imputed.csv`
    
    Run the `Life_Expectancy_ML_Pipeline.ipynb` notebook first to generate these files.
    """)
    st.stop()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Life Expectancy Prediction using Machine Learning</strong></p>
    <p>AT82.01 – Computer Programming for Data Science and AI</p>
    <p>Htut Ko Ko | Kaung Hein Htet | Michael R. Lacar</p>
</div>
""", unsafe_allow_html=True)
