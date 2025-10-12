# 📸 Screenshots for Final Assessment Report

**Student:** 24185521 - Antony O'Neill

This folder contains performance testing and test execution screenshots for the 1500-word critical evaluation report.

---

## 📋 Required Screenshots

### **Priority 1: Must Have**

#### 1. `test_results.png`
**What to capture:** Terminal output of full test suite
**Command:**
```bash
cd "/Users/Antony/Desktop/MSc Computer Science AI/UNIT 3 - SOFTWARE TESTING/Final Assessment/online-bookstore-final-assessment"
source venv/bin/activate
pytest tests/ -v
```
**Shows:** 86/86 tests passing, 100% pass rate

---

#### 2. `coverage_report.png`
**What to capture:** HTML coverage report main page
**Command:**
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```
**Shows:** 85% overall coverage, 95% models.py, 79% app.py

---

#### 3. `timeit_performance.png`
**What to capture:** Terminal output of performance benchmarks
**Command:**
```bash
python tests/test_performance.py
```
**Shows:** O(n*m) → O(n) optimization, 100x improvement

---

### **Priority 2: Highly Recommended**

#### 4. `locust_statistics.png`
**What to capture:** Locust Statistics tab
**Steps:**
1. Terminal 1: `python app.py`
2. Terminal 2: `locust -f locustfile.py`
3. Browser: http://localhost:8089
4. Set: 50 users, spawn rate 5, host http://localhost:5000
5. Run for 2-3 minutes
6. Screenshot Statistics tab

**Shows:** Requests per second, response times, failure rates

---

#### 5. `locust_charts.png`
**What to capture:** Locust Charts tab
**Shows:** Visual graphs of RPS and response times over time

---

## 📝 Screenshot Checklist

Before pushing to GitHub:
- [ ] test_results.png (86/86 passing)
- [ ] coverage_report.png (85% coverage)
- [ ] timeit_performance.png (O(n*m)→O(n) proof)
- [ ] locust_statistics.png (load testing metrics)
- [ ] locust_charts.png (performance graphs)

---

## 🎨 Tips for Good Screenshots

1. **Use high resolution** - Make text readable
2. **Crop appropriately** - Remove unnecessary UI
3. **Highlight key metrics** - Use arrows or boxes if needed
4. **Use consistent naming** - Follow the names above
5. **Keep originals** - Don't compress PNG files

---

## 📊 What Each Screenshot Proves

| Screenshot | Proves | Report Section |
|-----------|--------|----------------|
| test_results.png | 100% test pass rate | Section 2 & 4 |
| coverage_report.png | 85% code coverage | Section 4 |
| timeit_performance.png | Algorithmic optimization | Section 3 |
| locust_statistics.png | Load testing results | Section 3 |
| locust_charts.png | Performance under load | Section 3 |

---

## 🚀 Quick Commands

Save these screenshots in THIS folder, then:

```bash
# Check what you've added
ls -la screenshots/

# Add to git
git add screenshots/

# Commit
git commit -m "Add performance and testing screenshots"

# Push
git push origin main
```

---

**Status:** Folder ready - add your screenshots here!

*Last Updated: 12 October 2025*
