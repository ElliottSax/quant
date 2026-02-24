# Installing Dependencies

## Issue: Externally Managed Python Environment

Your system has an externally-managed Python environment which prevents direct pip installs.

---

## ✅ Solution Options

### Option 1: Use Existing Virtual Environment (Recommended)

If you have a working virtual environment set up:

```bash
# Activate your venv
source /path/to/your/venv/bin/activate

# Install pandas-ta
pip install pandas-ta

# Install optional providers
pip install alpha-vantage twelvedata finnhub-python
```

### Option 2: Create New Virtual Environment

```bash
# Navigate to backend directory
cd /mnt/e/projects/quant/quant/backend

# Create new venv
python3 -m venv venv_quant

# Activate it
source venv_quant/bin/activate

# Install all dependencies
pip install -r requirements.txt

# This will install pandas-ta and everything else
```

### Option 3: System-Wide Install (Not Recommended)

```bash
# Override the protection (use with caution)
pip install pandas-ta --break-system-packages

# Or install optional packages
pip install alpha-vantage twelvedata finnhub-python --break-system-packages
```

### Option 4: Use pipx (For Applications)

```bash
# Install pipx if needed
sudo apt install pipx

# Note: pipx is for applications, not libraries
# So this won't work for pandas-ta which is a library
```

---

## 🎯 Recommended Approach

**For Development:**

```bash
cd /mnt/e/projects/quant/quant/backend

# Create fresh venv
python3 -m venv venv_quant

# Activate
source venv_quant/bin/activate

# Install everything
pip install -r requirements.txt

# Verify
python3 verify_deployment.py
```

**For Quick Testing:**

```bash
# Just install what's needed (system-wide)
pip install pandas-ta --break-system-packages

# Run verification
python3 verify_deployment.py
```

---

## 📋 What Gets Installed

From `requirements.txt`, pandas-ta is now listed:

```
pandas-ta>=0.3.14b0          # Technical analysis (REQUIRED)
alpha-vantage>=2.3.1         # Optional market data
twelvedata>=1.2.13           # Optional market data
finnhub-python>=2.4.20       # Optional market data
```

---

## ✅ After Installation

Run verification to confirm:

```bash
cd /mnt/e/projects/quant/quant/backend
python3 verify_deployment.py
```

Expected result: **16/16 checks passing** ✅

---

## 🚀 Quick Start After Install

```bash
# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Test (new terminal)
cd /mnt/e/projects/quant
python examples/authenticated_prediction_demo.py
```

---

## 💡 Why Virtual Environments?

- **Isolation**: Dependencies don't conflict with system packages
- **Reproducibility**: Same environment across machines
- **Safety**: Won't break system Python
- **Best Practice**: Industry standard for Python development

---

**Choose your preferred option above and the system will be ready to deploy!**
