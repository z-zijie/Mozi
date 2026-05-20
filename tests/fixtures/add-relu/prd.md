# AddRelu PRD

## 1. Background / 背景
AddRelu is needed as an NPU operator requirement to represent the common fused expression `relu(x + bias)` while preserving reference-framework observable behavior.

## 2. Goal / 目标
Provide a normalized requirement for an elementwise AddRelu operator that accepts a tensor input and tensor or scalar bias, applies NumPy-style broadcasting, and returns the ReLU of the sum.

## 3. Non-Goals / 非目标
This PRD does not require in-place mutation, quantized integer behavior, custom activation thresholds, or any kernel design, scheduling, tiling, memory-planning, or hardware-instruction strategy.

## 4. User Scenarios / 使用场景
- Operator developers need a clear requirement source before writing a behavioral SPEC.
- Model conversion flows need a single operator requirement for patterns equivalent to `relu(x + bias)`.
- Validation flows need normal, broadcast, scalar-bias, empty-tensor, and unsupported-dtype acceptance criteria.

## 5. Functional Requirements / 功能需求
- Compute `max(x + bias, 0)` elementwise after broadcasting `x` and `bias`.
- Support `float16` and `float32` tensor inputs.
- Support `bias` as a tensor or scalar value broadcastable to `x`.
- Reject unsupported non-floating dtypes.
- Preserve deterministic reference behavior for empty tensors under broadcasting rules.

## 6. Input and Output Overview / 输入输出概述
Inputs are `x`, a floating tensor, and `bias`, a floating tensor or scalar broadcastable with `x`. The output is a floating tensor with the broadcast shape of `x` and `bias`; its dtype follows the supported dtype behavior established by the reference framework for the two inputs.

## 7. NPU ARCH
The target architecture scope is Mozi NPU v1. This section states platform scope only and does not define an execution design.

## 8. 算子原型
算子原型必须使用 PyTorch ATen IR 形式描述。

```text
aten::add_relu(Tensor x, Tensor bias) -> Tensor
```

## 9. Compatibility Requirements / 兼容性需求
The operator should match the observable behavior of a reference expression equivalent to `torch.relu(torch.add(x, bias))` for supported dtypes and broadcastable shapes.

## 10. Accuracy and Numerical Expectations / 精度期望
For supported floating dtypes, numeric results should match the reference expression within the tolerance normally used for the same dtype in operator validation.

## 11. Constraints / 约束
- `x` and `bias` must be broadcast-compatible.
- Only `float16` and `float32` are in scope.
- Non-floating dtypes and unsupported layouts are out of scope unless a later requirement extends this PRD.

## 12. Acceptance Criteria / 验收标准
- A `float32` tensor and same-shape `float32` bias produce the same values as `relu(x + bias)`.
- A `float16` tensor with scalar bias broadcasts correctly and returns the expected dtype.
- Broadcast-compatible tensor shapes produce the expected broadcast output shape.
- Empty tensors follow broadcasting rules and return an empty output with the inferred broadcast shape.
- Non-floating input dtype is rejected with a clear unsupported-input result.

## 13. Open Questions / 待澄清问题
None

## 14. References / 参考资料
- PyTorch reference expression: `torch.relu(torch.add(x, bias))`.
