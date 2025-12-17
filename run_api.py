"""
Run Flask API Server
Start the Mental Health Chatbot API on localhost:5000

Usage:
  python run_api.py

Then in another terminal:
  python manual_test_api.py
"""

from app import create_app


if __name__ == '__main__':
    print("=" * 80)
    print("Starting Mental Health Chatbot API".center(80))
    print("=" * 80)
    
    app = create_app()
    
    print("\n✅ API Server Starting...\n")
    print("🌐 Access the API at: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("📚 API health: http://localhost:5000/api/health")
    print("\n📖 API Documentation: See PHASE4_API_DOCS.txt\n")
    print("💡 To test endpoints, run in another terminal: python manual_test_api.py\n")
    print("🛑 Press CTRL+C to stop the server\n")
    print("=" * 80 + "\n")
    
    # Run the server
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)