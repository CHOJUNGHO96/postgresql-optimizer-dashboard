#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모델별 타임아웃 설정 검증 스크립트.

이 스크립트는 backend 디렉토리에서 실행해야 합니다:
cd backend && python ../verify_timeout_config.py
"""

import sys
import io
from pathlib import Path

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.core.model_configs import get_model_limits, MODEL_TOKEN_LIMITS
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    print(f"Make sure to run this script from the project root directory")
    sys.exit(1)


def main():
    """타임아웃 설정을 검증하고 출력한다."""
    print("=" * 80)
    print("Model Timeout Configuration Verification")
    print("=" * 80)
    print()

    # Test individual models
    test_cases = [
        ("gemini-2.5-flash", 150, "Gemini 2.5 Flash (Large Context)"),
        ("gemini-exp-1206", 180, "Gemini Exp 1206 (Largest Context)"),
        ("claude-3-5-sonnet-20241022", 75, "Claude Sonnet (Medium, Fast)"),
        ("claude-3-5-haiku-20241022", 60, "Claude Haiku (Standard)"),
        ("claude-haiku-4.5", 50, "Claude Haiku 4.5 (Fastest)"),
        ("glm-4.5-flash", 120, "GLM 4.5 Flash (Normal Speed)"),
        ("unknown-model", 90, "Unknown Model (Default)"),
    ]

    all_passed = True

    for model_name, expected_timeout, description in test_cases:
        limits = get_model_limits(model_name)
        actual_timeout = limits.timeout_seconds
        status = "[PASS]" if actual_timeout == expected_timeout else "[FAIL]"

        print(f"{status} {description}")
        print(f"   Model: {model_name}")
        print(f"   Expected: {expected_timeout}s | Actual: {actual_timeout}s")

        if actual_timeout != expected_timeout:
            all_passed = False
            print(f"   [WARN] Timeout does not match expected value!")

        print()

    # Verify all timeouts are reasonable
    print("=" * 80)
    print("Timeout Range Verification (30-300s)")
    print("=" * 80)
    print()

    for model_name, limits in MODEL_TOKEN_LIMITS.items():
        timeout = limits.timeout_seconds
        if 30 <= timeout <= 300:
            print(f"[PASS] {model_name}: {timeout}s (within range)")
        else:
            print(f"[FAIL] {model_name}: {timeout}s (out of range!)")
            all_passed = False

    # Check default
    default_timeout = get_model_limits("unknown-model").timeout_seconds
    if 30 <= default_timeout <= 300:
        print(f"[PASS] DEFAULT: {default_timeout}s (within range)")
    else:
        print(f"[FAIL] DEFAULT: {default_timeout}s (out of range!)")
        all_passed = False

    print()
    print("=" * 80)
    if all_passed:
        print("[SUCCESS] All verifications passed!")
    else:
        print("[FAILURE] Some verifications failed!")
        sys.exit(1)
    print("=" * 80)


if __name__ == "__main__":
    main()
