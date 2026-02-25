import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add current directory to path
sys.path.insert(0, '.')

print("Loading application...")

try:
    # Try to import and run with uvicorn
    import uvicorn
    from app.main import app
    
    print("✅ Application loaded successfully")
    print("")
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/v1/docs")
    print("Press CTRL+C to stop")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("")
    print("Please install dependencies:")
    print("  pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings")
    print("  pip install python-jose passlib python-multipart redis psycopg2-binary")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
