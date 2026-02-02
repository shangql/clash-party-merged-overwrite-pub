"""
YAML处理器模块
负责解析YAML格式的Clash配置文件，提取代理节点信息
"""

import re
import logging
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union


class YAMLProcessor:
    """YAML文件处理器"""
    
    def __init__(self):
        """初始化YAML处理器"""
        self.logger = logging.getLogger(__name__)
        
        # 支持的代理类型
        self.supported_proxy_types = {
            'ss', 'ssr', 'vmess', 'vless', 'trojan', 'socks5', 
            'http', 'https', 'hysteria', 'hysteria2', 'snell'
        }
        
    def extract_proxies(self, yaml_file: Path) -> List[Dict[str, Any]]:
        """
        从YAML文件中提取代理配置
        
        Args:
            yaml_file: YAML文件路径
            
        Returns:
            List[Dict[str, Any]]: 代理配置列表
        """
        try:
            self.logger.debug(f"开始解析YAML文件: {yaml_file}")
            
            # 读取YAML文件
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # 检查是否为Base64编码
            import base64
            import re
            
            # Base64模式：以特定字符串开头，包含大量字母数字和+/字符，长度较长
            base64_pattern = r'^[a-zA-Z0-9+/]{50,}(={0,2})?$'
            if re.match(base64_pattern, content) and len(content) > 100:
                self.logger.info(f"检测到Base64编码，正在解码: {yaml_file}")
                try:
                    # 尝试解码Base64
                    decoded_bytes = base64.b64decode(content)
                    content = decoded_bytes.decode('utf-8')
                    self.logger.info(f"Base64解码成功，原始大小: {len(decoded_bytes)} 字节")
                    
                    # 保存解码后的内容到同名文件（添加.decoded标记）
                    decoded_file = yaml_file.parent / (yaml_file.stem + '.decoded' + yaml_file.suffix)
                    with open(decoded_file, 'w', encoding='utf-8') as df:
                        df.write(content)
                    self.logger.info(f"已保存解码后的YAML文件: {decoded_file}")
                except Exception as decode_error:
                    self.logger.error(f"Base64解码失败: {str(decode_error)}")
                    return []
            
            # 解析YAML内容
            yaml_data = self._parse_yaml_content(content)
            if not yaml_data:
                self.logger.warning(f"YAML文件解析失败或为空: {yaml_file}")
                return []
                
            # 提取proxies部分
            proxies = yaml_data.get('proxies', [])
            if not proxies:
                self.logger.warning(f"文件中没有找到proxies配置: {yaml_file}")
                return []
                
            # 处理不同格式的代理配置
            processed_proxies = []
            for i, proxy in enumerate(proxies):
                try:
                    processed_proxy = self._process_proxy_config(proxy, i)
                    if processed_proxy and self._validate_proxy(processed_proxy):
                        processed_proxies.append(processed_proxy)
                    else:
                        self.logger.warning(f"跳过无效的代理配置 #{i+1}")
                except Exception as e:
                    self.logger.warning(f"处理代理配置 #{i+1} 时发生错误: {str(e)}")
                    
            self.logger.info(f"从 {yaml_file.name} 提取了 {len(processed_proxies)} 个有效代理")
            return processed_proxies
            
        except Exception as e:
            self.logger.error(f"提取代理配置时发生错误 {yaml_file}: {str(e)}")
            return []
            
    def _parse_yaml_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析YAML内容
        
        Args:
            content: YAML文本内容
            
        Returns:
            Dict[str, Any]: 解析后的数据，失败时返回None
        """
        try:
            # 尝试使用PyYAML解析
            data = yaml.safe_load(content)
            return data
            
        except yaml.YAMLError as e:
            self.logger.warning(f"标准YAML解析失败: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"解析YAML时发生未知错误: {str(e)}")
            return None
            
    def _process_proxy_config(self, proxy: Union[Dict, str], index: int) -> Optional[Dict[str, Any]]:
        """
        处理单个代理配置
        
        Args:
            proxy: 代理配置（可能是字典或字符串）
            index: 代理索引
            
        Returns:
            Dict[str, Any]: 处理后的代理配置
        """
        if isinstance(proxy, dict):
            return self._normalize_proxy_dict(proxy)
        elif isinstance(proxy, str):
            return self._parse_proxy_string(proxy)
        else:
            self.logger.warning(f"未知的代理配置类型: {type(proxy)}")
            return None
            
    def _normalize_proxy_dict(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化代理配置字典
        
        Args:
            proxy: 原始代理配置
            
        Returns:
            Dict[str, Any]: 标准化后的代理配置
        """
        normalized = proxy.copy()
        
        # 确保有name字段
        if 'name' not in normalized:
            normalized['name'] = f"proxy_{hash(str(proxy)) % 10000}"
            
        # 确保有type字段
        if 'type' not in normalized:
            if 'password' in normalized and 'server' in normalized:
                normalized['type'] = 'trojan'
            elif 'uuid' in normalized:
                normalized['type'] = 'vmess'
            elif 'auth' in normalized:
                normalized['type'] = 'socks5'
            else:
                normalized['type'] = 'unknown'
                
        return normalized
        
    def _parse_proxy_string(self, proxy_str: str) -> Optional[Dict[str, Any]]:
        """
        解析字符串格式的代理配置
        
        Args:
            proxy_str: 代理配置字符串
            
        Returns:
            Dict[str, Any]: 解析后的代理配置
        """
        try:
            # 尝试解析为JSON格式
            if proxy_str.strip().startswith('{') and proxy_str.strip().endswith('}'):
                return json.loads(proxy_str)
                
            # 尝试解析为YAML单行格式
            if ':' in proxy_str:
                import yaml
                try:
                    return yaml.safe_load(f"- {proxy_str}")
                except:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"解析代理字符串失败: {proxy_str}, 错误: {str(e)}")
            
        return None
        
    def _validate_proxy(self, proxy: Dict[str, Any]) -> bool:
        """
        验证代理配置的有效性
        
        Args:
            proxy: 代理配置
            
        Returns:
            bool: 是否有效
        """
        # 检查必需字段
        if 'name' not in proxy or not proxy['name']:
            return False
            
        if 'type' not in proxy:
            return False
            
        if 'server' not in proxy or not proxy['server']:
            return False
            
        if 'port' not in proxy:
            return False
            
        return True
        
    def get_proxy_names(self, yaml_file: Path) -> List[str]:
        """
        获取文件中所有代理的名称
        
        Args:
            yaml_file: YAML文件路径
            
        Returns:
            List[str]: 代理名称列表
        """
        proxies = self.extract_proxies(yaml_file)
        return [proxy.get('name', 'Unknown') for proxy in proxies]