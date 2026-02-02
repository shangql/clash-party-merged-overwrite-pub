"""
HTTP下载器模块
负责从订阅URL下载配置文件到指定目录
"""

import os
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class HTTPDownloader:
    """HTTP文件下载器"""
    
    def __init__(self, download_dir: str = "sub-yamls", timeout: int = 30):
        """
        初始化HTTP下载器
        
        Args:
            download_dir: 下载目录路径
            timeout: 下载超时时间（秒）
        """
        self.download_dir = Path(download_dir)
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # 创建下载目录
        self.download_dir.mkdir(exist_ok=True)
        
        # 设置HTTP请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/x-yaml, application/yaml, text/yaml, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 创建临时文件目录
        self.temp_dir = Path(tempfile.gettempdir()) / "clash_merger"
        self.temp_dir.mkdir(exist_ok=True)
        
    def download_subscription(self, filename: str, url: str) -> bool:
        """
        下载订阅文件
        
        Args:
            filename: 保存的文件名
            url: 订阅URL
            
        Returns:
            bool: 下载是否成功
        """
        output_file = self.download_dir / filename
        
        try:
            self.logger.info(f"开始下载订阅: {filename} from {url}")
            
            # 验证URL格式
            if not self._validate_url(url):
                self.logger.error(f"无效的URL: {url}")
                return False
                
            # 发送HTTP请求
            response = self._make_request(url)
            if not response:
                return False
                
            # 保存到临时文件
            temp_file = self.temp_dir / f"{filename}.tmp"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # 检查并处理Base64编码内容
            import base64
            import re
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否为Base64编码
            base64_pattern = r'^[a-zA-Z0-9+/]{50,}(={0,2})?$'
            if re.match(base64_pattern, content.strip()) and len(content.strip()) > 100:
                self.logger.info(f"检测到Base64编码，正在解码: {filename}")
                try:
                    decoded_bytes = base64.b64decode(content.strip())
                    content = decoded_bytes.decode('utf-8')
                    self.logger.info(f"Base64解码成功，原始大小: {len(decoded_bytes)} 字节")
                    
                    # 重新写入解码后的内容
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as decode_error:
                    self.logger.error(f"Base64解码失败: {str(decode_error)}")
                    temp_file.unlink(missing_ok=True)
                    return False
            
            # 检查是否为URI格式（trojan://, vless://等）
            from urllib.parse import urlparse, parse_qs, unquote
            import json
            
            uri_proxies = []
            for line in content.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 检查是否为URI格式
                if '://' in line and not line.startswith('{') and not line.startswith('mixed-port'):
                    try:
                        # 解析URI
                        uri = line
                        if '#' in uri:
                            uri, fragment = uri.split('#', 1)
                            proxy_name = unquote(fragment) if fragment else f"Proxy_{len(uri_proxies) + 1}"
                        else:
                            proxy_name = f"Proxy_{len(uri_proxies) + 1}"
                        
                        # 解析协议和参数
                        if uri.startswith('trojan://'):
                            protocol = 'trojan'
                            uri = uri[9:]  # 移除 'trojan://'
                        elif uri.startswith('ss://'):
                            protocol = 'ss'
                            uri = uri[5:]  # 移除 'ss://'
                        elif uri.startswith('vless://'):
                            protocol = 'vless'
                            uri = uri[8:]  # 移除 'vless://'
                        elif uri.startswith('vmess://'):
                            protocol = 'vmess'
                            # 解析VMess
                            import base64 as b64
                            json_str = b64.b64decode(uri[8:]).decode('utf-8')
                            vmess_config = json.loads(json_str)
                            
                            proxy = {
                                'name': proxy_name,
                                'type': 'vmess',
                                'server': vmess_config.get('add', vmess_config.get('address', '')),
                                'port': int(vmess_config.get('port', 443)),
                                'uuid': vmess_config.get('id', ''),
                                'alterId': vmess_config.get('aid', 0),
                                'cipher': vmess_config.get('scy', 'auto'),
                                'network': vmess_config.get('net', 'tcp'),
                            }
                            
                            if vmess_config.get('tls') == 'tls':
                                proxy['tls'] = True
                            if vmess_config.get('sni'):
                                proxy['sni'] = vmess_config.get('sni')
                            
                            uri_proxies.append(proxy)
                            continue
                        elif uri.startswith('hysteria2://'):
                            protocol = 'hysteria2'
                            uri = uri[12:]  # 移除 'hysteria2://'
                        else:
                            continue
                        
                        # 解析服务器和端口
                        if '@' in uri:
                            userinfo, server_part = uri.split('@', 1)
                        else:
                            userinfo = None
                            server_part = uri
                        
                        if '?' in server_part:
                            server_addr, query = server_part.split('?', 1)
                        else:
                            server_addr = server_part
                            query = ''
                        
                        # 清理server_addr末尾的斜杠（处理 /? 的情况）
                        server_addr = server_addr.rstrip('/')
                        
                        if ':' in server_addr:
                            server, port = server_addr.rsplit(':', 1)
                        else:
                            continue
                        
                        # 解析参数
                        params = {}
                        for param in query.split('&'):
                            if '=' in param:
                                key, value = param.split('=', 1)
                                params[key] = unquote(value)
                        
                        # 构建代理配置
                        proxy = {
                            'name': proxy_name,
                            'type': protocol,
                            'server': server,
                            'port': int(port),
                        }
                        
                        if userinfo:
                            if ':' in userinfo:
                                if protocol == 'trojan':
                                    proxy['password'] = userinfo
                                elif protocol == 'ss':
                                    password_idx = userinfo.rfind(':')
                                    if password_idx != -1:
                                        proxy['method'] = userinfo[:password_idx]
                                        proxy['password'] = userinfo[password_idx+1:]
                                elif protocol == 'vless':
                                    # vless格式可能是 UUID:flow 或 UUID
                                    parts = userinfo.split(':', 1)
                                    proxy['uuid'] = parts[0]
                                    if len(parts) > 1 and parts[1]:
                                        proxy['flow'] = parts[1]
                            else:
                                # 对于trojan/vless/vmess协议，userinfo就是对应的认证信息
                                if protocol == 'trojan':
                                    proxy['password'] = userinfo
                                elif protocol == 'vless':
                                    proxy['uuid'] = userinfo
                                elif protocol == 'vmess':
                                    proxy['uuid'] = userinfo
                        
                        # vless/vmess协议添加alterId和cipher默认值
                        if protocol == 'vless':
                            if 'alterId' not in proxy:
                                proxy['alterId'] = 0
                            if 'cipher' not in proxy:
                                proxy['cipher'] = 'auto'
                        
                        # 添加其他参数
                        if 'sni' in params:
                            proxy['sni'] = params['sni']
                        if 'servername' in params:
                            proxy['servername'] = params['servername']
                        if 'skip-cert-verify' in params:
                            proxy['skip-cert-verify'] = params['skip-cert-verify'] == '1'
                        if 'allowinsecure' in params:
                            proxy['skip-cert-verify'] = params['allowinsecure'] == '1'
                        if 'allowInsecure' in params:
                            proxy['skip-cert-verify'] = params['allowInsecure'] == '1'
                        if 'insecure' in params:
                            proxy['skip-cert-verify'] = params['insecure'] == '1'
                        if 'udp' in params:
                            proxy['udp'] = params['udp'] == '1'
                        if 'type' in params:
                            proxy['network'] = params['type']
                        
                        # TLS/Reality启用 (支持多种参数名)
                        if params.get('tls') == '1' or params.get('security') == 'tls':
                            proxy['tls'] = True
                        
                        # flow参数（支持flow=xxx格式）
                        if 'flow' in params:
                            proxy['flow'] = params['flow']
                        
                        # encryption参数
                        if 'encryption' in params:
                            proxy['cipher'] = params['encryption']
                        
                        # client-fingerprint参数
                        if 'fp' in params:
                            proxy['client-fingerprint'] = params['fp']
                        elif 'client-fingerprint' in params:
                            proxy['client-fingerprint'] = params['client-fingerprint']
                        
                        # WebSocket相关参数
                        if 'path' in params:
                            ws_opts = {'path': params['path']}
                            if 'host' in params:
                                ws_opts['headers'] = {'Host': params['host']}
                            # early-data相关参数
                            if 'ed' in params:
                                ws_opts['max-early-data'] = int(params['ed'])
                            if 'ecdh' in params:
                                ws_opts['early-data-header-name'] = params['ecdh']
                            proxy['ws-opts'] = ws_opts
                        
                        # Reality相关参数
                        if 'pbk' in params:
                            reality_opts = {'public-key': params['pbk']}
                            if 'sid' in params:
                                reality_opts['short-id'] = params['sid']
                            proxy['reality-opts'] = reality_opts
                        
                        # hysteria2特殊参数
                        if protocol == 'hysteria2':
                            if 'mport' in params:
                                proxy['mport'] = params['mport']
                            if 'ports' in params:
                                proxy['ports'] = params['ports']
                            # hysteria2默认开启udp
                            if 'udp' not in proxy:
                                proxy['udp'] = True
                        
                        # Trojan/Ws的默认参数
                        if protocol == 'trojan':
                            if 'password' not in proxy and 'userinfo' in dir():
                                # 如果userinfo没有:分隔，整个就是password
                                pass  # 已在上面处理
                        
                        uri_proxies.append(proxy)
                        
                    except Exception as e:
                        self.logger.warning(f"解析URI失败: {line[:50]}... 错误: {str(e)}")
                        continue
            
            # 如果包含URI代理，生成YAML格式
            if uri_proxies:
                self.logger.info(f"检测到 {len(uri_proxies)} 个URI格式代理，正在转换为YAML格式")
                
                # 生成YAML内容
                yaml_content = "mixed-port: 7890\nallow-lan: true\nbind-address: '*'\nmode: rule\nlog-level: info\nexternal-controller: '127.0.0.1:9090'\ndns:\n    enable: false\n    ipv6: false\n    default-nameserver: [223.5.5.5, 119.29.29.29]\n    enhanced-mode: fake-ip\n    fake-ip-range: 198.18.0.1/16\n    use-hosts: true\n    nameserver: ['https://doh.pub/dns-query', 'https://dns.alidns.com/dns-query']\n    fallback: ['https://doh.dns.sb/dns-query', 'https://dns.cloudflare.com/dns-query', 'https://dns.twnic.tw/dns-query', 'tls://8.8.4.4:853']\n    fallback-filter: { geoip: true, ipcidr: [240.0.0.0/4, 0.0.0.0/32] }\nproxies:\n"
                
                for proxy in uri_proxies:
                    proxy_json = json.dumps(proxy, ensure_ascii=False, separators=(',', ':'))
                    yaml_content += f"  - {proxy_json}\n"
                
                # 重新写入YAML格式内容
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                    
                self.logger.info(f"URI到YAML转换完成")
            
            # 验证下载内容
            if not self._validate_content(temp_file):
                self.logger.error(f"下载的文件内容无效: {filename}")
                temp_file.unlink(missing_ok=True)
                return False
                
            # 移动到目标位置
            temp_file.replace(output_file)
            
            file_size = output_file.stat().st_size
            self.logger.info(f"下载完成: {filename} ({file_size} 字节)")
            return True
            
        except Exception as e:
            self.logger.error(f"下载订阅时发生错误 {filename}: {str(e)}")
            return False
            
    def _validate_url(self, url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: 待验证的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
            
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            
        Returns:
            requests.Response: HTTP响应对象，失败时返回None
        """
        try:
            session = requests.Session()
            
            # 设置重试策略
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # 发送请求
            response = session.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True  # 验证SSL证书
            )
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接错误: {url}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP错误 {e.response.status_code}: {url}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求异常: {url} - {str(e)}")
        except Exception as e:
            self.logger.error(f"未知错误: {url} - {str(e)}")
            
        return None
        
    def _validate_content(self, file_path: Path) -> bool:
        """
        验证下载的文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 内容是否有效
        """
        try:
            # 检查文件大小
            if file_path.stat().st_size == 0:
                self.logger.error("下载的文件为空")
                return False
                
            # 检查是否为YAML格式
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # 读取前1024字符
                
                # 检查是否包含YAML关键字
                yaml_keywords = ['proxies:', 'proxy-groups:', 'rules:', 'mixed-port:', 'mode:']
                has_yaml_content = any(keyword in content for keyword in yaml_keywords)
                
                if not has_yaml_content:
                    self.logger.error("文件内容不是有效的YAML格式")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"验证文件内容时发生错误: {str(e)}")
            return False
            
    def download_with_progress(self, filename: str, url: str, 
                            progress_callback=None) -> bool:
        """
        带进度显示的下载
        
        Args:
            filename: 保存的文件名
            url: 订阅URL
            progress_callback: 进度回调函数
            
        Returns:
            bool: 下载是否成功
        """
        try:
            output_file = self.download_dir / filename
            temp_file = self.temp_dir / f"{filename}.tmp"
            
            with requests.get(url, headers=self.headers, 
                            timeout=self.timeout, stream=True) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 调用进度回调
                            if progress_callback:
                                progress = (downloaded_size / total_size * 100) if total_size > 0 else 0
                                progress_callback(filename, progress, downloaded_size, total_size)
                            
                # 验证和移动文件
                if self._validate_content(temp_file):
                    temp_file.replace(output_file)
                    return True
                else:
                    temp_file.unlink(missing_ok=True)
                    return False
                    
        except Exception as e:
            self.logger.error(f"下载时发生错误 {filename}: {str(e)}")
            return False
            
    def get_file_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取远程文件信息
        
        Args:
            url: 文件URL
            
        Returns:
            Dict[str, Any]: 文件信息，失败时返回None
        """
        try:
            response = requests.head(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            return {
                'content_length': response.headers.get('content-length'),
                'content_type': response.headers.get('content-type'),
                'last_modified': response.headers.get('last-modified'),
                'etag': response.headers.get('etag'),
                'status_code': response.status_code
            }
            
        except Exception as e:
            self.logger.error(f"获取文件信息时发生错误 {url}: {str(e)}")
            return None
            
    def cleanup(self):
        """清理临时文件"""
        try:
            for temp_file in self.temp_dir.glob("*.tmp"):
                temp_file.unlink(missing_ok=True)
                self.logger.debug(f"清理临时文件: {temp_file}")
        except Exception as e:
            self.logger.error(f"清理临时文件时发生错误: {str(e)}")
            
    def get_download_stats(self) -> Dict[str, Any]:
        """
        获取下载统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'download_dir': str(self.download_dir),
            'dir_exists': self.download_dir.exists(),
            'downloaded_files': [],
            'total_size': 0
        }
        
        if self.download_dir.exists():
            for file_path in self.download_dir.glob("*.yaml"):
                file_size = file_path.stat().st_size
                stats['downloaded_files'].append({
                    'name': file_path.name,
                    'size': file_size,
                    'modified': file_path.stat().st_mtime
                })
                stats['total_size'] += file_size
                
        return stats