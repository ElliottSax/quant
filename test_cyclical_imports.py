#!/usr/bin/env python3
"""
Quick validation script to test cyclical model imports and basic functionality.
Run this to verify the cyclical models are working before running full pytest suite.
"""

import sys
import numpy as np
import pandas as pd

sys.path.insert(0, 'quant/backend')

def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")

    try:
        from app.ml.cyclical.fourier import FourierCyclicalDetector
        print("✓ Fourier module imported")
    except Exception as e:
        print(f"✗ Fourier import failed: {e}")
        return False

    try:
        from app.ml.cyclical.hmm import RegimeDetector
        print("✓ HMM module imported")
    except Exception as e:
        print(f"✗ HMM import failed: {e}")
        return False

    try:
        from app.ml.cyclical.dtw import DynamicTimeWarpingMatcher
        print("✓ DTW module imported")
    except Exception as e:
        print(f"✗ DTW import failed: {e}")
        return False

    return True

def test_fourier_basic():
    """Test basic Fourier functionality"""
    print("\nTesting Fourier detector...")

    from app.ml.cyclical.fourier import FourierCyclicalDetector

    # Create synthetic data with known cycle
    np.random.seed(42)
    t = np.arange(200)
    signal = np.sin(2 * np.pi * t / 7) + 0.1 * np.random.randn(200)

    detector = FourierCyclicalDetector()
    result = detector.detect_cycles(signal)

    assert 'dominant_cycles' in result
    assert len(result['dominant_cycles']) > 0
    print(f"✓ Detected {len(result['dominant_cycles'])} cycles")

    return True

def test_hmm_basic():
    """Test basic HMM functionality"""
    print("\nTesting HMM detector...")

    from app.ml.cyclical.hmm import RegimeDetector

    # Create synthetic regime data
    np.random.seed(42)
    returns = np.concatenate([
        np.random.normal(0.02, 0.01, 50),  # Bull
        np.random.normal(-0.01, 0.03, 50),  # Bear
    ])

    detector = RegimeDetector(n_states=2)
    result = detector.fit_and_predict(returns)

    assert 'current_regime' in result
    assert 'regime_characteristics' in result
    print(f"✓ Current regime: {result['current_regime_name']}")

    return True

def test_dtw_basic():
    """Test basic DTW functionality"""
    print("\nTesting DTW matcher...")

    from app.ml.cyclical.dtw import DynamicTimeWarpingMatcher

    # Create pattern data
    np.random.seed(42)
    pattern = np.array([0, 1, 2, 1, 0, -1, -2, -1, 0, 1])
    historical = np.tile(pattern, 10) + np.random.normal(0, 0.1, 100)

    matcher = DynamicTimeWarpingMatcher(similarity_threshold=0.5)
    matches = matcher.find_similar_patterns(pattern, historical, window_size=10, top_k=3)

    assert len(matches) > 0
    print(f"✓ Found {len(matches)} pattern matches")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Cyclical Models Validation Test")
    print("=" * 60)

    all_passed = True

    if not test_imports():
        print("\n✗ Import tests failed")
        sys.exit(1)

    try:
        if not test_fourier_basic():
            all_passed = False
    except Exception as e:
        print(f"✗ Fourier test failed: {e}")
        all_passed = False

    try:
        if not test_hmm_basic():
            all_passed = False
    except Exception as e:
        print(f"✗ HMM test failed: {e}")
        all_passed = False

    try:
        if not test_dtw_basic():
            all_passed = False
    except Exception as e:
        print(f"✗ DTW test failed: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validation tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        sys.exit(1)
