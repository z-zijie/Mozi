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
The output is a tensor with the broadcast shape of `x` and `bias`, containing `max(x + bias, 0)` elementwise.

## 7. Attribute Specification / 属性规格
AddRelu has no attributes.

## 8. Mathematical Semantics / 数学语义
Let \(X \in D^{S_x}\) and \(B \in D^{S_b}\), where \(D \subset \mathbb{R}\) is the supported floating domain and \(S = broadcast(S_x, S_b)\). For every index \(i \in S\), the output \(Y \in D^S\) is defined as \(Y_i = \max(X_{broadcast(i)} + B_{broadcast(i)}, 0)\).

## 9. Functional Semantics / 功能语义
The observable behavior is equivalent to applying addition after broadcasting and then applying ReLU elementwise.

## 10. Numeric Semantics / 数值语义
For finite supported floating inputs, each output element equals the reference expression within the validation tolerance for the dtype.

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
Empty tensors follow broadcast shape inference. Scalar bias broadcasts to `x`. Unsupported non-floating dtypes are rejected.

## 15. Error Handling / 错误处理
Reject non-broadcastable shapes and unsupported dtype combinations with clear diagnostics.

## 16. Compatibility / 兼容性说明
Behavior is compatible with the reference expression `torch.relu(torch.add(x, bias))` for supported inputs.

## 17. Performance Requirements / 性能要求
No additional performance requirement is specified by the PRD.

## 18. Acceptance Criteria / 验收标准
Validation covers same-shape float32 inputs, scalar float16 bias, broadcast-compatible tensor bias, empty tensors, unsupported dtype rejection, shape inference, dtype inference, and documentation completeness.

## 19. Open Issues / 待确认问题
None
