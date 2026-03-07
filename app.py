"""
Dream Analyzer Web Application
Streamlit interface for AI-powered dream analysis
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from analyzer import DreamAnalyzer

# Page configuration
st.set_page_config(
    page_title="AI Dream Analyzer",
    page_icon="💭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
    }
    .result-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin: 1rem 0;
    }
    .symbol-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .recommendation-item {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #4B9EFF;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">💭 AI Dream Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Combining Zhou Gong Dream Interpretation with AI Emotion & Stress Analysis</p>', unsafe_allow_html=True)

# Initialize analyzer
@st.cache_resource
def get_analyzer():
    return DreamAnalyzer()

analyzer = get_analyzer()

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'total_analyses' not in st.session_state:
    st.session_state.total_analyses = 0

# Sidebar
with st.sidebar:
    st.markdown("## 📊 About")
    st.info("""
    **Academic Project**  
    This tool uses two AI models:
    1. 🤖 Emotion analysis (DistilRoBERTa)
    2. 🤖 Recommendation generation (FLAN-T5)
    
    Combines traditional Zhou Gong interpretations with modern AI.
    """)
    
    st.markdown("---")
    
    # Sample dreams
    st.markdown("## 📝 Sample Dreams")
    sample_dreams = {
        "Select a sample": "",
        "😨 Falling Dream": "I was falling from a skyscraper and couldn't stop myself. I felt terrified as the ground rushed toward me.",
        "😊 Flying Dream": "I was flying over beautiful mountains and forests. The sun was shining and I felt completely free and happy.",
        "🏃 Chase Dream": "Someone was chasing me through dark, empty streets. I kept running but my legs felt heavy and slow.",
        "📝 Exam Dream": "I was taking an important exam but couldn't read the questions. Everyone else was finishing while I was stuck.",
        "🦷 Teeth Dream": "All my teeth started falling out. I tried to catch them but they turned to dust in my hands."
    }
    
    selected_sample = st.selectbox("Try a sample dream:", list(sample_dreams.keys()))
    
    if selected_sample != "Select a sample":
        st.session_state.sample_dream = sample_dreams[selected_sample]
        st.success("Sample loaded! Scroll down to analyze.")
    
    st.markdown("---")
    
    # History
    if st.session_state.analysis_history:
        st.markdown("## 📋 Recent Analyses")
        for i, analysis in enumerate(st.session_state.analysis_history[-3:], 1):
            with st.expander(f"Analysis #{len(st.session_state.analysis_history)-3+i}"):
                st.write(f"**Dream:** {analysis['dream_snippet']}")
                st.write(f"**Stress:** {analysis['stress_score']}/10 ({analysis['stress_level']})")
                st.write(f"**Emotion:** {analysis['emotion']}")
    
    st.markdown("---")
    
    # Clear history button
    if st.button("🗑️ Clear All History"):
        st.session_state.analysis_history = []
        st.session_state.total_analyses = 0
        st.rerun()
    
    # Stats
    st.markdown("## 📈 Statistics")
    st.metric("Total Analyses", st.session_state.total_analyses)
    
    if st.session_state.analysis_history:
        avg_stress = sum(h["stress_score"] for h in st.session_state.analysis_history) / len(st.session_state.analysis_history)
        st.metric("Average Stress", f"{avg_stress:.1f}/10")

# Main content area
st.markdown("## ✍️ Describe Your Dream")

# Get dream text
dream_text = ""
if 'sample_dream' in st.session_state:
    dream_text = st.text_area(
        "Enter your dream description:",
        value=st.session_state.sample_dream,
        height=150,
        placeholder="Example: Last night I dreamed that I was flying over mountains...",
        label_visibility="collapsed"
    )
    # Clear sample after showing
    if st.button("Clear Sample"):
        del st.session_state.sample_dream
        st.rerun()
else:
    dream_text = st.text_area(
        "Enter your dream description:",
        height=150,
        placeholder="Example: Last night I dreamed that I was flying over mountains...",
        label_visibility="collapsed"
    )

# Analyze button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_clicked = st.button(
        "🔍 Analyze Dream with AI",
        type="primary",
        use_container_width=True,
        disabled=not dream_text.strip()
    )

# Analysis section
if analyze_clicked and dream_text.strip():
    with st.spinner("🤖 Analyzing your dream with AI models... This may take 10-20 seconds."):
        # Add small delay for better UX
        time.sleep(1)
        
        # Perform analysis
        result = analyzer.analyze(dream_text)
    
    if result["success"]:
        # Display success message
        st.success("✅ Analysis Complete!")
        
        # Show models used
        if "models_used" in result:
            st.caption(f"**AI Models Used:** {', '.join(result['models_used'])}")
        
        # Create two columns for results
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 🎯 Dream Symbols & Meaning")
            
            if result["symbols"]:
                for symbol in result["symbols"]:
                    with st.expander(f"🔍 {symbol['symbol']} ({symbol['category']})", expanded=True):
                        st.write(f"**Traditional Meaning:** {symbol['meaning']}")
                        st.write(f"**Stress Impact:** {symbol['stress_impact']}/10")
                        
                        # Color code based on stress impact
                        if symbol['stress_impact'] < 4:
                            st.caption("Low stress symbol")
                        elif symbol['stress_impact'] < 7:
                            st.caption("Medium stress symbol")
                        else:
                            st.caption("High stress symbol")
            else:
                st.info("No common dream symbols detected in your description.")
            
            st.markdown("### 😊 Emotional Analysis")
            st.markdown(f"""
            <div class="result-card">
                <h4>Primary Emotion: {result['emotion'].upper()}</h4>
                <p>Confidence: {result['emotion_confidence']*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_right:
            st.markdown("### 📊 Stress Assessment")
            
            # Stress score with visual
            stress_score = result["stress_score"]
            stress_level = result["stress_level"]
            
            # Color-coded metric
            if stress_level == "Low":
                st.metric("Stress Score", f"{stress_score}/10", delta="Low Stress", delta_color="off")
                st.success("✅ Your dream suggests low stress levels")
            elif stress_level == "Medium":
                st.metric("Stress Score", f"{stress_score}/10", delta="Medium Stress", delta_color="off")
                st.warning("⚠️ Your dream indicates moderate stress")
            else:
                st.metric("Stress Score", f"{stress_score}/10", delta="High Stress", delta_color="off")
                st.error("🚨 Your dream suggests high stress levels")
            
            # Progress bar
            st.progress(stress_score / 10)
            
            # Stress explanation
            st.markdown("#### How stress is calculated:")
            st.caption("""
            - **40%**: Stress keywords in dream text
            - **40%**: Stress impact of dream symbols  
            - **20%**: Negative emotion words present
            """)
        
        # Recommendations section
        st.markdown("### 💡 AI-Generated Recommendations")
        st.info("These recommendations are generated by AI based on your dream analysis:")
        
        for i, recommendation in enumerate(result["recommendations"], 1):
            st.markdown(f"""
            <div class="recommendation-item">
                <strong>{i}. {recommendation}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Save to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.analysis_history.append({
            "dream_snippet": dream_text[:50] + "..." if len(dream_text) > 50 else dream_text,
            "stress_score": stress_score,
            "stress_level": stress_level,
            "emotion": result["emotion"],
            "timestamp": timestamp,
            "symbol_count": len(result["symbols"])
        })
        st.session_state.total_analyses += 1
        
        # Export options
        st.markdown("---")
        st.markdown("### 💾 Export Results")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # Export current analysis
            current_data = {
                "Dream": [dream_text[:200]],
                "Stress_Score": [stress_score],
                "Stress_Level": [stress_level],
                "Primary_Emotion": [result["emotion"]],
                "Emotion_Confidence": [result["emotion_confidence"]],
                "Symbols_Found": [", ".join([s["symbol"] for s in result["symbols"]])],
                "Recommendations": [" | ".join(result["recommendations"])],
                "Timestamp": [timestamp]
            }
            df_current = pd.DataFrame(current_data)
            
            st.download_button(
                label="📥 Download This Analysis",
                data=df_current.to_csv(index=False),
                file_name=f"dream_analysis_{timestamp.replace(':', '').replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Export all history
            if st.session_state.analysis_history:
                history_data = []
                for item in st.session_state.analysis_history:
                    history_data.append({
                        "Dream_Snippet": item["dream_snippet"],
                        "Stress_Score": item["stress_score"],
                        "Stress_Level": item["stress_level"],
                        "Emotion": item["emotion"],
                        "Symbol_Count": item["symbol_count"],
                        "Timestamp": item["timestamp"]
                    })
                df_history = pd.DataFrame(history_data)
                
                st.download_button(
                    label="📊 Download All History",
                    data=df_history.to_csv(index=False),
                    file_name="dream_analysis_history.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col_exp3:
            # New analysis button
            if st.button("🔄 Analyze Another Dream", use_container_width=True):
                st.rerun()
    
    else:
        st.error("❌ Analysis failed. Please try again.")
        if "error" in result:
            st.code(result["error"][:200])

elif analyze_clicked and not dream_text.strip():
    st.warning("⚠️ Please enter a dream description before analyzing.")

# Statistics dashboard
if st.session_state.total_analyses > 0:
    st.markdown("---")
    st.markdown("## 📈 Dream Analysis Dashboard")
    
    # Calculate statistics
    total = st.session_state.total_analyses
    avg_stress = sum(h["stress_score"] for h in st.session_state.analysis_history) / total
    high_stress = sum(1 for h in st.session_state.analysis_history if h["stress_level"] == "High")
    low_stress = sum(1 for h in st.session_state.analysis_history if h["stress_level"] == "Low")
    
    # Display metrics
    metric1, metric2, metric3, metric4 = st.columns(4)
    
    with metric1:
        st.metric("Total Dreams", total)
    
    with metric2:
        st.metric("Average Stress", f"{avg_stress:.1f}/10")
    
    with metric3:
        st.metric("High Stress Dreams", high_stress)
    
    with metric4:
        st.metric("Low Stress Dreams", low_stress)
    
    # Stress trend chart
    if total > 1:
        st.markdown("#### Stress Score Trend")
        stress_values = [h["stress_score"] for h in st.session_state.analysis_history]
        dates = [f"Dream {i+1}" for i in range(total)]
        chart_data = pd.DataFrame({"Stress": stress_values}, index=dates)
        st.line_chart(chart_data)
    
    # Common symbols
    if st.session_state.analysis_history:
        st.markdown("#### Most Common Dream Symbols")
        all_symbols = []
        for analysis in st.session_state.analysis_history:
            # This would require storing symbols in history
            pass

# Welcome message for new users
if st.session_state.total_analyses == 0:
    st.markdown("---")
    st.markdown("## 👋 Welcome to Dream Analyzer!")
    st.info("""
    **Get started:**
    1. ✍️ Describe your dream in the text box above
    2. 🔍 Click "Analyze Dream with AI"
    3. 📊 View your results including:
       - Traditional dream symbols (Zhou Gong)
       - AI emotion analysis
       - Stress score (1-10)
       - Personalized recommendations
    
    **Or try a sample dream from the sidebar!**
    """)

# Footer
st.markdown("---")
st.caption("""
**Academic Project | AI Dream Analyzer**  
This tool uses two Hugging Face models for educational purposes.  
Dream interpretations combine traditional Zhou Gong methods with modern AI analysis.  
Always consult qualified professionals for mental health concerns.
""")