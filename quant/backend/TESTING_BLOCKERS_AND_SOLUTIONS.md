# Testing Blockers and Solutions

**Status**: Active Investigation
**Last Updated**: February 2, 2026

---

## 🚧 Current Blockers

### 1. MLflow Import Hanging

**Symptom**: Tests hang indefinitely during collection phase

**Root Cause**:
```python
signal_generator.py
→ from app.ml.ensemble import EnsemblePredictor
→ from app.ml.cyclical import FourierCyclicalDetector, RegimeDetector, DynamicTimeWarpingMatcher
→ from app.ml.cyclical.experiment_tracker import CyclicalExperimentTracker
→ import mlflow  # HANGS HERE
```

**Why It Hangs**:
- MLflow tries to connect to tracking server at import time
- No tracking server running in test environment
- Import blocks indefinitely waiting for connection

**Affected Tests**:
- `tests/test_services/test_signal_generator.py` (100 tests)

---

### 2. Redis Async Import Hanging

**Symptom**: Tests hang during pytest collection

**Root Cause**:
```python
websocket_events.py
→ from app.core.cache import cache_manager
→ import redis.asyncio as redis  # HANGS HERE
```

**Why It Hangs**:
- Redis async client appears to do network/DNS operations at import time
- No Redis server running in test environment
- Import blocks waiting for resolution

**Affected Tests**:
- `tests/test_services/test_websocket_events.py` (63 tests)

---

## ✅ Attempted Solutions

### Solution 1: Lazy Imports with TYPE_CHECKING

**File**: `app/services/signal_generator.py`

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ml.ensemble import EnsemblePredictor
else:
    try:
        from app.ml.ensemble import EnsemblePredictor
    except ImportError:
        EnsemblePredictor = None
```

**Result**: ❌ Still hangs during pytest collection

**Why**: Pytest still imports the module to collect tests, triggering the import chain

---

### Solution 2: Module Mocking in Tests

**File**: `tests/test_services/test_signal_generator.py`

```python
import sys
from unittest.mock import MagicMock

sys.modules['mlflow'] = MagicMock()
sys.modules['app.ml.ensemble'] = MagicMock()
# ... more mocks

from app.services.signal_generator import SignalGenerator
```

**Result**: ❌ Still hangs

**Why**: Mocking happens AFTER Python has already started importing the real modules

---

### Solution 3: Conftest-Level Mocking

**File**: `tests/conftest.py`

```python
import sys
from unittest.mock import MagicMock

# Mock BEFORE app imports
sys.modules['mlflow'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()

from app.main import app  # Now import app modules
```

**Result**: ❌ Broke existing tests, reverted

**Why**: Mocking core modules breaks other parts of the application

---

### Solution 4: Try/Except in Source Files

**File**: `app/services/websocket_events.py`

```python
try:
    from app.core.cache import cache_manager
except ImportError:
    cache_manager = None
```

**Result**: ❌ Still hangs

**Why**: The import itself hangs before the exception can be caught

---

## 💡 Recommended Solutions

### Immediate: Environment-Based Lazy Loading

**Strategy**: Make imports truly lazy - only import when actually used

**Implementation**:

**File**: `app/services/signal_generator.py`
```python
class SignalGenerator:
    def __init__(self, ensemble_predictor=None):
        self.ensemble = ensemble_predictor
        self._ml_module = None

    def _get_ml_module(self):
        """Lazy load ML module only when needed"""
        if self._ml_module is None and os.getenv('ENVIRONMENT') != 'test':
            from app.ml.ensemble import EnsemblePredictor
            self._ml_module = EnsemblePredictor
        return self._ml_module
```

**Pros**:
- ✅ Imports only happen when actually needed
- ✅ Tests can run without ML dependencies
- ✅ Minimal code changes

**Cons**:
- ⚠️ Slightly more complex code
- ⚠️ Need to update all heavy import sites

---

### Medium-Term: Dependency Injection

**Strategy**: Pass dependencies explicitly instead of importing globally

**Implementation**:

**File**: `app/services/signal_generator.py`
```python
class SignalGenerator:
    def __init__(
        self,
        ensemble_predictor=None,
        cache_service=None
    ):
        self.ensemble = ensemble_predictor or get_default_ensemble()
        self.cache = cache_service or get_default_cache()
```

**Test File**:
```python
def test_signal_generation():
    mock_ensemble = Mock()
    generator = SignalGenerator(ensemble_predictor=mock_ensemble)
    # Test without any imports
```

**Pros**:
- ✅ Best practice architecture
- ✅ Highly testable
- ✅ Clear dependencies
- ✅ No import issues

**Cons**:
- ⚠️ Requires refactoring services
- ⚠️ Need to update all call sites
- ⚠️ More initial work

---

### Long-Term: Service Layer Abstraction

**Strategy**: Create abstract interfaces for heavy dependencies

**Implementation**:

**File**: `app/services/interfaces.py`
```python
from abc import ABC, abstractmethod

class MLServiceInterface(ABC):
    @abstractmethod
    async def predict(self, data): pass

class CacheServiceInterface(ABC):
    @abstractmethod
    async def get(self, key): pass
```

**File**: `app/services/signal_generator.py`
```python
class SignalGenerator:
    def __init__(
        self,
        ml_service: MLServiceInterface,
        cache_service: CacheServiceInterface
    ):
        self.ml = ml_service
        self.cache = cache_service
```

**Test File**:
```python
class MockMLService(MLServiceInterface):
    async def predict(self, data):
        return {"prediction": 0.5}

def test_signal_generation():
    generator = SignalGenerator(
        ml_service=MockMLService(),
        cache_service=MockCacheService()
    )
```

**Pros**:
- ✅ Clean architecture
- ✅ Easy to test
- ✅ Easy to swap implementations
- ✅ Type-safe interfaces

**Cons**:
- ⚠️ Significant refactoring
- ⚠️ More boilerplate code
- ⚠️ Learning curve for team

---

## 🔧 Quick Fix for Current Session

### Option A: Test Without Running (Static Analysis)

1. **Code Coverage via AST Analysis**:
   ```bash
   # Count functions defined
   grep -r "def " app/services/signal_generator.py | wc -l

   # Count test functions
   grep -r "def test_" tests/test_services/test_signal_generator.py | wc -l
   ```

2. **Manual Code Review**:
   - Review test file to verify comprehensive coverage
   - Check that all public methods have corresponding tests
   - Verify edge cases are covered

3. **Document Test Quality**:
   - Tests are well-written and comprehensive
   - Ready to run once import issues resolved
   - Count toward total test suite size

**Pros**:
- ✅ Can proceed with other services
- ✅ Tests are ready for when blocking issues fixed
- ✅ Still valuable documentation

**Cons**:
- ⚠️ Can't verify tests actually pass
- ⚠️ No actual coverage measurement

---

### Option B: Isolate Tests in Separate Files

1. **Create Lightweight Test Modules**:
   - Test pure functions without imports
   - Test data classes and enums
   - Test logic that doesn't require heavy dependencies

2. **File**: `tests/test_services/test_signal_generator_pure.py`
   ```python
   # Test pure logic without heavy imports
   def test_parse_amount():
       from app.services.websocket_events import ActivityMonitor
       monitor = ActivityMonitor()
       assert monitor._parse_amount("$1,000,000") == 1000000.0
   ```

**Pros**:
- ✅ Can test some functionality immediately
- ✅ No import issues
- ✅ Incremental progress

**Cons**:
- ⚠️ Only partial coverage
- ⚠️ Doesn't test integration points

---

### Option C: Skip Problematic Tests, Continue Others

1. **Mark tests to skip**:
   ```python
   @pytest.mark.skip(reason="MLflow import issues - blocked on #123")
   class TestSignalGenerator:
       ...
   ```

2. **Continue with other services**:
   - Test backtesting service
   - Test portfolio optimization
   - Test market data service
   - Come back to blocked tests later

**Pros**:
- ✅ Make progress on other services
- ✅ Increase overall coverage
- ✅ Document blocked tests for later

**Cons**:
- ⚠️ Critical services remain untested
- ⚠️ Delayed gratification

---

## 📋 Action Items

### For Development Team

1. **Immediate**:
   - [ ] Decide on quick fix strategy (A, B, or C above)
   - [ ] Document decision and rationale
   - [ ] Continue with unblocked services

2. **This Week**:
   - [ ] Implement lazy loading for ML imports
   - [ ] Add environment checks before heavy imports
   - [ ] Verify tests run successfully

3. **This Sprint**:
   - [ ] Refactor signal_generator for dependency injection
   - [ ] Create cache service interface
   - [ ] Update tests to use mocked dependencies

4. **Next Sprint**:
   - [ ] Full service layer refactoring
   - [ ] Abstract interfaces for all heavy dependencies
   - [ ] Comprehensive integration testing strategy

---

## 📚 Related Resources

- MLflow Testing Guide: https://www.mlflow.org/docs/latest/python_api/mlflow.html#mlflow.set_tracking_uri
- Redis Async Testing: https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
- Pytest Import Mocking: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- Dependency Injection in Python: https://python-dependency-injector.ets.org/

---

## 🎯 Success Criteria

Tests considered "unblocked" when:
- ✅ Pytest can collect all tests without hanging
- ✅ All tests pass or fail (not timeout)
- ✅ Coverage can be measured
- ✅ Tests run in < 30 seconds total
- ✅ No external service dependencies (Redis, MLflow servers)

---

**Next Review**: After implementing lazy loading solution
**Owner**: Development Team
**Priority**: High (blocking 163 tests)

---

*This document will be updated as solutions are implemented and tested.*
