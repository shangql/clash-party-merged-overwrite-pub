"""
格式转换器模块
负责将多行YAML格式转换为JSON单行格式
"""

import json
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path


class FormatConverter:
    """格式转换器"""
    
    def __init__(self):
        """初始化格式转换器"""
        self.logger = logging.getLogger(__name__)
        
    def convert_proxies_to_json(self, proxies: List[Dict[str, Any]]) -> List[str]:
        """
        将代理列表转换为JSON格式字符串列表
        
        Args:
            proxies: 代理配置列表
            
        Returns:
            List[str]: JSON格式的代理配置字符串列表
        """
        json_proxies = []
        for proxy in proxies:
            try:
                # 确保代理配置有name和type字段
                if 'name' not in proxy or 'type' not in proxy:
                    self.logger.warning(f"代理配置缺少必要字段，跳过: {proxy.get('name', 'Unknown')}")
                    continue
                    
                # 转换为JSON字符串
                proxy_json = json.dumps(proxy, ensure_ascii=False, separators=(',', ':'))
                json_proxy = f'  - {proxy_json}'
                json_proxies.append(json_proxy)
                
            except Exception as e:
                self.logger.warning(f"转换代理配置为JSON失败: {str(e)}")
                continue
                
        self.logger.info(f"成功转换 {len(json_proxies)} 个代理为JSON格式")
        return json_proxies
        
    def convert_proxy_groups_to_json(self, proxy_names: List[str]) -> List[str]:
        """
        将代理名称列表转换为JSON格式的proxy-groups配置
        
        Args:
            proxy_names: 代理名称列表
            
        Returns:
            List[str]: JSON格式的proxy-groups配置字符串列表
        """
        json_groups = []
        
        # 构建代理名称的JSON格式列表
        proxies_json_list = []
        for name in proxy_names:
            # 处理特殊字符和引号
            escaped_name = json.dumps(name, ensure_ascii=False)
            proxies_json_list.append(escaped_name)
            
        proxies_content = ', '.join(proxies_json_list)
        
        # 手动选择组
        manual_select = self._create_proxy_group_json(
            '手动选择', 
            'select', 
            ['自动选择', '故障转移'] + proxy_names
        )
        json_groups.append(manual_select)
        
        # 自动选择组
        auto_select = self._create_proxy_group_json(
            '自动选择',
            'url-test',
            proxy_names,
            url='http://www.gstatic.com/generate_204',
            interval=86400
        )
        json_groups.append(auto_select)
        
        # 故障转移组
        fallback = self._create_proxy_group_json(
            '故障转移',
            'fallback',
            proxy_names,
            url='http://www.gstatic.com/generate_204',
            interval=7200
        )
        json_groups.append(fallback)
        
        self.logger.info(f"生成了 {len(json_groups)} 个代理组配置")
        return json_groups
        
    def _create_proxy_group_json(self, name: str, group_type: str, proxies: List[str],
                                url: Optional[str] = None, interval: Optional[int] = None) -> str:
        """
        创建单个代理组的JSON格式配置
        
        Args:
            name: 组名称
            group_type: 组类型（select, url-test, fallback）
            proxies: 代理名称列表
            url: 测试URL（用于url-test和fallback）
            interval: 测试间隔（秒）
            
        Returns:
            str: JSON格式的代理组配置字符串
        """
        # 构建代理名称列表
        proxies_list = []
        for proxy_name in proxies:
            escaped_name = json.dumps(proxy_name, ensure_ascii=False)
            proxies_list.append(escaped_name)
            
        proxies_content = ', '.join(proxies_list)
        
        # 构建JSON对象
        group_data = {
            'name': name,
            'type': group_type,
            'proxies': proxies_list
        }
        
        # 添加url-test或fallback特定字段
        if url:
            group_data['url'] = url
        if interval:
            group_data['interval'] = interval
            
        # 转换为JSON字符串
        group_json = json.dumps(group_data, ensure_ascii=False, separators=(', ', ': '))
        return f'  - {group_json}'
        
    def extract_proxies_from_multiline(self, content: str) -> List[Dict[str, Any]]:
        """
        从多行YAML内容中提取代理配置
        
        Args:
            content: YAML文件内容
            
        Returns:
            List[Dict[str, Any]]: 代理配置列表
        """
        proxies = []
        
        # 查找proxies部分
        lines = content.split('\n')
        in_proxies = False
        current_proxy = {}
        current_indent = 0
        
        for line in lines:
            stripped = line.strip()
            
            # 检测proxies部分开始
            if stripped.startswith('proxies:'):
                in_proxies = True
                current_indent = len(line) - len(line.lstrip())
                continue
                
            # 检测其他顶级部分开始
            if in_proxies and stripped and not line.startswith(' ') and not line.startswith('\t'):
                if not stripped.startswith('#'):
                    break
                    
            # 在proxies部分中
            if in_proxies:
                # 检测新代理开始
                if stripped.startswith('-'):
                    # 保存前一个代理
                    if current_proxy:
                        proxies.append(current_proxy)
                        
                    current_proxy = {'name': '', 'type': '', 'server': '', 'port': 0}
                    # 提取name
                    name_match = re.search(r'name:\s*["\']?([^"\'\s,]+)["\']?', stripped)
                    if name_match:
                        current_proxy['name'] = name_match.group(1)
                        
                # 处理多行属性
                elif current_proxy and ':' in stripped:
                    parts = stripped.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        current_proxy[key] = value
                        
        # 保存最后一个代理
        if current_proxy:
            proxies.append(current_proxy)
            
        return proxies
        
    def format_proxy_to_json_line(self, proxy: Dict[str, Any]) -> str:
        """
        将单个代理配置格式化为JSON单行
        
        Args:
            proxy: 代理配置字典
            
        Returns:
            str: JSON格式的代理配置字符串
        """
        # 确保所有值都是正确的类型
        formatted_proxy = {}
        for key, value in proxy.items():
            if isinstance(value, bool):
                formatted_proxy[key] = value
            elif isinstance(value, (int, float)):
                formatted_proxy[key] = value
            elif isinstance(value, str):
                formatted_proxy[key] = value
            else:
                # 其他复杂类型保持原样
                formatted_proxy[key] = value
                
        proxy_json = json.dumps(formatted_proxy, ensure_ascii=False, separators=(',', ':'))
        return f'  - {proxy_json}'
        
    def convert_to_compact_yaml(self, proxies: List[Dict[str, Any]]) -> str:
        """
        将代理列表转换为紧凑的YAML格式
        
        Args:
            proxies: 代理配置列表
            
        Returns:
            str: 紧凑格式的YAML字符串
        """
        lines = ['proxies:']
        for proxy in proxies:
            line = self.format_proxy_to_json_line(proxy)
            lines.append(line)
            
        return '\n'.join(lines)