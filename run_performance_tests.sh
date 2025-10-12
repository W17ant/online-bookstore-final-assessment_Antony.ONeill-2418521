#!/bin/bash
# Performance Testing Runner Script
# Student: 24185521 - Antony O'Neill

echo "=========================================================================="
echo "   PERFORMANCE TESTING SUITE - Online Bookstore"
echo "   Student: 24185521 - Antony O'Neill"
echo "=========================================================================="

# Activate virtual environment
source venv/bin/activate

# Function to run timeit benchmarks
run_timeit() {
    echo ""
    echo "📊 Running Python timeit Benchmarks..."
    echo "=========================================================================="
    python tests/test_performance.py
    echo ""
    echo "✅ timeit benchmarks complete!"
    echo "📸 Screenshot the terminal output for your report!"
    echo ""
}

# Function to provide Locust instructions
run_locust() {
    echo ""
    echo "🚀 Starting Locust Load Testing..."
    echo "=========================================================================="
    echo ""
    echo "⚠️  IMPORTANT: You need TWO terminals for this!"
    echo ""
    echo "Terminal 1 (Flask App):"
    echo "  cd '$(pwd)'"
    echo "  source venv/bin/activate"
    echo "  python app.py"
    echo ""
    echo "Terminal 2 (Locust):"
    echo "  cd '$(pwd)'"
    echo "  source venv/bin/activate"
    echo "  locust -f locustfile.py"
    echo ""
    echo "Then:"
    echo "  1. Open browser: http://localhost:8089"
    echo "  2. Set: 50 users, spawn rate 5, host http://localhost:5000"
    echo "  3. Click 'Start swarming'"
    echo "  4. Wait 2-3 minutes for stable metrics"
    echo "  5. Take screenshots (Statistics & Charts tabs)"
    echo ""
    echo "=========================================================================="
}

# Function to run security scan
run_security() {
    echo ""
    echo "🛡️  Running Bandit Security Scan..."
    echo "=========================================================================="
    bandit -r . -ll --exclude ./venv,./tests,./.github
    echo ""
    echo "✅ Security scan complete!"
    echo ""
    echo "📊 Summary:"
    echo "   - 1 HIGH severity issue (Flask debug=True - acceptable for demo)"
    echo "   - 11 LOW severity issues (hardcoded keys, weak RNG - acceptable for demo)"
    echo ""
    echo "📸 Screenshot the terminal output for your report!"
    echo "📄 See SECURITY_TESTING_GUIDE.md for detailed analysis"
    echo ""
}

# Main menu
echo ""
echo "Select test to run:"
echo ""
echo "  1) Run timeit benchmarks (automatic)"
echo "  2) Get Locust instructions (manual - requires 2 terminals)"
echo "  3) Run Bandit security scan (automatic)"
echo "  4) Run all automatic tests (timeit + security + coverage)"
echo "  5) Generate coverage report"
echo "  6) Run full test suite"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        run_timeit
        ;;
    2)
        run_locust
        ;;
    3)
        run_security
        ;;
    4)
        echo ""
        echo "🔬 Running all automatic tests..."
        echo ""
        run_timeit
        echo ""
        echo "Press Enter to continue to security scan..."
        read
        run_security
        echo ""
        echo "Press Enter to continue to coverage report..."
        read
        echo ""
        echo "📊 Generating coverage report..."
        pytest tests/ --cov=. --cov-report=html --cov-report=term
        echo ""
        echo "✅ All automatic tests complete!"
        echo "📂 Opening coverage HTML report..."
        open htmlcov/index.html
        ;;
    5)
        echo ""
        echo "📊 Generating coverage report..."
        pytest tests/ --cov=. --cov-report=html --cov-report=term
        echo ""
        echo "✅ Coverage report generated!"
        echo "📂 Opening HTML report..."
        open htmlcov/index.html
        ;;
    6)
        echo ""
        echo "🧪 Running full test suite..."
        pytest tests/ -v --cov=. --cov-report=term
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================================================="
echo "✅ Done! Check PERFORMANCE_TESTING_GUIDE.md for detailed instructions."
echo "=========================================================================="
