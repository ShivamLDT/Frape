# Setting Up Beam on EC2

## Quick Setup Guide

### Step 1: Push Beam to GitHub

On your local machine:

```bash
cd C:\Users\LDT\frappe\beam

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial beam CLI"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/beam.git
git push -u origin main
```

**Important**: Only push the `beam/` folder, NOT the `bench/` folder!

### Step 2: Clone on EC2

```bash
# SSH into your EC2 instance
ssh ubuntu@your-ec2-ip

# Clone the repository
git clone https://github.com/yourusername/beam.git
cd beam
```

### Step 3: Install Beam

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install beam (this will also install frappe-bench)
pip install -e .

# Verify installation
beam --version
```

### Step 4: Create a Test Bench (Isolated)

```bash
# Create a test bench in a separate location
beam init ~/test-bench

cd ~/test-bench

# Create a test site
beam new-site test.localhost

# Test it works
beam start
# (Press Ctrl+C to stop)
```

## Keeping Your Production Safe

### Option 1: Use Separate User (Recommended)

```bash
# Create a test user
sudo adduser beamtest

# Switch to test user
sudo su - beamtest

# Install beam as this user
cd ~
git clone https://github.com/yourusername/beam.git
cd beam
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Create test bench
beam init ~/test-bench
```

This completely isolates your test setup from production.

### Option 2: Use Different Directory

If you want to use the same user:

```bash
# Install beam in your home directory
cd ~
git clone https://github.com/yourusername/beam.git
cd beam
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Create test bench in a clearly named directory
beam init ~/beam-test-bench

# Your production benches (if any) are elsewhere, untouched
```

## What Gets Installed

When you run `pip install -e .`:
- ✅ `beam` CLI tool (your wrapper)
- ✅ `frappe-bench` (as dependency, in the venv only)
- ❌ Nothing touches your existing production benches

## Testing

```bash
# Test basic commands
beam --version
beam --help

# Test bench creation
beam init test-bench
cd test-bench
beam new-site test.localhost

# Test app installation
beam get-app erpnext https://github.com/frappe/erpnext
beam --site test.localhost install-app erpnext
```

## Cleanup (If Needed)

If you want to remove the test setup:

```bash
# Remove the test bench
rm -rf ~/test-bench

# Remove beam installation
rm -rf ~/beam

# If you used a separate user:
sudo userdel -r beamtest
```

## Notes

- ✅ Beam installs `frappe-bench` in the virtual environment only
- ✅ Your production benches remain completely untouched
- ✅ You can have multiple benches on the same server
- ✅ Each bench is independent

---

**You're ready to test beam on EC2!**

