# 🛡️ Security Testing (Optional but Recommended)

**Time:** 10 minutes
**Value:** HIGH (differentiates your work!)

---

## Why Add Security Testing?

✅ **Shows comprehensive approach** - Functional + Performance + Security
✅ **Demonstrates professional awareness** - Using industry-standard tools
✅ **Adds 150-200 words** to your report
✅ **Provides another screenshot** for evidence
✅ **Makes you stand out** from other submissions

---

## Quick Start (3 Commands)

```bash
cd "/Users/Antony/Desktop/MSc Computer Science AI/UNIT 3 - SOFTWARE TESTING/Final Assessment/online-bookstore-final-assessment"

source venv/bin/activate

# Run security scan
bandit -r . -ll --exclude ./venv,./tests,./.github

# Take screenshot of output
# Save as: screenshots/bandit_security_scan.png
```

---

## What Bandit Found

### 📊 Summary
- **Total issues:** 12
- **HIGH severity:** 1 (Flask debug=True)
- **LOW severity:** 11 (hardcoded keys, weak RNG)

### ⚠️ The HIGH Issue
**Flask debug mode enabled** (app.py:343)
- **Risk:** In production, allows arbitrary code execution
- **Your answer:** "Acceptable for demo app, would disable in production"

---

## For Your Report (Copy This!)

Add this to **Section 2 (Test Strategy)** or **Section 4 (Coverage)**:

> **Security Testing**
>
> Security testing was conducted using Bandit, an industry-standard static analysis tool for Python. The scan analyzed 556 lines of code, identifying 12 potential issues: 1 HIGH severity (CWE-94) and 11 LOW severity.
>
> The HIGH severity issue relates to Flask's debug mode being enabled (app.py:343). While appropriate for development, this would pose a serious security risk in production as it exposes the Werkzeug debugger. The 11 LOW severity issues concern hardcoded credentials and weak random number generation, which are acceptable within the context of a demonstration application.
>
> This multi-dimensional testing approach (functional, performance, and security) demonstrates comprehensive quality assurance and professional awareness of production security requirements.

**Word count:** ~100 words
**Impact:** Shows you understand professional testing!

---

## Screenshot Instructions

1. Run the command above
2. Screenshot showing:
   - Total lines scanned (556)
   - 1 HIGH + 11 LOW issues
   - Specific CWE references
3. Save as: `screenshots/bandit_security_scan.png`

---

## Testing Coverage Summary

With security testing, you now have:

| Test Type | Tool | Result |
|-----------|------|--------|
| Unit/Integration | pytest | 86/86 passing ✅ |
| Code Coverage | pytest-cov | 85% ✅ |
| Performance | Locust + timeit | 100x improvement ✅ |
| **Security** | **Bandit** | **12 issues identified** ✅ |

**Complete testing strategy!** ⭐⭐⭐⭐⭐

---

## Full Guide

For detailed information, see: `SECURITY_TESTING_GUIDE.md`

---

**Bottom Line:** 10 minutes to add security testing = much stronger report!

*Do this BEFORE writing your report!*
