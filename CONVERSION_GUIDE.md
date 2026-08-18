# NL2RepoBench → Harbor 转换指南

## ✅ 验证成功的任务

### arguably

- **Oracle**: 82.9% (58/70)
- **Agent (Fable 5)**: 8.6%-11.4% (6-8/70)
- **转换方式**: 手写 Harbor 任务
- **关键特征**: editable install, 相对导入

**文件位置**: `examples/harbor/arguably/`

## 🛠️ 转换脚本

**位置**: `scripts/convert_testfiles_to_harbor.py`

### 使用方法

```bash
python scripts/convert_testfiles_to_harbor.py <task-id> \
  --upstream-url https://github.com/<org>/<repo>
```

### 功能

✅ 自动生成所有必需文件
✅ 自动检测 editable install 需求  
✅ 自动检测测试目录名称
✅ 自动解析预期测试数量

⚠️ 手动步骤：
- 复制上游测试文件到 `tests/test/`
- 调整依赖（tests/Dockerfile）
- 测试 Oracle

## 🚧 常见问题与解决方案

### 1. setuptools-scm 版本检测失败

**症状**: `setuptools-scm was unable to detect version`

**解决方案**: 在 solution/solve.sh 中不删除 .git 目录

### 2. 缺少测试依赖

**解决方案**: 更新 `tests/Dockerfile` 添加所需依赖

### 3. pytest 配置冲突

**解决方案**: 在 verifier Dockerfile 中安装 pytest-cov

### 4. 网络依赖

**解决方案**: 设置 `verifier.environment.network_mode = "public"`

## 📋 转换检查清单

### 准备
- [ ] 确认任务存在
- [ ] 找到上游 URL

### 转换
- [ ] 运行转换脚本
- [ ] 复制测试文件
- [ ] 重命名为 test/（单数）
- [ ] 调整依赖

### 验证
- [ ] 运行 Oracle
- [ ] 检查 reward > 0.8
- [ ] 修复问题

### Agent测试
- [ ] 运行 Agent
- [ ] 检查 reward > 0

## 📝 完整示例

```bash
# 转换
python scripts/convert_testfiles_to_harbor.py arguably \
  --upstream-url https://github.com/treykeown/arguably

# 获取测试
git clone --depth 1 https://github.com/treykeown/arguably /tmp/arguably
cp -r /tmp/arguably/test examples/harbor/arguably/tests/

# 验证 Oracle
cd harbor-runner
uv run harbor run -p ../examples/harbor/arguably -a oracle

# 运行 Agent
uv run harbor run -p ../examples/harbor/arguably \
  -a openhands-sdk -m anthropic/claude-fable-5
```

## 🎓 经验教训

### 成功要素
1. ✅ 手写 Harbor 任务比修改编译器更直接
2. ✅ 参考 ministats 示例
3. ✅ Oracle 验证是必需的
4. ✅ 依赖管理很关键

### 常见陷阱
1. ⚠️ setuptools-scm 需要 .git
2. ⚠️ 测试目录命名需统一
3. ⚠️ 先选简单任务

---

**最后更新**: 2026-08-18 16:55  
**状态**: ✅ 1个任务成功，转换脚本完成  
**下一步**: 批量转换更多任务
