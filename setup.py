"""
Setup script for Dream Analyzer project
"""
import os
import sys

def setup_project():
    """Setup the Dream Analyzer project"""
    print("🚀 Setting up Dream Analyzer...")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs(".streamlit", exist_ok=True)
    
    print("✅ Created directories: data/, .streamlit/")
    
    # Create requirements.txt if it doesn't exist
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("""streamlit==1.28.0
transformers==4.35.0
torch==2.1.0
pandas==2.1.3
protobuf==3.20.3
sentencepiece==0.1.99""")
        print("✅ Created requirements.txt")
    
    # Create config.toml if it doesn't exist
    if not os.path.exists(".streamlit/config.toml"):
        with open(".streamlit/config.toml", "w") as f:
            f.write("""[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
""")
        print("✅ Created .streamlit/config.toml")
    
    # Create dream_symbols.csv if it doesn't exist
    if not os.path.exists("data/dream_symbols.csv"):
        with open("data/dream_symbols.csv", "w") as f:
            f.write("""symbol,traditional_meaning,stress_weight,category
water,Wealth and emotional flow,2,nature
snake,Transformation and wisdom,5,animals
falling,Anxiety and loss of control,8,action
flying,Freedom and ambition,3,action
teeth,Communication issues,6,body
money,Opportunity and value,4,objects
death,Endings and new beginnings,9,concepts
house,Self and security,4,places
car,Journey and direction,3,objects
fire,Passion and destruction,7,elements
ocean,Emotions and subconscious,3,nature
bird,Freedom and messages,2,animals
exam,Evaluation and pressure,7,education
running,Escape or pursuit,6,action
rain,Cleansing and renewal,3,nature
bridge,Transition and connection,4,objects""")
        print("✅ Created data/dream_symbols.csv")
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the app: streamlit run app.py")
    print("3. Open browser: http://localhost:8501")
    print("\n🌐 For Streamlit Cloud deployment:")
    print("   - Push to GitHub")
    print("   - Deploy at: share.streamlit.io")

if __name__ == "__main__":
    setup_project()