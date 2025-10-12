# Final Assessment Implementation Plan
**Student:** 24185521 - Antony O'Neill
**Deadline:** 20 October 2025, 23:59 UK Time
**Status:** GitHub Actions CI/CD Setup Complete ✅

---

## ✅ What's Been Completed

### 1. GitHub Actions CI/CD Pipeline (PRIMARY REQUIREMENT)
✅ **Main Testing Workflow** (`.github/workflows/test-and-coverage.yml`)
- Automated pytest execution on every push
- Multi-version Python testing (3.11, 3.12)
- Comprehensive coverage reports (XML, HTML, JSON)
- JUnit test results
- HTML test reports
- Automated PR comments with results
- Coverage threshold checking (60% minimum)

✅ **Performance Testing Workflow** (`.github/workflows/performance-testing.yml`)
- Weekly scheduled performance profiling
- timeit benchmarking
- cProfile analysis
- Memory profiling
- Automated artifact uploads

✅ **Quality Checks Workflow** (Integrated)
- Flake8 style checking
- Bandit security scanning
- Safety dependency checks
- Pylint code quality analysis

### 2. Performance Testing Suite
✅ **`tests/test_performance.py`** - Comprehensive performance tests using:
- `timeit` module for micro-benchmarks
- `cProfile` for function-level profiling
- `memory_profiler` for memory usage analysis
- Clear before/after improvement demonstrations

**Tests 4 Key Inefficiencies:**
1. Cart total calculation (O(n*m) → O(n))
2. Book lookup operations (linear → helper function)
3. User order sorting (eager → lazy evaluation)
4. Memory usage analysis

### 3. Traceability Matrix (**ADDRESSES MID-MODULE FEEDBACK**)
✅ **`TRACEABILITY_MATRIX.md`** - Complete mapping:
- FR-001 through FR-007 → Test Scenarios
- Test Scenarios → Test Cases
- Test Cases → Actual Python functions
- Reverse mapping (Function → Requirement)
- Coverage statistics and gap analysis
- Execution evidence documented

### 4. Updated Dependencies
✅ **`requirements.txt`** - Added:
- pytest-html (HTML reports)
- pytest-json-report (JSON results)
- pytest-benchmark (benchmarking)
- memory-profiler (memory analysis)
- flake8, bandit, safety, pylint (quality/security)

### 5. Initial Test Suite
✅ **`tests/test_app.py`** - 15 passing tests covering:
- Book browsing (FR-001)
- Shopping cart operations (FR-002)
- Basic checkout validation
- Edge cases (zero/negative quantities)

---

## 🎯 What Still Needs to be Done

### Part 1: Test Code (Software Artefact) - 50%

#### Priority 1: Expand Test Coverage (CRITICAL)
Current: 15 tests (50% of requirements)
Target: 30+ tests (comprehensive coverage)

**Need to Create:**

1. **`tests/test_checkout.py`** - Checkout process (FR-003)
   ```python
   - test_checkout_page_loads
   - test_checkout_form_validation
   - test_shipping_info_collection
   - test_discount_code_application
   - test_checkout_total_calculation
   ```

2. **`tests/test_payment.py`** - Payment processing (FR-004)
   ```python
   - test_payment_gateway_success
   - test_payment_gateway_failure (card ending in 1111)
   - test_payment_method_credit_card
   - test_payment_method_paypal
   - test_invalid_card_validation
   ```

3. **`tests/test_auth.py`** - User authentication (FR-006)
   ```python
   - test_user_registration_success
   - test_user_registration_duplicate_email
   - test_user_login_success
   - test_user_login_invalid_credentials
   - test_user_session_persistence
   - test_user_logout
   - test_password_hashing_security
   ```

4. **`tests/test_order.py`** - Order confirmation (FR-005)
   ```python
   - test_order_creation
   - test_order_confirmation_page
   - test_email_service_mock
   - test_order_history_tracking
   ```

#### Priority 2: Code Optimization Implementation
**Identify and fix the 6 intentional bugs/inefficiencies:**

1. **Bug #1: Cart update quantity logic** (models.py)
   - Add validation for zero/negative quantities
   - Remove items when quantity <= 0

2. **Bug #2: Quantity input validation** (app.py)
   - Add try-catch for int() conversion
   - Handle non-numeric gracefully

3. **Bug #3: Case-sensitive discount codes** (app.py)
   - Make discount codes case-insensitive
   - `discount_code.upper() == 'SAVE10'`

4. **Inefficiency #1: Cart total calculation** (models.py)
   - Replace nested loop with multiplication
   - `total += item.book.price * item.quantity`

5. **Inefficiency #2: Order sorting** (models.py)
   - Implement lazy evaluation
   - Sort only in get_order_history()

6. **Inefficiency #3: Book lookup** (app.py)
   - Use get_book_by_title() consistently
   - Remove manual loops

**For each fix, document:**
- Before: Code + performance metrics
- After: Improved code + performance metrics
- Screenshots of timeit/cProfile results

#### Priority 3: Update test_app.py with Traceability Comments
Add clear TC-ID references:
```python
def test_add_to_cart_single_item(self, client, clean_cart):
    """
    [TC002-01] Verify adding a single book to cart
    Related Requirement: FR-002 - Shopping Cart Functionality
    """
```

### Part 2: Report (1500 words) - 30%

**Structure your report with these 5 sections:**

#### 1. Test Case Design and Coverage (300 words)
- Explain test strategy (unit, integration, performance)
- Justify testing approaches chosen
- Document challenges (e.g., mocking payment gateway)
- Reference TRACEABILITY_MATRIX.md for coverage proof

#### 2. Effectiveness of Improvements (400 words)
- Document each of the 6 bug fixes
- Include before/after performance comparisons
- Use actual timeit/cProfile results
- Screenshots showing improvements
- Explain impact on system performance

#### 3. CI/CD Automation Integration (300 words)
- Explain GitHub Actions setup
- Describe automated workflow triggers
- Benefits of continuous testing
- Challenges faced (e.g., environment setup)
- Show workflow run screenshots

#### 4. Code Quality and Maintainability (300 words)
- Discuss test code structure
- Explain conftest.py fixtures
- Test organization and naming conventions
- How tests accommodate future changes
- Industry best practices followed (AAA pattern, etc.)

#### 5. Future Considerations (200 words)
- Additional test coverage recommendations
- Further optimization opportunities
- Enhanced CI/CD pipeline features
- Security testing expansion
- Load testing considerations

---

## 📅 Timeline to Deadline (8 days)

### Days 1-2 (Today + Tomorrow): Test Implementation
- ✅ GitHub Actions setup (DONE)
- ✅ Performance tests (DONE)
- ✅ Traceability matrix (DONE)
- 🔄 Create test_checkout.py (4-5 tests)
- 🔄 Create test_payment.py (5 tests)
- 🔄 Create test_auth.py (6-7 tests)
- 🔄 Create test_order.py (3-4 tests)

### Days 3-4: Code Optimization
- 🔄 Fix Bug #1: Cart quantity validation
- 🔄 Fix Bug #2: Input validation with try-catch
- 🔄 Fix Bug #3: Case-insensitive discount codes
- 🔄 Fix Inefficiency #1: Cart total calculation
- 🔄 Fix Inefficiency #2: Order sorting
- 🔄 Fix Inefficiency #3: Book lookup consistency
- 📸 Document each fix with screenshots

### Days 5-6: Testing and Documentation
- 🔄 Run full test suite locally
- 🔄 Push to GitHub, verify Actions run
- 🔄 Collect all test execution screenshots
- 🔄 Gather performance profiling results
- 🔄 Update TRACEABILITY_MATRIX.md with final line numbers

### Days 7-8: Report Writing
- 🔄 Write 1500-word report (5 sections)
- 🔄 Insert screenshots and code snippets
- 🔄 Add Harvard references
- 🔄 Proofread and format
- 🔄 Create final submission ZIP

### Day 8: Final Submission
- 🔄 Create submission ZIP with Python files
- 🔄 Export report as PDF
- 🔄 Double-check student number on documents
- 🔄 Submit via Canvas before 23:59

---

## 📦 Submission Checklist

### Software Artefact (ZIP file)
```
online-bookstore-final/
├── .github/
│   └── workflows/
│       ├── test-and-coverage.yml ✅
│       └── performance-testing.yml ✅
├── tests/
│   ├── __init__.py ✅
│   ├── test_app.py ✅ (update with TC-IDs)
│   ├── test_performance.py ✅
│   ├── test_checkout.py 🔄 (to create)
│   ├── test_payment.py 🔄 (to create)
│   ├── test_auth.py 🔄 (to create)
│   └── test_order.py 🔄 (to create)
├── app.py 🔄 (fix bugs/inefficiencies)
├── models.py 🔄 (fix bugs/inefficiencies)
├── requirements.txt ✅
├── TRACEABILITY_MATRIX.md ✅
├── README.md ✅
└── FINAL_ASSESSMENT_PLAN.md ✅ (this file)
```

### Report (PDF file)
- [ ] 1500 words (±10%)
- [ ] 5 required sections
- [ ] Screenshots of test execution
- [ ] Before/after performance comparisons
- [ ] GitHub Actions workflow screenshots
- [ ] Harvard referencing
- [ ] Student number: 24185521
- [ ] Double-spaced, 12pt Calibri/Arial

---

## 🎯 Success Criteria (Assessment Rubric)

### Technical Implementation (50%)
**Target: 70-79% (First Class)**
- ✅ Comprehensive test coverage (aim for 80%+)
- ✅ CI/CD pipeline seamless (GitHub Actions)
- ✅ Performance optimizations with timeit/cProfile
- ✅ All high-priority tests implemented
- ✅ Code well-structured and documented

### Critical Evaluation (30%)
**Target: 70-79% (First Class)**
- ✅ Well-structured analysis
- ✅ Solid justification for improvements
- ✅ CI/CD benefits clearly explained
- ✅ Performance impacts demonstrated
- ✅ Evidence of reflective practice

### Report Quality (20%)
**Target: 70-79% (First Class)**
- ✅ Clear and well-organized
- ✅ Technical language appropriate
- ✅ Proper Harvard referencing
- ✅ Comprehensive coverage of all sections
- ✅ Professional presentation

**Overall Target: 70%+ (First Class)**

---

## 🔑 Key Differentiators from Mid-Module

### Addressed Feedback Points:
1. ✅ **Traceability Matrix** - Complete FR → Test mapping
2. ✅ **Test Case ID Mapping** - Every function mapped to TC-ID
3. ✅ **Execution Evidence** - Screenshots and metrics documented

### New Requirements Met:
4. ✅ **GitHub Actions** (not Jenkins!)
5. ✅ **Performance Profiling** (timeit + cProfile)
6. ✅ **Code Optimization** (before/after comparisons)
7. ✅ **Quality Checks** (Flake8, Bandit, Safety)

---

## 📚 References to Include

```
GitHub Actions Documentation (2024) Available at: https://docs.github.com/en/actions (Accessed: 12 October 2025).

pytest Documentation (2024) Available at: https://docs.pytest.org/ (Accessed: 12 October 2025).

Python timeit Module (2024) Python Software Foundation. Available at: https://docs.python.org/3/library/timeit.html (Accessed: 12 October 2025).

Python cProfile Module (2024) Python Software Foundation. Available at: https://docs.python.org/3/library/profile.html (Accessed: 12 October 2025).

Myers, G.J., Sandler, C. and Badgett, T. (2011) The Art of Software Testing. 3rd edn. Hoboken: John Wiley & Sons.

Beizer, B. (1990) Software Testing Techniques. 2nd edn. Boston: International Thomson Computer Press.
```

---

## 💡 Tips for Success

1. **Test Early, Test Often** - Run tests after every change
2. **Document Everything** - Take screenshots as you go
3. **Use Git Commits** - Show your progress
4. **Performance Baseline** - Measure before optimizing
5. **Clear Comments** - Explain complex test logic
6. **Peer Review** - Have someone check your work
7. **Academic Integrity** - All work must be your own

---

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd "/Users/Antony/Desktop/MSc Computer Science AI/UNIT 3 - SOFTWARE TESTING/Final Assessment/online-bookstore-final-assessment"

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v --cov=. --cov-report=html

# Run performance tests
python tests/test_performance.py

# Run with cProfile
python -m cProfile -o profile.prof -m pytest tests/ -v

# View profile results
python -c "import pstats; p = pstats.Stats('profile.prof'); p.sort_stats('cumulative'); p.print_stats(30)"

# Check coverage
coverage report -m
```

---

**Remember:** You have 8 days. Stay focused, work systematically, and you'll achieve first-class marks!

*Good luck! 🎓*
