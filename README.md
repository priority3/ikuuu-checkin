# GitHub Actions 自动化部署指南

本文档详细介绍如何使用 GitHub Actions 实现 ikuuu 自动签到的云端自动化运行。

## 🚀 快速开始

### 本地测试配置

如需本地测试，可以直接在 `main.py` 文件中设置测试变量：

```python
# 本地测试变量，本地测试时可以在这里设置，为空时使用环境变量
LOCAL_EMAIL = "your_email@example.com"  # 本地测试时填入邮箱
LOCAL_PASSWORD = "your_password"         # 本地测试时填入密码
```

⚠️ **注意**：
- 本地测试完成后，请将测试变量清空再提交代码
- 不要将包含真实账户信息的代码上传到公开仓库

### 第一步：Fork 或创建仓库

1. **Fork 本仓库**（推荐）
   - 点击右上角的 "Fork" 按钮
   - 选择你的 GitHub 账户

2. **或者创建新仓库**
   - 在 GitHub 创建新的私有仓库
   - 将代码文件上传到仓库

### 第二步：配置 Secrets

⚠️ **重要：GitHub Actions 运行时需要通过 Secrets 配置敏感信息，确保隐私安全**

1. 进入你的 GitHub 仓库页面
2. 点击 `Settings`（设置）
3. 在左侧菜单找到 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 添加以下密钥：

#### 必需的 Secrets

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `IKUUU_EMAIL` | 你的 ikuuu 账户邮箱 | `user@example.com` |
| `IKUUU_PASSWORD` | 你的 ikuuu 账户密码 | `your_password_here` |

#### 配置步骤说明

```
GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret
```

1. **添加邮箱**
   - Name: `IKUUU_EMAIL`
   - Secret: 输入你的邮箱地址

2. **添加密码**
   - Name: `IKUUU_PASSWORD`
   - Secret: 输入你的密码

### 第三步：启用 GitHub Actions

1. 进入仓库的 `Actions` 标签页
2. 如果显示需要启用，点击 `I understand my workflows, go ahead and enable them`
3. 找到 `Daily Check-in` 工作流
4. 点击 `Enable workflow`

## ⏰ 运行时间配置

### 当前配置

```yaml
schedule:
  - cron: '30 16 * * *'  # 北京时间 00:30 每日执行
```

### 时间说明

- **执行时间**: 每天北京时间 00:30（UTC 16:30）
- **时区**: 脚本运行时设置为 `Asia/Shanghai`
- **频率**: 每日一次

### 自定义运行时间

如需修改运行时间，编辑 `.github/workflows/daily-checkin.yml` 文件中的 cron 表达式：

```yaml
# 北京时间 06:00 执行
- cron: '0 22 * * *'

# 北京时间 12:00 执行  
- cron: '0 4 * * *'

# 每天多次执行（早8点和晚8点）
- cron: '0 0 * * *'   # 北京时间 08:00
- cron: '0 12 * * *'  # 北京时间 20:00
```

## 🎯 手动触发

除了定时执行，还支持手动触发：

1. 进入仓库的 `Actions` 标签页
2. 选择 `Daily Check-in` 工作流
3. 点击右侧的 `Run workflow` 按钮
4. 点击绿色的 `Run workflow` 确认

## 📊 查看运行日志

### 查看执行历史

1. 进入 `Actions` 标签页
2. 查看 `Daily Check-in` 工作流的运行历史
3. 点击任意一次运行记录查看详细日志

### 日志输出示例

```
============================================================
[2024-01-01 00:30:15] 🚀 IKUUU.CH 自动签到程序启动
============================================================
[2024-01-01 00:30:16] 🔑 使用环境变量，正在使用账号 use***@example.com 登录...
[2024-01-01 00:30:18] ✅ 登录成功
[2024-01-01 00:30:19] ✅ 签到成功: 获得了 1024MB 流量
============================================================
[2024-01-01 00:30:21] ✨ 程序执行完成
============================================================
```

## 🔧 配置优先级

程序会按以下优先级获取账户信息：

1. **本地测试变量**（`LOCAL_EMAIL`, `LOCAL_PASSWORD`）
2. **环境变量**（`IKUUU_EMAIL`, `IKUUU_PASSWORD`）

这样设计的好处：
- 本地开发时可以直接设置测试变量，无需配置环境变量
- GitHub Actions 运行时会自动使用 Secrets 中的环境变量
- 配置简单，只有两种方式，避免混乱

### 使用示例

**本地测试时**：
```python
LOCAL_EMAIL = "your_email@example.com"
LOCAL_PASSWORD = "your_password"
```

**GitHub Actions 时**：
系统会自动使用 Secrets 中配置的 `IKUUU_EMAIL` 和 `IKUUU_PASSWORD`

## 🛡️ 安全最佳实践

### ✅ 推荐做法

- ✅ 本地测试完成后清空测试变量
- ✅ 使用 GitHub Secrets 存储敏感信息
- ✅ 设置仓库为私有（Private）
- ✅ 定期检查 Actions 运行日志
- ✅ 及时更新依赖包版本

### ❌ 避免的做法

- ❌ 将包含真实账户信息的代码上传到仓库
- ❌ 在代码中硬编码账户信息
- ❌ 在公开仓库中存储敏感信息
- ❌ 共享包含密码的日志
- ❌ 使用弱密码

## 🔍 故障排除

### 常见问题及解决方案

#### 1. 工作流未自动运行

**可能原因**：
- GitHub Actions 未启用
- Secrets 配置错误
- 仓库处于非活跃状态

**解决方案**：
```bash
# 检查 Actions 是否启用
Repository Settings → Actions → General → Allow all actions

# 手动触发一次测试
Actions → Daily Check-in → Run workflow
```

#### 2. 登录失败

**可能原因**：
- 邮箱或密码错误
- 账户被锁定
- 网络连接问题

**解决方案**：
```bash
# 检查 Secrets 配置
Settings → Secrets → IKUUU_EMAIL / IKUUU_PASSWORD

# 确认账户状态
手动登录当前配置的域名网站验证
```

## 📞 支持与反馈

如果遇到问题或有改进建议：

1. 查看 [Issues](../../issues) 页面
2. 创建新的 Issue 描述问题
3. 提供详细的错误日志和环境信息

---

**⚠️ 免责声明**: 本项目仅供学习和个人使用，请遵守相关服务条款。
