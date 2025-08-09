import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import re
import base64
import time
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 域名配置
# 支持GitHub环境变量 IKUUU_DOMAIN，可以设置不同的域名
# 本地测试时可直接修改 LOCAL_DOMAIN，为空时使用环境变量，默认为 ikuuu.ch
LOCAL_DOMAIN = ""                     # 本地测试时可填入域名，如：ikuuu.ch
DEFAULT_DOMAIN = "ikuuu.ch"           # 默认域名

# 按优先级获取域名：本地变量 > 环境变量 > 默认值
BASE_DOMAIN = LOCAL_DOMAIN if LOCAL_DOMAIN else os.getenv('IKUUU_DOMAIN', DEFAULT_DOMAIN)
BASE_URL = f"https://{BASE_DOMAIN}"

# 本地测试变量，本地测试时可以在这里设置，为空时使用环境变量
LOCAL_EMAIL = "1724747604@qq.com"     # 本地测试时填入邮箱
LOCAL_PASSWORD = "Lzq030152"  # 本地测试时可以填入密码

def print_with_time(message, level="INFO"):
    """带时间戳和级别的打印"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level_emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍"
    }
    emoji = level_emoji.get(level, "ℹ️")
    print(f"[{current_time}] {emoji} {message}")

def print_separator(char="=", length=60):
    """打印分隔线"""
    print(char * length)

def decode_base64_safe(encoded_str):
    """安全地解码Base64字符串"""
    try:
        decoded = base64.b64decode(encoded_str).decode('utf-8')
        print_with_time("成功解码Base64内容", "SUCCESS")
        return decoded
    except Exception as e:
        print_with_time(f"Base64解码失败: {str(e)}", "ERROR")
        return None

def create_session():
    """创建配置完整的会话对象"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    # 设置适配器，避免连接池问题
    adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

def safe_request(method, url, **kwargs):
    """安全的网络请求，包含重试和超时控制"""
    max_retries = 2
    base_timeout = 8  # 降低超时时间
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = attempt * 2
                print_with_time(f"第 {attempt + 1} 次重试，等待 {wait_time} 秒...", "WARNING")
                time.sleep(wait_time)
            
            # 使用新的session
            session = create_session()
            
            # 设置超时
            kwargs['timeout'] = base_timeout
            kwargs['verify'] = False  # 跳过SSL验证
            
            response = session.request(method, url, **kwargs)
            session.close()  # 主动关闭连接
            return response
            
        except requests.exceptions.Timeout:
            print_with_time(f"请求超时 (尝试 {attempt + 1}/{max_retries})", "WARNING")
            if attempt == max_retries - 1:
                print_with_time("所有重试均超时，请检查网络连接", "ERROR")
                return None
        except requests.exceptions.ConnectionError as e:
            print_with_time(f"连接错误: {str(e)} (尝试 {attempt + 1}/{max_retries})", "WARNING")
            if attempt == max_retries - 1:
                print_with_time("网络连接失败，请检查网络状态", "ERROR")
                return None
        except KeyboardInterrupt:
            print_with_time("用户中断操作", "WARNING")
            raise
        except Exception as e:
            print_with_time(f"请求异常: {str(e)} (尝试 {attempt + 1}/{max_retries})", "WARNING")
            if attempt == max_retries - 1:
                return None
    
    return None

def login_and_get_cookie():
    """登录 SSPanel 并获取 Cookie"""
    # 按优先级获取账户信息：本地变量 > 环境变量
    email = LOCAL_EMAIL if LOCAL_EMAIL else os.getenv('IKUUU_EMAIL')
    password = LOCAL_PASSWORD if LOCAL_PASSWORD else os.getenv('IKUUU_PASSWORD')
    
    if not email or not password:
        print_with_time("请设置账户信息", "ERROR")
        print_with_time("可选配置方式:", "INFO")
        print("   📝 1. 在代码中设置 LOCAL_EMAIL 和 LOCAL_PASSWORD")
        print("   🔧 2. 设置环境变量 IKUUU_EMAIL 和 IKUUU_PASSWORD")
        print("")
        print_with_time("可选域名配置:", "INFO")
        print("   📝 1. 在代码中设置 LOCAL_DOMAIN")
        print("   🔧 2. 设置环境变量 IKUUU_DOMAIN")
        print(f"   ⚙️  当前使用域名: {BASE_DOMAIN}")
        return None
    
    # 判断使用的配置方式
    config_source = "本地变量" if LOCAL_EMAIL and LOCAL_PASSWORD else "环境变量"
    domain_source = "本地变量" if LOCAL_DOMAIN else ("环境变量" if os.getenv('IKUUU_DOMAIN') else "默认值")
    masked_email = f"{email[:3]}***{email.split('@')[1]}"
    print_with_time(f"使用{config_source}配置，账号: {masked_email}", "INFO")
    print_with_time(f"使用{domain_source}域名: {BASE_DOMAIN}", "INFO")
    
    try:
        # 获取登录页面
        print_with_time("正在获取登录页面...", "INFO")
        login_page_url = f"{BASE_URL}/auth/login"
        
        response = safe_request('GET', login_page_url)
        
        if not response or response.status_code != 200:
            print_with_time(f"无法访问登录页面，状态码: {response.status_code if response else 'None'}", "ERROR")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找 CSRF token
        csrf_token = None
        csrf_input = soup.find('input', {'name': '_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print_with_time("已获取CSRF令牌", "DEBUG")
        
        # 准备登录数据
        login_data = {
            'email': email,
            'passwd': password
        }
        
        if csrf_token:
            login_data['_token'] = csrf_token
        
        # 发送登录请求
        print_with_time("正在发送登录请求...", "INFO")
        login_url = f"{BASE_URL}/auth/login"
        
        headers = {
            'Origin': BASE_URL,
            'Referer': f"{BASE_URL}/auth/login",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = safe_request('POST', login_url, data=login_data, headers=headers)
        
        if not response:
            print_with_time("登录请求失败", "ERROR")
            return None
        
        # 检查登录结果
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('ret') == 1:
                    print_with_time("登录成功！", "SUCCESS")
                    # 从响应头获取Cookie
                    cookies = response.cookies
                    cookie_string = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies])
                    return cookie_string
                else:
                    error_msg = result.get('msg', '未知错误')
                    print_with_time(f"登录失败: {error_msg}", "ERROR")
                    return None
            except:
                # 可能是重定向到用户页面
                if 'user' in response.url:
                    print_with_time("登录成功（通过重定向检测）", "SUCCESS")
                    cookies = response.cookies
                    cookie_string = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies])
                    return cookie_string
                else:
                    print_with_time("登录状态检测失败", "ERROR")
                    return None
        else:
            print_with_time(f"登录请求失败，状态码: {response.status_code}", "ERROR")
            return None
            
    except KeyboardInterrupt:
        print_with_time("用户中断登录操作", "WARNING")
        raise
    except Exception as e:
        print_with_time(f"登录过程中发生错误: {str(e)}", "ERROR")
        return None

def checkin(cookie):
    """执行签到操作"""
    print_with_time("开始执行签到...", "INFO")
    
    headers = {
        'Origin': BASE_URL,
        'Referer': f"{BASE_URL}/user",
        'Cookie': cookie,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    url = f"{BASE_URL}/user/checkin"
    
    try:
        print_with_time("正在发送签到请求...", "DEBUG")
        response = safe_request('POST', url, headers=headers)
        
        if not response:
            print_with_time("签到请求失败", "ERROR")
            return False
        
        data = response.json()
        
        if data.get('ret') == 1:
            print_with_time(f"签到成功: {data.get('msg', '获得奖励')}", "SUCCESS")
            return True
        elif "已经签到" in data.get('msg', ''):
            print_with_time(f"今日已签到: {data.get('msg', '请明天再来')}", "WARNING")
            return True
        else:
            print_with_time(f"签到失败: {data.get('msg', '未知错误')}", "ERROR")
            return False
            
    except KeyboardInterrupt:
        print_with_time("用户中断签到操作", "WARNING")
        raise
    except Exception as e:
        print_with_time(f"签到请求失败: {str(e)}", "ERROR")
        return False

def extract_account_info(soup):
    """从解析的HTML中提取账户信息"""
    info_found = False
    
    # 查找统计卡片
    stat_cards = soup.find_all('div', class_='card-statistic-2')
    if not stat_cards:
        stat_cards = soup.find_all('div', class_='card-statistic')
    if not stat_cards:
        stat_cards = soup.find_all('div', class_='card')
    
    print_with_time(f"找到 {len(stat_cards)} 个信息卡片", "DEBUG")
    
    for i, card in enumerate(stat_cards, 1):
        # 尝试找到标题
        header = card.find('h4') or card.find('h3') or card.find('h5')
        
        if header:
            title = header.get_text(strip=True)
            
            # 获取主要数值
            body = card.find('div', class_='card-body') or card.find('div', class_='card-content')
            
            if body:
                value_text = re.sub(r'\s+', ' ', body.get_text(strip=True))
                
                # 根据标题分类显示信息
                if any(keyword in title for keyword in ['会员时长', '时长', '到期']):
                    # 清理会员状态显示
                    clean_value = value_text.replace('天', '天').strip()
                    print(f"👑 会员状态: {clean_value}")
                    info_found = True
                    
                elif any(keyword in title for keyword in ['剩余流量', '流量', '可用']):
                    # 清理流量显示
                    clean_value = value_text.strip()
                    print(f"📊 剩余流量: {clean_value}")
                    info_found = True
                    
                    # 查找今日使用量并清理格式
                    stats = card.find('div', class_='card-stats-title') or card.find('div', class_='card-stats')
                    if stats:
                        extra_info = re.sub(r'\s+', ' ', stats.get_text(strip=True))
                        if any(keyword in extra_info for keyword in ['今日', '已用', 'today']):
                            # 清理今日使用量格式，移除重复的冒号
                            clean_extra = extra_info.replace('今日已用 :', '').replace('今日已用:', '').strip()
                            if clean_extra:
                                print(f"📈 今日使用: {clean_extra}")
                                
                elif any(keyword in title for keyword in ['在线设备', '设备', '连接']):
                    # 清理设备数显示
                    clean_value = value_text.strip()
                    print(f"📱 在线设备: {clean_value}")
                    info_found = True
                    
                elif any(keyword in title for keyword in ['钱包', '余额', '积分']):
                    # 清理余额显示
                    clean_value = value_text.strip()
                    print(f"💰 账户余额: {clean_value}")
                    info_found = True
                    
                    # 查找累计返利并清理格式
                    stats = card.find('div', class_='card-stats-title') or card.find('div', class_='card-stats')
                    if stats:
                        extra_info = re.sub(r'\s+', ' ', stats.get_text(strip=True))
                        if extra_info and extra_info != value_text:
                            # 清理返利信息格式，移除重复的冒号和文字
                            clean_extra = extra_info.replace('累计获得返利金额:', '').replace('累计获得返利金额', '').strip()
                            if clean_extra and clean_extra != clean_value:
                                print(f"💎 累计返利: {clean_extra}")
                else:
                    # 显示其他有效信息，清理格式
                    if value_text and len(value_text) > 3 and not value_text.isspace():
                        clean_title = title.replace(':', '').strip()
                        clean_value = value_text.strip()
                        print(f"📋 {clean_title}: {clean_value}")
                        info_found = True
    
    return info_found

def get_user_info(cookie):
    """获取用户信息和流量数据"""
    print_separator("─", 50)
    print_with_time("正在获取账户信息...", "INFO")
    
    headers = {
        'Cookie': cookie
    }
    url = f"{BASE_URL}/user"
    
    try:
        response = safe_request('GET', url, headers=headers)
        
        if not response:
            print_with_time("获取账户信息失败", "ERROR")
            return False
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面标题确认登录状态
        page_title = soup.find('title')
        if page_title:
            title_text = page_title.get_text(strip=True)
            if any(keyword in title_text.lower() for keyword in ['login', '登录']):
                print_with_time("登录状态已失效，请检查账户信息", "ERROR")
                return False
        
        # 检查是否有Base64编码的内容
        scripts = soup.find_all('script')
        decoded_html = None
        
        for script in scripts:
            script_content = script.get_text()
            if 'originBody' in script_content and 'decodeBase64' in script_content:
                # 提取Base64编码的内容
                match = re.search(r'var originBody = "([^"]+)"', script_content)
                if match:
                    encoded_content = match.group(1)
                    decoded_html = decode_base64_safe(encoded_content)
                    break
        
        info_extracted = False
        
        if decoded_html:
            # 解析解码后的HTML
            print_with_time("正在解析解码后的页面内容...", "DEBUG")
            decoded_soup = BeautifulSoup(decoded_html, 'html.parser')
            info_extracted = extract_account_info(decoded_soup)
        else:
            # 尝试直接解析原始页面
            print_with_time("尝试直接解析页面内容...", "DEBUG")
            info_extracted = extract_account_info(soup)
        
        if not info_extracted:
            print_with_time("未能提取到详细账户信息", "WARNING")
            # 尝试查找页面中的数值信息作为备用
            all_text = soup.get_text() if not decoded_html else decoded_html
            numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(GB|MB|天|个|USD|CNY)', all_text)
            if numbers:
                print_with_time("发现以下数值信息:", "INFO")
                unique_numbers = list(set(numbers))[:5]  # 去重并限制数量
                for value, unit in unique_numbers:
                    print(f"📊 {value} {unit}")
            else:
                print_with_time("页面可能使用了高级反爬虫保护", "WARNING")
        
        print_separator("─", 50)
        return True
        
    except KeyboardInterrupt:
        print_with_time("用户中断信息获取操作", "WARNING")
        raise
    except Exception as e:
        print_with_time(f"获取用户信息失败: {str(e)}", "ERROR")
        return False

def main():
    """主程序入口"""
    print_separator("=", 60)
    print_with_time(f"🚀 {BASE_DOMAIN.upper()} 自动签到程序启动", "INFO")
    print_separator("=", 60)
    
    start_time = time.time()
    
    # 登录获取 Cookie
    cookie_data = login_and_get_cookie()
    
    if not cookie_data:
        print_with_time("程序终止：无法获取有效登录状态", "ERROR")
        return False
    
    # 短暂延迟，避免请求过于频繁
    time.sleep(1)
    
    # 执行签到
    checkin_result = checkin(cookie_data)
    
    # 短暂延迟
    time.sleep(1)
    
    # 获取用户信息
    info_result = get_user_info(cookie_data)
    
    # 程序结束统计
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    
    print_separator("=", 60)
    if checkin_result and info_result:
        print_with_time(f"✨ 程序执行完成，耗时 {elapsed_time} 秒", "SUCCESS")
    elif checkin_result:
        print_with_time(f"⚠️ 签到成功但信息获取异常，耗时 {elapsed_time} 秒", "WARNING")
    else:
        print_with_time(f"❌ 程序执行异常，耗时 {elapsed_time} 秒", "ERROR")
    print_separator("=", 60)
    
    return checkin_result

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)