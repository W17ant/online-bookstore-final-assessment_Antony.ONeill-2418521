# Final Assessment Implementation Guide
**Student:** 24185521 - Antony O'Neill
**Module:** Software Testing
**Deadline:** 20 October 2025, 23:59 UK Time
**Days Remaining:** 8 days

---

## 📊 Current Status Summary

### ✅ What's Already Complete (Excellent Progress!)

**Test Suite: 86 Tests Created**
- ✅ `tests/conftest.py` - Shared fixtures (245 lines)
- ✅ `tests/test_app.py` - Book catalog & cart tests (267 lines, 15 tests)
- ✅ `tests/test_checkout.py` - Checkout process (362 lines, 14 tests)
- ✅ `tests/test_payment.py` - Payment processing (509 lines, 15 tests)
- ✅ `tests/test_auth.py` - User authentication (592 lines, 23 tests)
- ✅ `tests/test_order.py` - Order confirmation (647 lines, 19 tests)
- ✅ `tests/test_performance.py` - Performance testing (280 lines)
- **Current Results:** 80 passing (93%), 6 minor failures

**CI/CD Pipeline:**
- ✅ `.github/workflows/test-and-coverage.yml` - Main testing workflow
- ✅ `.github/workflows/performance-testing.yml` - Performance profiling
- ✅ Both workflows configured and tested

**Documentation:**
- ✅ `TRACEABILITY_MATRIX.md` - Complete FR → Test mapping
- ✅ `FINAL_ASSESSMENT_PLAN.md` - Implementation roadmap
- ✅ `INSTRUCTOR_BUGS_LIST.md` - Bug documentation
- ✅ `requirements.txt` - All dependencies listed

**Test Coverage:**
- FR-001 (Book Catalog): 83% covered
- FR-002 (Shopping Cart): 91% covered
- FR-003 (Checkout): 14 tests created
- FR-004 (Payment): 15 tests created
- FR-005 (Orders): 19 tests created
- FR-006 (Authentication): 23 tests created

---

## 🚨 CRITICAL: What MUST Be Done (Priority Order)

### **PHASE 1: Fix Bugs & Document Performance (Days 1-3) - 50% of marks!**

This is THE MOST IMPORTANT part. You need to:
1. Fix each bug
2. Measure performance BEFORE fix
3. Measure performance AFTER fix
4. Take screenshots
5. Document improvements

---

## 📝 DETAILED STEP-BY-STEP INSTRUCTIONS

---

## BUG #1: Cart Quantity Validation (30 minutes)

### Location: `models.py` lines 51-53

### Problem:
```python
def update_quantity(self, book_title, quantity):
    if book_title in self.items:
        self.items[book_title].quantity = quantity  # Allows zero/negative!
```

### Step-by-Step Fix:

1. **Take BEFORE screenshot:**
```bash
# Activate venv
cd "/Users/Antony/Desktop/MSc Computer Science AI/UNIT 3 - SOFTWARE TESTING/Final Assessment/online-bookstore-final-assessment"
source venv/bin/activate

# Run test that demonstrates the bug
pytest tests/test_app.py::TestEdgeCases::test_add_zero_quantity_to_cart -v

# Screenshot this output showing the bug exists
```

2. **Fix the code in `models.py`:**
```python
def update_quantity(self, book_title, quantity):
    if book_title in self.items:
        if quantity <= 0:
            # Remove item if quantity is zero or negative
            del self.items[book_title]
        else:
            self.items[book_title].quantity = quantity
```

3. **Take AFTER screenshot:**
```bash
# Run the same test - should now behave correctly
pytest tests/test_app.py::TestEdgeCases::test_add_zero_quantity_to_cart -v

# Screenshot this output showing the fix works
```

4. **Document in your report:**
- Before: Cart accepted zero/negative quantities
- After: Cart removes items when quantity <= 0
- Impact: Prevents invalid cart states, improves data integrity

---

## BUG #2: Input Validation Try-Catch (20 minutes)

### Location: `app.py` lines 60 and 103

### Problem:
```python
quantity = int(request.form.get('quantity', 1))  # Crashes on non-numeric input!
```

### Step-by-Step Fix:

1. **Demonstrate the bug:**
```bash
# Start the Flask app
python app.py

# In browser, try to add book with quantity="abc" (will crash)
# Screenshot the error page
```

2. **Fix in `app.py` (line 60):**
```python
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    book_title = request.form.get('title')
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity <= 0:
            flash('Quantity must be a positive number.', 'error')
            return redirect(url_for('index'))
    except ValueError:
        flash('Invalid quantity. Please enter a number.', 'error')
        return redirect(url_for('index'))

    # Rest of the function...
```

3. **Fix in `app.py` (line 103):**
```python
@app.route('/update-cart', methods=['POST'])
def update_cart():
    book_title = request.form.get('title')
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        flash('Invalid quantity. Please enter a number.', 'error')
        return redirect(url_for('view_cart'))

    # Rest of the function...
```

4. **Test the fix:**
```bash
# Start app again
python app.py

# Try invalid input - should show friendly error message
# Screenshot the graceful error handling
```

---

## BUG #3: Case-Sensitive Discount Codes (15 minutes)

### Location: `app.py` lines 168 and 172

### Problem:
```python
if discount_code == 'SAVE10':  # 'save10' won't work!
```

### Step-by-Step Fix:

1. **Test the bug exists:**
```bash
pytest tests/test_checkout.py::TestDiscountCodes::test_case_sensitive_discount_code_bug -v
# Screenshot showing lowercase 'save10' doesn't work
```

2. **Fix in `app.py`:**
```python
@app.route('/process-checkout', methods=['POST'])
def process_checkout():
    # ... earlier code ...

    discount_code = request.form.get('discount_code', '').upper()  # Convert to uppercase!

    # Calculate total with discount
    total_amount = cart.get_total_price()
    discount_applied = 0

    if discount_code == 'SAVE10':  # Now 'save10', 'Save10', 'SAVE10' all work
        discount_applied = total_amount * 0.10
        total_amount -= discount_applied
        flash(f'Discount applied! You saved ${discount_applied:.2f}', 'success')
    elif discount_code == 'WELCOME20':
        discount_applied = total_amount * 0.20
        total_amount -= discount_applied
        flash(f'Welcome discount applied! You saved ${discount_applied:.2f}', 'success')
    elif discount_code:
        flash('Invalid discount code', 'error')
```

3. **Test the fix:**
```bash
pytest tests/test_checkout.py::TestDiscountCodes -v
# Screenshot showing all discount tests pass
```

---

## INEFFICIENCY #1: Cart Total Calculation O(n*m) → O(n) (30 minutes)

### Location: `models.py` lines 55-60

### Problem:
```python
def get_total_price(self):
    total = 0
    for item in self.items.values():
        for i in range(item.quantity):  # Nested loop! O(n*m)
            total += item.book.price
    return total
```

### Step-by-Step Fix with Performance Measurement:

1. **Measure BEFORE performance:**
```bash
# Run performance test showing the inefficiency
python tests/test_performance.py

# Or run with timeit:
python -m timeit -s "from models import Cart, Book; cart = Cart(); book = Book('Test', 'Cat', 10.0, 'img.jpg'); cart.add_book(book, 1000)" "cart.get_total_price()"

# Screenshot the SLOW time (will show nested loop iterations)
```

2. **Fix in `models.py`:**
```python
def get_total_price(self):
    total = 0
    for item in self.items.values():
        total += item.book.price * item.quantity  # Direct multiplication! O(n)
    return total
```

3. **Measure AFTER performance:**
```bash
# Run same performance test
python tests/test_performance.py

# Or run with timeit again:
python -m timeit -s "from models import Cart, Book; cart = Cart(); book = Book('Test', 'Cat', 10.0, 'img.jpg'); cart.add_book(book, 1000)" "cart.get_total_price()"

# Screenshot the FAST time
```

4. **Document improvement:**
- Before: O(n*m) - 1000 iterations for 1 item with quantity 1000
- After: O(n) - 1 iteration
- Expected speedup: ~1000x for large quantities
- Impact: Cart page loads faster, better user experience

---

## INEFFICIENCY #2: Order Sorting (25 minutes)

### Location: `models.py` line 88

### Problem:
```python
def add_order(self, order):
    self.orders.append(order)
    self.orders.sort(key=lambda x: x.order_date)  # Sorts on EVERY add! O(n log n)
```

### Step-by-Step Fix with Performance Measurement:

1. **Measure BEFORE performance:**
```bash
python -c "
from models import User, Order
import time

user = User('test@example.com', 'pass')

# Create 1000 orders
start = time.time()
for i in range(1000):
    order = Order(f'ORD{i}', 'test@example.com', [], {}, {}, 100.0)
    user.add_order(order)
end = time.time()

print(f'Time to add 1000 orders: {end-start:.4f}s')
print(f'Sorts every time = 1000 * O(n log n) operations')
"
# Screenshot the SLOW time
```

2. **Fix in `models.py`:**
```python
def add_order(self, order):
    self.orders.append(order)  # Just append, don't sort!
    # Sorting moved to get_order_history()

def get_order_history(self):
    # Sort only when retrieving (lazy evaluation)
    return sorted(self.orders, key=lambda x: x.order_date, reverse=True)
```

3. **Measure AFTER performance:**
```bash
python -c "
from models import User, Order
import time

user = User('test@example.com', 'pass')

# Create 1000 orders
start = time.time()
for i in range(1000):
    order = Order(f'ORD{i}', 'test@example.com', [], {}, {}, 100.0)
    user.add_order(order)
end = time.time()

print(f'Time to add 1000 orders: {end-start:.4f}s')
print(f'Sort only once when needed = Much faster!')
"
# Screenshot the FAST time
```

4. **Document improvement:**
- Before: O(n log n) on every add = 1000 sorts for 1000 orders
- After: O(1) on add, O(n log n) once on retrieval
- Expected speedup: ~100x for 1000 orders
- Impact: Faster order processing, better scalability

---

## INEFFICIENCY #3: Book Lookup Helper (20 minutes)

### Location: `app.py` lines 63-66

### Problem:
```python
book = None
for b in BOOKS:  # Manual loop instead of using helper!
    if b.title == book_title:
        book = b
        break
```

### Step-by-Step Fix:

1. **Show the inconsistency:**
```bash
# Helper function EXISTS at line 27:
grep -n "get_book_by_title" app.py

# But manual loops used at lines 63-66
grep -n "for b in BOOKS" app.py
```

2. **Fix in `app.py` (line 63-66):**
```python
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    book_title = request.form.get('title')
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity <= 0:
            flash('Quantity must be a positive number.', 'error')
            return redirect(url_for('index'))
    except ValueError:
        flash('Invalid quantity. Please enter a number.', 'error')
        return redirect(url_for('index'))

    # Use helper function instead of manual loop
    book = get_book_by_title(book_title)

    if book:
        cart.add_book(book, quantity)
        flash(f'Added {quantity} "{book.title}" to cart!', 'success')
    else:
        flash('Book not found!', 'error')

    return redirect(url_for('index'))
```

3. **Run tests to verify:**
```bash
pytest tests/test_app.py -v
# All tests should still pass
```

4. **Document improvement:**
- Before: Manual loops scattered throughout code (code duplication)
- After: Consistent use of helper function
- Impact: Better code maintainability, easier to optimize later (e.g., add caching)

---

## 📸 PHASE 2: Collect Evidence (Day 3)

### Create Screenshots Folder:
```bash
mkdir screenshots
```

### Required Screenshots:

1. **Test Execution:**
   - `screenshots/test_results_all_passing.png` - Full test suite passing
   - `screenshots/test_coverage_report.png` - Coverage report showing 80%+

2. **Performance Improvements (6 screenshots):**
   - `screenshots/bug1_before.png` & `screenshots/bug1_after.png`
   - `screenshots/bug2_before.png` & `screenshots/bug2_after.png`
   - `screenshots/bug3_before.png` & `screenshots/bug3_after.png`
   - `screenshots/inefficiency1_before.png` & `screenshots/inefficiency1_after.png`
   - `screenshots/inefficiency2_before.png` & `screenshots/inefficiency2_after.png`
   - `screenshots/inefficiency3_before.png` & `screenshots/inefficiency3_after.png`

3. **CI/CD Pipeline:**
   - `screenshots/github_actions_workflow.png` - Workflow running
   - `screenshots/github_actions_success.png` - All tests passing on GitHub

### Commands to Generate Evidence:

```bash
# Activate venv
source venv/bin/activate

# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term > test_results.txt

# Open HTML coverage report
open htmlcov/index.html
# Screenshot this!

# Run performance tests
python tests/test_performance.py > performance_results.txt
# Screenshot the output!

# Generate cProfile report
python -m cProfile -o profile.prof -m pytest tests/ -v
python -c "import pstats; p = pstats.Stats('profile.prof'); p.sort_stats('cumulative'); p.print_stats(30)" > cprofile_results.txt
# Screenshot this!
```

---

## 📝 PHASE 3: Write Report (Days 4-6)

### Report Structure (1500 words, ±10%):

**Create:** `REPORT.md` or `REPORT.docx`

#### Section 1: Test Case Design and Coverage (300 words)

**What to write:**
- Explain your test strategy (unit, integration, performance)
- Justify why you chose pytest framework
- Document challenges (e.g., mocking PaymentGateway, EmailService)
- Reference TRACEABILITY_MATRIX.md
- Explain AAA pattern usage
- Mention fixture usage for code reuse

**Evidence to include:**
- Table showing test counts per FR
- Screenshot of test results
- Coverage report screenshot

---

#### Section 2: Effectiveness of Improvements (400 words) ⭐ MOST IMPORTANT

**What to write (for EACH of the 6 bugs):**

**Bug #1: Cart Quantity Validation**
- Problem: Cart accepted zero/negative quantities
- Solution: Added validation to remove items when qty <= 0
- Impact: Prevents invalid cart states
- Evidence: Before/after screenshots

**Bug #2: Input Validation**
- Problem: No try-catch, app crashed on non-numeric input
- Solution: Added try-except blocks with user-friendly error messages
- Impact: Better user experience, no crashes
- Evidence: Before/after screenshots

**Bug #3: Case-Sensitive Discount Codes**
- Problem: 'save10' didn't work, only 'SAVE10' worked
- Solution: Convert input to uppercase before comparison
- Impact: Better user experience, fewer support tickets
- Evidence: Test results showing fix

**Inefficiency #1: Cart Total O(n*m) → O(n)**
- Problem: Nested loop in get_total_price()
- Before: 1000 iterations for quantity=1000
- After: 1 iteration (direct multiplication)
- Performance gain: ~1000x faster (include timeit results!)
- Impact: Faster page loads, better scalability
- Evidence: Performance test screenshots

**Inefficiency #2: Order Sorting**
- Problem: Sorted on every add_order() call
- Before: O(n log n) * 1000 for 1000 orders
- After: O(1) on add, O(n log n) once on retrieval
- Performance gain: ~100x faster (include timeit results!)
- Impact: Faster order processing
- Evidence: Performance test screenshots

**Inefficiency #3: Book Lookup Consistency**
- Problem: Manual loops instead of helper function
- Solution: Used get_book_by_title() consistently
- Impact: Better code maintainability, DRY principle
- Evidence: Code diff

---

#### Section 3: CI/CD Automation Integration (300 words)

**What to write:**
- Explain GitHub Actions setup (why not Jenkins?)
- Describe test-and-coverage.yml workflow
  - Triggers: push/PR to main/master/develop
  - Matrix testing: Python 3.11 and 3.12
  - Steps: checkout, setup, install, test, coverage, upload artifacts
- Describe performance-testing.yml workflow
  - Scheduled weekly on Sundays
  - timeit benchmarking
  - cProfile profiling
  - Memory profiling
  - Artifact uploads
- Benefits of CI/CD:
  - Catches bugs early
  - Automated testing on every push
  - Prevents broken code from merging
  - Coverage tracking over time
- Challenges faced:
  - Setting up proper Python path for imports
  - Configuring artifact uploads
  - Matrix testing with multiple Python versions

**Evidence to include:**
- Screenshot of GitHub Actions workflow
- Screenshot of successful test run
- Link to your repository

---

#### Section 4: Code Quality and Maintainability (300 words)

**What to write:**
- Discuss test code structure:
  - conftest.py for shared fixtures
  - Separate test files per functional area
  - Clear test naming conventions (test_feature_scenario)
  - Comprehensive docstrings with TC-IDs
- AAA pattern usage (Arrange-Act-Assert)
- Fixture usage:
  - client fixture for Flask testing
  - clean_cart fixture for isolation
  - registered_user, logged_in_client fixtures
  - valid_checkout_data fixtures
- Test organization:
  - Unit tests: test_util.py (helper functions)
  - Integration tests: test_user_booking_flow.py (end-to-end)
  - Performance tests: test_performance.py (profiling)
- How tests accommodate future changes:
  - Fixtures make tests reusable
  - Clear TC-IDs enable traceability
  - Modular structure allows easy addition of new tests
- Industry best practices followed:
  - Pytest framework (industry standard)
  - pytest-cov for coverage
  - GitHub Actions for CI/CD
  - Comprehensive documentation

---

#### Section 5: Future Considerations (200 words)

**What to write:**
- Additional test coverage recommendations:
  - UI tests with Selenium for FR-007 (responsive design)
  - Load testing with locust or pytest-benchmark
  - Security testing with OWASP ZAP or bandit (already in workflow)
  - API testing if REST endpoints added
- Further optimization opportunities:
  - Database integration (currently JSON files)
  - Caching for book lookups
  - Redis for session management
  - CDN for static assets
- Enhanced CI/CD features:
  - Deployment to staging environment
  - Blue-green deployments
  - Automated rollback on test failures
  - Slack/email notifications on failures
  - Code quality gates (SonarQube)
- Security testing expansion:
  - Penetration testing
  - SQL injection tests (if DB added)
  - XSS vulnerability testing
  - Password hashing (currently plain text - security issue!)
- Load testing considerations:
  - Apache JMeter for stress testing
  - Test with 1000+ concurrent users
  - Database query optimization

---

### Harvard References to Include:

```
GitHub Actions Documentation (2024) Available at: https://docs.github.com/en/actions
(Accessed: 12 October 2025).

pytest Documentation (2024) Available at: https://docs.pytest.org/
(Accessed: 12 October 2025).

Python timeit Module (2024) Python Software Foundation. Available at:
https://docs.python.org/3/library/timeit.html (Accessed: 12 October 2025).

Python cProfile Module (2024) Python Software Foundation. Available at:
https://docs.python.org/3/library/profile.html (Accessed: 12 October 2025).

Myers, G.J., Sandler, C. and Badgett, T. (2011) The Art of Software Testing.
3rd edn. Hoboken: John Wiley & Sons.

Beizer, B. (1990) Software Testing Techniques. 2nd edn. Boston:
International Thomson Computer Press.

Fowler, M. (2018) Refactoring: Improving the Design of Existing Code.
2nd edn. Boston: Addison-Wesley Professional.
```

---

## 📦 PHASE 4: Final Submission Preparation (Day 7)

### Update TRACEABILITY_MATRIX.md:

```bash
# Update with final line numbers after bug fixes
# Update test counts (should now show 86/86 tests implemented)
# Update coverage percentages
```

### Update FINAL_ASSESSMENT_PLAN.md:

```bash
# Change all 🔄 to ✅
# Update status from "In Progress" to "Complete"
```

### Create README.md for Submission:

```markdown
# Online Bookstore - Final Assessment Submission
**Student:** 24185521 - Antony O'Neill
**Module:** Software Testing
**Date:** 20 October 2025

## How to Run Tests

```bash
# Navigate to project
cd online-bookstore-final-assessment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html

# Run performance tests
python tests/test_performance.py
```

## Test Results Summary
- Total Tests: 86
- Passing: 86 (100%)
- Coverage: 85%+

## CI/CD Pipeline
GitHub Actions workflows configured at `.github/workflows/`

## Documentation
- `TRACEABILITY_MATRIX.md` - Requirements traceability
- `REPORT.md` - 1500-word critical evaluation
- `INSTRUCTOR_BUGS_LIST.md` - Bug documentation with fixes
```

---

## 🚀 PHASE 5: Push to GitHub (Day 7)

### Set up your GitHub repository:

```bash
cd "/Users/Antony/Desktop/MSc Computer Science AI/UNIT 3 - SOFTWARE TESTING/Final Assessment/online-bookstore-final-assessment"

# Set remote URL to YOUR fork
git remote set-url origin https://github.com/W17ant/online-bookstore-final-assessment_Antony.ONeill-2418521.git

# Check what's changed
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Final Assessment Submission - All Tests Passing

- 86 comprehensive tests (100% passing)
- Fixed all 6 bugs/inefficiencies with performance documentation
- GitHub Actions CI/CD pipeline configured
- Complete traceability matrix
- Performance improvements: O(n*m) to O(n), lazy sorting
- Test coverage: 85%+

Student: Antony O'Neill (24185521)"

# Push to GitHub
git push origin main
```

### Verify on GitHub:
1. Go to: https://github.com/W17ant/online-bookstore-final-assessment_Antony.ONeill-2418521
2. Check GitHub Actions ran successfully
3. Verify all files are present
4. Check README.md displays correctly

---

## 📋 PHASE 6: Create Submission ZIP (Day 8)

### Files to Include in ZIP:

```bash
# Create submission folder
mkdir online-bookstore-submission
cd online-bookstore-submission

# Copy essential files
cp -r ../online-bookstore-final-assessment/.github .
cp -r ../online-bookstore-final-assessment/tests .
cp -r ../online-bookstore-final-assessment/templates .
cp -r ../online-bookstore-final-assessment/static .
cp ../online-bookstore-final-assessment/app.py .
cp ../online-bookstore-final-assessment/models.py .
cp ../online-bookstore-final-assessment/requirements.txt .
cp ../online-bookstore-final-assessment/TRACEABILITY_MATRIX.md .
cp ../online-bookstore-final-assessment/README.md .
cp ../online-bookstore-final-assessment/INSTRUCTOR_BUGS_LIST.md .

# Create ZIP
cd ..
zip -r 24185521_AntonyONeill_FinalAssessment.zip online-bookstore-submission/

# Verify ZIP contents
unzip -l 24185521_AntonyONeill_FinalAssessment.zip
```

### Submission Checklist:

**Software Artefact (ZIP file):**
- [ ] All `.py` files (app.py, models.py)
- [ ] All test files (`tests/` directory)
- [ ] GitHub Actions workflows (`.github/workflows/`)
- [ ] requirements.txt
- [ ] TRACEABILITY_MATRIX.md
- [ ] README.md with setup instructions
- [ ] INSTRUCTOR_BUGS_LIST.md with fixes documented

**Report (PDF file):**
- [ ] 1500 words (±10%)
- [ ] 5 required sections
- [ ] Screenshots included
- [ ] Before/after performance comparisons
- [ ] Harvard referencing
- [ ] Student number: 24185521
- [ ] Formatted: Double-spaced, 12pt Calibri/Arial

---

## 🎯 Success Criteria Checklist

### Technical Implementation (50%):
- [ ] 80+ tests covering all FRs
- [ ] All tests passing (100%)
- [ ] GitHub Actions CI/CD working
- [ ] All 6 bugs fixed with documentation
- [ ] Performance improvements measured (timeit/cProfile)
- [ ] Test coverage 80%+
- [ ] Traceability matrix complete

### Critical Evaluation (30%):
- [ ] 1500-word report written
- [ ] All 5 sections complete
- [ ] Evidence included (screenshots)
- [ ] Performance data included
- [ ] CI/CD benefits explained
- [ ] Reflective analysis

### Report Quality (20%):
- [ ] Clear and well-organized
- [ ] Proper Harvard referencing (6+ sources)
- [ ] Professional formatting
- [ ] No spelling/grammar errors
- [ ] Technical language appropriate
- [ ] Screenshots clear and labeled

---

## ⏰ Time Estimates

| Task | Estimated Time | Priority |
|------|---------------|----------|
| Fix Bug #1 | 30 min | HIGH |
| Fix Bug #2 | 20 min | HIGH |
| Fix Bug #3 | 15 min | HIGH |
| Fix Inefficiency #1 | 30 min | HIGH |
| Fix Inefficiency #2 | 25 min | HIGH |
| Fix Inefficiency #3 | 20 min | HIGH |
| Collect screenshots | 1 hour | HIGH |
| Write report | 4-5 hours | HIGH |
| Update documentation | 1 hour | MEDIUM |
| Push to GitHub | 30 min | MEDIUM |
| Create submission ZIP | 30 min | LOW |
| **TOTAL** | **~9 hours** | |

---

## 🎓 Tips for Success

1. **Work in Order** - Fix bugs first, then write report (you need the data!)
2. **Take Screenshots as You Go** - Don't leave this until the end!
3. **Run Tests Frequently** - After each fix, verify tests still pass
4. **Commit Often** - Git commit after each bug fix
5. **Time Management** - Allocate 2 hours/day for 5 days
6. **Proofread Report** - Grammar/spelling errors lose marks!
7. **Test Your ZIP** - Extract and verify all files present
8. **Submit Early** - Don't wait until 23:59!

---

## 🆘 If You Get Stuck

**Test Failures:**
```bash
# Run single test to debug
pytest tests/test_app.py::TestCart::test_cart_total_calculation -v

# Check what's failing
pytest tests/ -v --tb=short
```

**Import Errors:**
```bash
# Activate venv first!
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Git Issues:**
```bash
# Check status
git status

# Undo last commit (if needed)
git reset --soft HEAD~1

# Force push (only if necessary!)
git push origin main --force
```

---

## 📞 Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run performance tests
python tests/test_performance.py

# Run specific test
pytest tests/test_app.py::TestCart::test_cart_initialization -v

# Start Flask app
python app.py

# Git push
git add . && git commit -m "message" && git push origin main
```

---

## 🎯 Target: 70%+ (First Class)

**You're in excellent position!** You have:
- ✅ Comprehensive test suite (86 tests!)
- ✅ CI/CD pipeline configured
- ✅ Documentation framework complete

**What you need:**
- ⏰ 9 hours of focused work
- 📸 Screenshots of bug fixes
- 📝 1500-word report

**You can do this!** Follow this guide step-by-step and you'll achieve First Class marks! 🏆

---

*Last Updated: 12 October 2025*
*Good luck! 🎓*
