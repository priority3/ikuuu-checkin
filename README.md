# IKUUU 自动签到程序

这是一个用于 IKUUU 网站的自动签到程序，支持通过环境变量灵活配置。

## 功能特性

- 🔐 自动登录和签到
- 📊 显示账户信息（流量、余额、设备等）
- 🌐 支持自定义域名配置
- ⚙️ 支持本地变量和环境变量配置
- 🔄 智能重试机制
- 📝 详细的日志输出

## 配置方式

### 账户配置

#### 方式一：本地变量（适合本地测试）
在代码中直接设置：
```python
LOCAL_EMAIL = "your-email@example.com"
LOCAL_PASSWORD = "your-password"
```

#### 方式二：环境变量（推荐用于GitHub Actions）
设置以下环境变量：
- `IKUUU_EMAIL`: 您的邮箱账号
- `IKUUU_PASSWORD`: 您的密码

### 域名配置

#### 方式一：本地变量
在代码中设置：
```python
LOCAL_DOMAIN = "ikuuu.ch"  # 或其他域名
```

#### 方式二：环境变量（推荐用于GitHub Actions）
设置环境变量：
- `IKUUU_DOMAIN`: 目标域名（如：ikuuu.ch）

如果不设置，程序将使用默认域名 `ikuuu.ch`

## GitHub Actions 使用

在 GitHub 仓库中设置以下 Secrets：

1. 进入仓库设置 → Secrets and variables → Actions
2. 添加以下 Repository secrets：
   - `IKUUU_EMAIL`: 您的邮箱
   - `IKUUU_PASSWORD`: 您的密码
   - `IKUUU_DOMAIN`: 目标域名（可选，不设置则使用默认域名）

## 配置优先级

程序按以下优先级读取配置：

1. **本地变量** (LOCAL_EMAIL, LOCAL_PASSWORD, LOCAL_DOMAIN)
2. **环境变量** (IKUUU_EMAIL, IKUUU_PASSWORD, IKUUU_DOMAIN)
3. **默认值** (仅域名有默认值：ikuuu.ch)

## 运行程序

```bash
python main.py
```

## 注意事项

- 请妥善保管您的账户信息
- 建议在生产环境中使用环境变量而非本地变量
- 程序包含智能重试机制，网络不稳定时会自动重试
- 程序会显示详细的运行日志，便于排查问题

## 依赖库

- requests
- beautifulsoup4
- urllib3

安装依赖：
```bash
pip install requests beautifulsoup4 urllib3
```