# Python random Module Reference

**Official Source**: https://docs.python.org/3/library/random.html
**Module**: `random` (Python Standard Library)
**Purpose**: Pseudo-random number generation for various distributions
**Last Updated**: 2025-10-25
**Python Version**: 3.8+

---

## Overview

The `random` module generates pseudo-random numbers using the **Mersenne Twister algorithm**. It's suitable for simulations, modeling, and general random number generation, but **NOT for cryptographic purposes** (use `secrets` module instead).

---

## Why We Use This Instead of numpy.random

**In Snowflake Streamlit Environment**:
- ✅ `random` module: **WORKS** (Python standard library, fully supported)
- ❌ `np.random.*`: **DOESN'T WORK** (limited numpy support in Snowflake)

**This is our solution for random number generation in Snowflake Streamlit apps.**

---

## Core Functions

### Basic Random Generation

```python
import random

# Random float in [0.0, 1.0)
x = random.random()

# Random integer (inclusive on both ends)
n = random.randint(1, 10)  # Returns 1 ≤ n ≤ 10

# Random float between a and b
x = random.uniform(0.0, 10.0)

# Random element from sequence
item = random.choice(['apple', 'banana', 'orange'])
```

---

## Distribution Functions

### 1. Normal/Gaussian Distribution

```python
random.gauss(mu, sigma)
```

**Parameters**:
- `mu`: Mean (center of distribution)
- `sigma`: Standard deviation (spread)

**Returns**: Float from normal distribution

**Example**:
```python
# Standard normal distribution (mean=0, std=1)
values = [random.gauss(0, 1) for _ in range(100)]

# Custom normal distribution (mean=100, std=15)
test_scores = [random.gauss(100, 15) for _ in range(1000)]
```

**Use Case**: Replace `np.random.randn()` or `np.random.standard_normal()`

---

### 2. Exponential Distribution

```python
random.expovariate(lambd)
```

**Parameters**:
- `lambd`: Rate parameter (1/mean), must be > 0

**Returns**: Float from exponential distribution

**Example**:
```python
# Exponential with lambda=1.5
values = [random.expovariate(1.5) for _ in range(100)]

# Poisson approximation (for counts)
# Poisson with rate=5
poisson_approx = [int(random.expovariate(1/5)) for _ in range(100)]
```

**Use Case**: Replace `np.random.poisson()` (approximation)

**Note**: Exponential is related to Poisson. For event counts, use `int(random.expovariate(1/lambda))`.

---

### 3. Uniform Distribution

```python
random.uniform(a, b)
```

**Parameters**:
- `a`: Lower bound
- `b`: Upper bound

**Returns**: Float where a ≤ x ≤ b

**Example**:
```python
# Uniform between 0 and 10
values = [random.uniform(0, 10) for _ in range(100)]

# Random percentage
percentage = random.uniform(0, 100)
```

**Use Case**: Replace `np.random.uniform()`

---

### 4. Random Integers

```python
random.randint(a, b)  # Inclusive on both ends
```

**Parameters**:
- `a`: Lower bound (inclusive)
- `b`: Upper bound (inclusive)

**Returns**: Integer where a ≤ n ≤ b

**Example**:
```python
# Dice roll (1-6)
dice = random.randint(1, 6)

# Random integers for array
values = [random.randint(0, 99) for _ in range(50)]
```

**Important Difference from numpy**:
```python
# numpy.randint: high is EXCLUSIVE
np.random.randint(0, 10)  # Returns 0-9

# Python random.randint: high is INCLUSIVE
random.randint(0, 10)  # Returns 0-10

# To match numpy behavior:
random.randint(0, 9)  # Returns 0-9 (equivalent to np.random.randint(0, 10))
```

**Use Case**: Replace `np.random.randint()` (adjust upper bound by -1)

---

## Other Useful Distributions

### Triangular Distribution
```python
random.triangular(low, high, mode)
```
- `low`: Minimum value
- `high`: Maximum value
- `mode`: Peak value

### Beta Distribution
```python
random.betavariate(alpha, beta)
```
- Returns value between 0 and 1
- Useful for probabilities

### Gamma Distribution
```python
random.gammavariate(alpha, beta)
```

### Log-Normal Distribution
```python
random.lognormvariate(mu, sigma)
```

---

## Sequence Operations

### Choose Random Element
```python
# Single random element
item = random.choice([1, 2, 3, 4, 5])

# Multiple elements WITH replacement
items = random.choices([1, 2, 3, 4, 5], k=10)

# Multiple elements WITHOUT replacement
items = random.sample([1, 2, 3, 4, 5], k=3)
```

### Shuffle List
```python
my_list = [1, 2, 3, 4, 5]
random.shuffle(my_list)  # Modifies list in-place
print(my_list)  # [3, 1, 5, 2, 4] (example)
```

---

## State Management

### Seed for Reproducibility
```python
# Set seed for reproducible results
random.seed(42)

values1 = [random.gauss(0, 1) for _ in range(10)]

# Reset seed
random.seed(42)

values2 = [random.gauss(0, 1) for _ in range(10)]

# values1 == values2 (same sequence)
```

### Save/Restore State
```python
# Save current state
state = random.getstate()

# Generate some numbers
x = random.random()

# Restore previous state
random.setstate(state)

# Will generate same x again
x2 = random.random()  # x == x2
```

---

## Snowflake Streamlit Compatibility

### ✅ Complete Replacement Guide

| numpy.random | Python random | Example |
|--------------|---------------|---------|
| `np.random.randn(N)` | `[random.gauss(0, 1) for _ in range(N)]` | Normal distribution |
| `np.random.standard_normal(N)` | `[random.gauss(0, 1) for _ in range(N)]` | Standard normal |
| `np.random.poisson(lam, N)` | `[int(random.expovariate(1/lam)) for _ in range(N)]` | Poisson (approx) |
| `np.random.uniform(a, b, N)` | `[random.uniform(a, b) for _ in range(N)]` | Uniform |
| `np.random.randint(a, b, N)` | `[random.randint(a, b-1) for _ in range(N)]` | Random integers |

### Example: Full Conversion

**Before (doesn't work in Snowflake)**:
```python
import numpy as np

# Normal distribution
data1 = np.random.randn(100)

# Poisson distribution
data2 = np.random.poisson(5, 50)

# Uniform distribution
data3 = np.random.uniform(0, 10, 30)
```

**After (works in Snowflake)**:
```python
import random

# Normal distribution
data1 = [random.gauss(0, 1) for _ in range(100)]

# Poisson distribution (approximation)
data2 = [int(random.expovariate(1/5)) if 5 > 0 else 0 for _ in range(50)]

# Uniform distribution
data3 = [random.uniform(0, 10) for _ in range(30)]
```

---

## Performance Considerations

### Thread Safety
- The `random` module is thread-safe for most operations
- For multi-threaded applications, create separate `Random()` instances per thread:

```python
import random

# Create separate instance for thread
thread_random = random.Random()
thread_random.seed(thread_id)
value = thread_random.gauss(0, 1)
```

### Performance Tips
- List comprehensions are efficient for generating multiple values
- For very large datasets (millions), consider using numpy locally (not in Snowflake)
- `random.random()` is the fastest function

---

## Security Warning

⚠️ **DO NOT use `random` for cryptographic purposes!**

For security-sensitive applications, use the `secrets` module:

```python
import secrets

# Cryptographically secure random
token = secrets.token_hex(16)
secure_number = secrets.randbelow(100)
```

---

## Common Use Cases

### 1. Generate Test Data
```python
# Random user ages
ages = [random.randint(18, 80) for _ in range(1000)]

# Random prices
prices = [round(random.uniform(10.0, 100.0), 2) for _ in range(500)]

# Random dates (as day offsets)
day_offsets = [random.randint(0, 365) for _ in range(100)]
```

### 2. Simulations
```python
# Monte Carlo simulation
def simulate_coin_flips(n_flips, n_simulations):
    results = []
    for _ in range(n_simulations):
        heads = sum(random.choice([0, 1]) for _ in range(n_flips))
        results.append(heads)
    return results

outcomes = simulate_coin_flips(100, 10000)
average_heads = sum(outcomes) / len(outcomes)
```

### 3. Sampling
```python
# Random sample from population
population = list(range(1000))
sample = random.sample(population, k=100)

# Weighted random selection
choices = ['A', 'B', 'C']
weights = [0.5, 0.3, 0.2]
selected = random.choices(choices, weights=weights, k=1000)
```

---

## Best Practices

1. **Seed for Reproducibility**: Always set seed when reproducibility is needed
2. **Use List Comprehensions**: Efficient for generating multiple values
3. **Choose Right Distribution**: Match distribution to your data requirements
4. **Separate Instances for Threads**: Avoid contention in multi-threaded code
5. **Don't Use for Security**: Use `secrets` module for cryptographic needs

---

## Additional Resources

**Official Documentation**: https://docs.python.org/3/library/random.html

**Related Modules**:
- `secrets` - Cryptographically secure random numbers
- `numpy.random` - Advanced random generation (not available in Snowflake Streamlit)
- `statistics` - Statistical functions

---

## Version History

| Date | Version | Notes |
|------|---------|-------|
| 2025-10-25 | 1.0 | Initial documentation for Snowflake Streamlit compatibility |

---

**Maintainer**: Fuad Onate (fuad.onate@CompanyX.com)
**Last Review**: 2025-10-25
**Next Review**: When Python version updates
