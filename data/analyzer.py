"""
Dream Analyzer AI Module
Uses two Hugging Face models:
1. Emotion classification
2. Recommendation generation
"""
import pandas as pd
import streamlit as st
from transformers import pipeline

class DreamAnalyzer:
    """Main analyzer class with two Hugging Face models"""
    
    def __init__(self):
        """Initialize both AI models and load symbols"""
        self.load_models()
        self.dream_symbols = self.load_symbols()
        self.stress_keywords = self.get_stress_keywords()
    
    def load_models(self):
        """Load and cache both Hugging Face models"""
        # Model 1: Emotion classification
        if 'emotion_analyzer' not in st.session_state:
            with st.spinner("Loading emotion model..."):
                st.session_state.emotion_analyzer = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=-1  # Use CPU for Streamlit Cloud
                )
        
        # Model 2: Recommendation generation
        if 'recommendation_generator' not in st.session_state:
            with st.spinner("Loading recommendation model..."):
                st.session_state.recommendation_generator = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-small",  # Small version for memory
                    device=-1
                )
        
        self.emotion_analyzer = st.session_state.emotion_analyzer
        self.recommendation_generator = st.session_state.recommendation_generator
    
    def load_symbols(self):
        """Load Zhou Gong dream symbols from CSV"""
        try:
            symbols_df = pd.read_csv("data/dream_symbols.csv")
            symbols = {}
            for _, row in symbols_df.iterrows():
                symbols[row['symbol']] = {
                    "meaning": row['traditional_meaning'],
                    "stress": row['stress_weight'],
                    "category": row['category']
                }
            return symbols
        except FileNotFoundError:
            # Fallback to default symbols
            return {
                "water": {"meaning": "Wealth and emotional flow", "stress": 2, "category": "nature"},
                "snake": {"meaning": "Transformation and wisdom", "stress": 5, "category": "animals"},
                "falling": {"meaning": "Anxiety and loss of control", "stress": 8, "category": "action"},
                "flying": {"meaning": "Freedom and ambition", "stress": 3, "category": "action"},
                "teeth": {"meaning": "Communication issues", "stress": 6, "category": "body"},
                "money": {"meaning": "Opportunity and value", "stress": 4, "category": "objects"},
                "death": {"meaning": "Endings and new beginnings", "stress": 9, "category": "concepts"},
                "house": {"meaning": "Self and security", "stress": 4, "category": "places"}
            }
    
    def get_stress_keywords(self):
        """Return list of stress-indicating keywords"""
        return [
            "falling", "chase", "lost", "trapped", "failed",
            "late", "death", "attack", "cry", "scream",
            "anxious", "scared", "terrified", "panic",
            "running", "escape", "fight", "war", "crash",
            "drowning", "buried", "trapped", "paralyzed"
        ]
    
    def analyze(self, dream_text):
        """
        Main analysis function using both models
        
        Args:
            dream_text (str): User's dream description
            
        Returns:
            dict: Analysis results with emotions, stress, and recommendations
        """
        try:
            # 1. Analyze emotion using Model 1
            emotion_result = self.analyze_emotion(dream_text)
            
            # 2. Extract dream symbols
            symbols = self.extract_symbols(dream_text)
            
            # 3. Calculate stress score
            stress_score = self.calculate_stress_score(dream_text, symbols)
            stress_level = self.get_stress_level(stress_score)
            
            # 4. Generate recommendations using Model 2
            recommendations = self.generate_ai_recommendations(
                dream_text, emotion_result, stress_score, stress_level, symbols
            )
            
            return {
                "success": True,
                "emotion": emotion_result["label"],
                "emotion_confidence": round(emotion_result["score"], 3),
                "symbols": symbols,
                "stress_score": round(stress_score, 1),
                "stress_level": stress_level,
                "recommendations": recommendations,
                "models_used": ["emotion-distilroberta", "flan-t5-small"]
            }
            
        except Exception as e:
            # Fallback analysis if models fail
            return self.fallback_analysis(dream_text, str(e))
    
    def analyze_emotion(self, text):
        """Use Model 1 to analyze emotions in dream text"""
        # Limit text length for performance
        truncated_text = text[:256]
        result = self.emotion_analyzer(truncated_text)[0]
        return {
            "label": result["label"],
            "score": result["score"]
        }
    
    def extract_symbols(self, text):
        """Extract Zhou Gong dream symbols from text"""
        text_lower = text.lower()
        found_symbols = []
        
        for symbol, info in self.dream_symbols.items():
            if symbol in text_lower:
                found_symbols.append({
                    "symbol": symbol.capitalize(),
                    "meaning": info["meaning"],
                    "stress_impact": info["stress"],
                    "category": info["category"]
                })
        
        # Return top 5 symbols by stress impact
        found_symbols.sort(key=lambda x: x["stress_impact"], reverse=True)
        return found_symbols[:5]
    
    def calculate_stress_score(self, text, symbols):
        """
        Calculate stress score (1-10) based on:
        1. Stress keywords (40%)
        2. Symbol stress impact (40%)
        3. Negative emotion words (20%)
        """
        text_lower = text.lower()
        
        # 1. Keyword stress (max 4 points)
        keyword_count = sum(1 for word in self.stress_keywords if word in text_lower)
        keyword_score = min(4, keyword_count * 0.5)
        
        # 2. Symbol stress (max 4 points)
        symbol_score = 0
        if symbols:
            avg_symbol_stress = sum(s["stress_impact"] for s in symbols) / len(symbols)
            symbol_score = min(4, avg_symbol_stress / 2.5)
        
        # 3. Negative emotion boost (max 2 points)
        negative_words = ["fear", "anxiety", "scared", "terrified", "panic", "worried", "afraid"]
        emotion_boost = 2 if any(word in text_lower for word in negative_words) else 0
        
        # Calculate total (0-10 scale)
        total_score = keyword_score + symbol_score + emotion_boost
        
        # Ensure score is between 1 and 10
        return max(1, min(10, total_score))
    
    def get_stress_level(self, score):
        """Convert numerical score to categorical level"""
        if score < 4:
            return "Low"
        elif score < 7:
            return "Medium"
        else:
            return "High"
    
    def generate_ai_recommendations(self, dream_text, emotion_result, stress_score, stress_level, symbols):
        """
        Use Model 2 (FLAN-T5) to generate personalized recommendations
        
        Args:
            dream_text: Original dream description
            emotion_result: Emotion analysis results
            stress_score: Calculated stress score
            stress_level: Stress level category
            symbols: Extracted dream symbols
            
        Returns:
            list: 3 personalized recommendations
        """
        try:
            # Prepare context for the model
            symbols_str = ", ".join([s["symbol"] for s in symbols]) if symbols else "No specific symbols"
            
            prompt = f"""
            Dream Analysis Context:
            - Dream snippet: "{dream_text[:80]}..."
            - Primary emotion: {emotion_result['label']} (confidence: {emotion_result['score']:.2f})
            - Stress level: {stress_level} (score: {stress_score}/10)
            - Key symbols: {symbols_str}
            
            Based on this dream analysis, generate 3 personalized wellness recommendations.
            Focus on practical, actionable advice for:
            1. Sleep improvement
            2. Stress management
            3. Emotional wellbeing
            
            Format as a numbered list with clear, concise recommendations.
            """
            
            # Generate with FLAN-T5
            generated = self.recommendation_generator(
                prompt,
                max_length=150,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                truncation=True
            )
            
            # Parse the generated text
            raw_text = generated[0]['generated_text']
            recommendations = self.parse_recommendations(raw_text)
            
            # Ensure we have at least 3 recommendations
            if len(recommendations) >= 3:
                return recommendations[:3]
            else:
                # Fill with basic recommendations if needed
                basic_recs = self.get_basic_recommendations(stress_score)
                return recommendations + basic_recs[:3-len(recommendations)]
                
        except Exception:
            # Fallback to basic recommendations if AI generation fails
            return self.get_basic_recommendations(stress_score)
    
    def parse_recommendations(self, text):
        """Parse AI-generated text into clean recommendations"""
        recommendations = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering (1., 2., 3.) or bullets
            if line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                line = line[3:].strip()
            elif line.startswith('- '):
                line = line[2:].strip()
            elif line.startswith('• '):
                line = line[2:].strip()
            elif ') ' in line and line[0].isdigit():
                line = line.split(') ', 1)[1].strip()
            
            # Only keep substantial recommendations
            if line and len(line) > 15 and not line.startswith('Dream'):
                recommendations.append(line)
        
        return recommendations
    
    def get_basic_recommendations(self, stress_score):
        """Fallback recommendations if AI generation fails"""
        if stress_score < 4:
            return [
                "Maintain a consistent sleep schedule of 7-9 hours",
                "Practice gratitude journaling before bedtime",
                "Continue tracking dreams to identify positive patterns"
            ]
        elif stress_score < 7:
            return [
                "Try 10-minute meditation or deep breathing exercises daily",
                "Reduce caffeine and screen time 2 hours before bed",
                "Establish a relaxing pre-sleep routine (reading, warm bath)"
            ]
        else:
            return [
                "Consider consulting a mental health professional",
                "Practice the 4-7-8 breathing technique for anxiety relief",
                "Create a worry journal to process thoughts before sleep"
            ]
    
    def fallback_analysis(self, dream_text, error_msg):
        """Provide basic analysis if models fail"""
        symbols = self.extract_symbols(dream_text)
        stress_score = 5.0  # Default medium stress
        
        return {
            "success": True,
            "emotion": "neutral",
            "emotion_confidence": 0.5,
            "symbols": symbols,
            "stress_score": stress_score,
            "stress_level": "Medium",
            "recommendations": self.get_basic_recommendations(stress_score),
            "models_used": ["fallback_mode"],
            "note": f"Using fallback analysis (AI error: {error_msg[:50]})"
        }