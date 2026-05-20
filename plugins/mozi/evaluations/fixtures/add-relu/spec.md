# AddRelu SPEC

## 1. Overview / 概述
AddRelu computes the elementwise ReLU of the broadcasted sum of `x` and `bias`, based on the sibling AddRelu PRD.

## 2. Scope / 范围
The SPEC covers floating tensor inputs, scalar or tensor bias, NumPy-style broadcasting, output dtype and shape inference, unsupported dtype handling, and reference compatibility. It excludes implementation strategy.

## 3. Supported Platforms / 支持的NPU平台
Mozi NPU v1 is the target platform scope.

## 4. Operator Interface / 算子接口
### PyTorch ATen IR

```text
aten::add_relu(Tensor x, Tensor bias) -> Tensor
```

### Pure Python Signature

```python
def add_relu(x, bias):
    """Compute the elementwise ReLU of x + bias.

    Args:
        x: Floating input tensor. It supplies the primary tensor values, shape, dtype, layout, and non-mutated input memory.
        bias: Floating tensor or scalar bias broadcastable with x. It is read-only and may have a shape compatible with NumPy broadcasting.

    Returns:
        Output tensor metadata and values equivalent to max(x + bias, 0), with broadcast shape and supported floating dtype behavior.
    """
```

### Pure C++ Signature

```cpp
/**
 * @brief Compute the elementwise ReLU of the broadcasted sum of x and bias.
 *
 * Constraints: x and bias must be floating values with broadcast-compatible shapes.
 * Numeric semantics: results match ReLU of the sum for supported floating dtypes.
 * Memory semantics: inputs are read-only and the result is a new tensor.
 * @param x Floating input tensor providing primary values, shape, dtype, layout, and read-only memory.
 * @param bias Floating tensor or scalar bias broadcastable with x and read-only.
 * @return Tensor containing the ReLU of the broadcasted sum with broadcast shape.
 */
Tensor add_relu(Tensor x, Tensor bias);
```

## 5. Input Specification / 输入规格
`x` is a `float16` or `float32` tensor. `bias` is a `float16` or `float32` tensor or scalar broadcastable with `x`.

## 6. Output Specification / 输出规格
The output is a tensor with the broadcast shape of `x` and `bias`, containing `max(x + bias, 0)` elementwise. The output dtype is `float16` when both inputs are `float16`; mixed `float16` and `float32` inputs promote to `float32`; two `float32` inputs produce `float32`.

## 7. Attribute Specification / 属性规格
AddRelu has no attributes.

## 8. Mathematical Semantics / 数学语义
Let \(X \in D^{S_x}\) and \(B \in D^{S_b}\), where \(D \subset \mathbb{R}\) is the supported floating domain and \(S = broadcast(S_x, S_b)\). For every index \(i \in S\), the output \(Y \in D^S\) is defined as \(Y_i = \max(X_{broadcast(i)} + B_{broadcast(i)}, 0)\).

## 9. Functional Semantics / 功能语义
The observable behavior is equivalent to applying addition after broadcasting and then applying ReLU elementwise.

### NumPy Reference Function

```python
import numpy as np

def add_relu(x, bias):
    """Compute the AddRelu behavioral reference.

    Args:
        x: Floating NumPy-compatible tensor supplying the primary values.
        bias: Floating NumPy-compatible tensor or scalar broadcastable with x.

    Returns:
        NumPy array containing max(x + bias, 0) with the promoted supported dtype.

    Raises:
        TypeError: If x or bias has an unsupported non-floating dtype.
        ValueError: If x and bias are not broadcast-compatible.

    Notes:
        This executable reference defines functional behavior only and does not imply an implementation strategy.
    """
    x_array = np.asarray(x)
    bias_array = np.asarray(bias)
    supported = {np.dtype("float16"), np.dtype("float32")}
    if x_array.dtype not in supported or bias_array.dtype not in supported:
        raise TypeError("AddRelu supports float16 and float32 inputs only")
    result_dtype = np.result_type(x_array.dtype, bias_array.dtype)
    if result_dtype not in supported:
        result_dtype = np.dtype("float32")
    summed = np.add(x_array.astype(result_dtype), bias_array.astype(result_dtype))
    return np.maximum(summed, np.array(0, dtype=result_dtype)).astype(result_dtype)
```

### Pure C++17 Reference Function

```cpp
/**
 * @brief Compute the AddRelu behavioral reference.
 *
 * @param x Floating tensor providing primary values.
 * @param bias Floating tensor or scalar broadcastable with x.
 * @return Tensor containing max(x + bias, 0) with the promoted supported dtype.
 */
Tensor add_relu(Tensor x, Tensor bias) {
    Tensor broadcasted_x = broadcast_to_result_shape(x, bias);
    Tensor broadcasted_bias = broadcast_to_result_shape(bias, x);
    Tensor summed = elementwise_add_with_supported_float_promotion(broadcasted_x, broadcasted_bias);
    return elementwise_max(summed, 0.0);
}
```

## 10. Numeric Semantics / 数值语义
For finite supported floating inputs, each output element equals the reference expression within the validation tolerance for the dtype. Addition and ReLU use the promoted supported floating dtype. NaN, Inf, and signed-zero behavior follows the reference framework expression `torch.relu(torch.add(x, bias))` when such values are supplied.

## 11. Shape Semantics / Shape 语义
The output shape is the NumPy broadcast shape of `x` and `bias`.

```python
import numpy as np

def add_relu(x, bias):
    """Infer the output shape for AddRelu.

    Args:
        x: Input tensor-like object with a shape attribute or NumPy-compatible shape.
        bias: Bias tensor-like object or scalar broadcastable with x.

    Returns:
        Tuple representing the broadcast output shape.

    Raises:
        ValueError: If x and bias shapes are not broadcast-compatible.

    Notes:
        The rule returns shape metadata only and does not compute tensor values.
    """
    shape_rules = [
        ("broadcast", lambda a, b: np.broadcast_shapes(np.shape(a), np.shape(b))),
    ]
    for _name, rule in shape_rules:
        return rule(x, bias)
```

## 12. Data Type Support / 数据类型支持
Supported dtypes are `float16` and `float32`; mixed supported floating dtypes promote to `float32`.

```python
def add_relu(x, bias):
    """Infer the output dtype for AddRelu.

    Args:
        x: Input tensor-like object with dtype metadata.
        bias: Bias tensor-like object or scalar with dtype metadata.

    Returns:
        String naming the output dtype.

    Raises:
        TypeError: If either input dtype is unsupported.

    Notes:
        The rule returns dtype metadata only and follows table-driven supported dtype behavior.
    """
    dtype_rules = {
        ("float16", "float16"): "float16",
        ("float16", "float32"): "float32",
        ("float32", "float16"): "float32",
        ("float32", "float32"): "float32",
    }
    x_dtype = str(getattr(x, "dtype", x))
    bias_dtype = str(getattr(bias, "dtype", bias))
    key = (x_dtype, bias_dtype)
    if key not in dtype_rules:
        raise TypeError(f"Unsupported AddRelu dtype combination: {key}")
    return dtype_rules[key]
```

## 13. Layout and Format Constraints / Layout 与 Format 约束
The PRD does not establish additional layout constraints beyond supported tensor compatibility.

## 14. Boundary Cases / 边界场景
Empty tensors follow broadcast shape inference and produce empty outputs with the broadcast shape. Scalar bias broadcasts to `x`. Unsupported non-floating dtypes are rejected before computing output values.

## 15. Error Handling / 错误处理
Reject non-broadcastable shapes and unsupported dtype combinations with clear diagnostics.

## 16. Compatibility / 兼容性说明
Behavior is compatible with the reference expression `torch.relu(torch.add(x, bias))` for supported inputs.

## 17. Performance Requirements / 性能要求
No additional performance requirement is specified by the PRD.

## 18. Acceptance Criteria / 验收标准
### Numerical Analysis / 数值分析
#### Floating Point Error Analysis / 浮点误差分析
AddRelu performs one rounded floating-point addition per output element in the promoted supported dtype, followed by an exact ReLU selection between the rounded sum and zero. The ReLU clamp does not introduce additional rounding, but it can expose the sign of a rounded near-zero sum by selecting zero when the rounded sum is non-positive. There are no transcendental approximations, saturating arithmetic modes, or additional casts beyond the supported dtype promotion and output storage rules. The output `y` therefore inherits one addition-rounding error source for non-empty float tensors; empty outputs have no elementwise numerical error and are validated by shape and dtype.
Conclusion: AddRelu precision tolerance is driven by one rounded addition per output element, with no extra error contribution from the ReLU clamp.

#### Stability Analysis / 稳定性分析
The formulation `max(x + bias, 0)` is forward stable for ordinary inputs because it evaluates the specified expression directly with one rounded addition. The only numerically risky region is near the ReLU threshold, where a small addition-rounding difference around zero can change whether the output is exactly zero or a small positive value. No algebraic transformation is required to improve stability because the operator has no subtractive reformulation, reciprocal, normalization, or iterative computation.
Conclusion: AddRelu is stable for supported inputs except for expected threshold sensitivity when the exact sum is near zero.

#### Conditioning / 条件数
For elements whose exact broadcasted sum is positive, the output sensitivity to `x` and `bias` is the sensitivity of addition and is locally well conditioned. For elements whose exact sum is negative, the output is clamped to zero and is insensitive to small perturbations that stay negative. At the discontinuity where the exact sum is zero, the derivative changes abruptly and the output is ill conditioned with respect to sign-changing perturbations. There are no denominators, ties, or reduction axes; overflow and underflow behavior follows the supported floating dtype and reference addition semantics.
Conclusion: AddRelu is well conditioned away from the zero threshold and explicitly ill conditioned at the ReLU boundary.

#### Reduction Error Analysis / 归约误差分析
AddRelu has no reductions, accumulations, or order-dependent aggregation. Broadcasting only selects which `x` and `bias` values participate in each independent elementwise addition. Because each output element uses exactly one addition, there is no accumulation depth, reduction-axis effect, or deterministic-versus-nondeterministic reduction behavior to budget.
Conclusion: Reduction error does not apply to AddRelu because the operator is purely elementwise.

#### Mixed Precision Analysis / 混合精度分析
Supported `float16` and `float32` combinations follow the dtype promotion rules in `InferDtype`; computation and output storage use the promoted supported dtype. A `float16` result may lose precision from half-precision addition and half-precision output storage, while a `float32` result uses the tighter float32 tolerance. Unsupported non-floating dtype combinations raise an error instead of silently casting, and no hidden higher-precision accumulation is specified by the PRD.
Conclusion: Mixed precision behavior is defined by explicit promotion to the output dtype, so tolerance scenarios separate float16 and float32 outputs.

#### Error Budget / 误差预算
The float32 scenario allocates `atol=1.0e-6` and `rtol=1.0e-6` to one rounded float32 addition plus threshold comparison against zero. The float16 scenario allocates `atol=1.0e-3` and `rtol=1.0e-3` to half-precision addition and output storage. The empty-output scenario allocates `atol=0.0` and `rtol=0.0` because there are no elements to compare numerically; only shape and dtype equality are meaningful. These budgets match the YAML scenarios below and apply to the sole output `y`.
Conclusion: The precision YAML tolerances are fully allocated to AddRelu's one addition-rounding source and dtype-specific output precision.

### Precision Standards / 精度标准

```yaml
scenarios:
  - name: "float32 same-shape and broadcast tensor"
    condition: "x and bias are float32 tensors with equal or broadcast-compatible shapes"
    outputs:
      - name: "y"
        dtype: "float32"
        atol: 1.0e-6
        rtol: 1.0e-6
        rationale: "float32 addition may round once before the exact ReLU clamp"
  - name: "float16 scalar or tensor bias"
    condition: "x and bias are float16 values, including scalar bias"
    outputs:
      - name: "y"
        dtype: "float16"
        atol: 1.0e-3
        rtol: 1.0e-3
        rationale: "float16 addition and output storage have half-precision rounding"
  - name: "empty broadcast-compatible tensors"
    condition: "broadcast output has at least one zero-sized dimension"
    outputs:
      - name: "y"
        dtype: "float16 or float32"
        atol: 0.0
        rtol: 0.0
        rationale: "empty outputs are validated by shape and dtype because no elements are compared"
```

### NumPy Compare Function / NumPy 精度比对函数

```python
from typing import Tuple
import numpy as np

def compare(actual_outputs, expected_outputs) -> Tuple[bool]:
    actual = actual_outputs[0] if isinstance(actual_outputs, (list, tuple)) else actual_outputs
    expected = expected_outputs[0] if isinstance(expected_outputs, (list, tuple)) else expected_outputs
    actual_array = np.asarray(actual)
    expected_array = np.asarray(expected)
    if actual_array.shape != expected_array.shape or actual_array.dtype != expected_array.dtype:
        return (False,)
    if actual_array.size == 0:
        return (True,)
    if actual_array.dtype == np.dtype("float16"):
        atol = 1.0e-3
        rtol = 1.0e-3
    else:
        atol = 1.0e-6
        rtol = 1.0e-6
    return (bool(np.allclose(actual_array, expected_array, atol=atol, rtol=rtol, equal_nan=True)),)
```

## 19. Open Issues / 待确认问题
None
