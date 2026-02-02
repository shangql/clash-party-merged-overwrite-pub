"""
配置解析器模块
负责读取和解析subscriptions.conf文件，提取订阅配置信息
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional


class ConfigParser:
    """订阅配置解析器"""
    
    def __init__(self, config_file: str):
        """
        初始化配置解析器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        
        # 配置文件格式正则表达式
        self.config_pattern = re.compile(r'^\s*([^|]+)\s*\|\s*(.+?)\s*$')
        
    def parse_subscriptions(self) -> List[Tuple[str, str]]:
        """
        解析订阅配置文件
        
        Returns:
            List[Tuple[str, str]]: 订阅配置列表，格式为[(文件名, URL), ...]
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if not self.config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
            
        subscriptions = []
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                    
                # 解析配置行
                match = self.config_pattern.match(line)
                if not match:
                    self.logger.warning(f"第{line_num}行格式错误，跳过: {line}")
                    continue
                    
                filename = match.group(1).strip()
                url = match.group(2).strip()
                
                # 验证文件名和URL
                if not filename:
                    self.logger.warning(f"第{line_num}行文件名为空，跳过: {line}")
                    continue
                    
                if not url:
                    self.logger.warning(f"第{line_num}行URL为空，跳过: {line}")
                    continue
                    
                subscriptions.append((filename, url))
                self.logger.debug(f"解析订阅: {filename} -> {url}")
                
        except Exception as e:
            raise ValueError(f"读取配置文件时发生错误: {str(e)}")
            
        if not subscriptions:
            raise ValueError("配置文件中没有找到有效的订阅配置")
            
        self.logger.info(f"成功解析 {len(subscriptions)} 个订阅配置")
        return subscriptions
        
    def validate_subscription(self, filename: str, url: str) -> bool:
        """
        验证单个订阅配置的有效性
        
        Args:
            filename: 文件名
            url: 订阅URL
            
        Returns:
            bool: 是否有效
        """
        # 检查文件名格式
        if not filename.endswith('.yaml') and not filename.endswith('.yml'):
            self.logger.warning(f"文件名格式可能不正确: {filename}")
            
        # 检查URL格式
        url_pattern = re.compile(r'^https?://.+$')
        if not url_pattern.match(url):
            self.logger.warning(f"URL格式可能不正确: {url}")
            return False
            
        return True
        
    def get_excluded_subscriptions(self) -> List[str]:
        """
        获取需要排除的订阅列表
        
        Returns:
            List[str]: 排除的订阅文件名列表
        """
        return []
        
    def filter_subscriptions(self, subscriptions: List[Tuple[str, str]], 
                          include_excluded: bool = False) -> List[Tuple[str, str]]:
        """
        过滤订阅配置
        
        Args:
            subscriptions: 订阅配置列表
            include_excluded: 是否包含排除的订阅
            
        Returns:
            List[Tuple[str, str]]: 过滤后的订阅配置列表
        """
        if include_excluded:
            return subscriptions
            
        excluded = self.get_excluded_subscriptions()
        filtered = []
        
        for filename, url in subscriptions:
            if filename not in excluded:
                filtered.append((filename, url))
            else:
                self.logger.info(f"排除订阅: {filename}")
                
        return filtered
        
    def get_subscription_info(self) -> dict:
        """
        获取订阅配置的统计信息
        
        Returns:
            dict: 统计信息
        """
        try:
            subscriptions = self.parse_subscriptions()
            excluded = self.get_excluded_subscriptions()
            
            total_count = len(subscriptions)
            excluded_count = sum(1 for filename, _ in subscriptions if filename in excluded)
            active_count = total_count - excluded_count
            
            return {
                'total_subscriptions': total_count,
                'excluded_subscriptions': excluded_count,
                'active_subscriptions': active_count,
                'excluded_list': excluded,
                'config_file': str(self.config_file),
                'file_exists': self.config_file.exists(),
                'file_size': self.config_file.stat().st_size if self.config_file.exists() else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取订阅信息时发生错误: {str(e)}")
            return {
                'error': str(e),
                'config_file': str(self.config_file),
                'file_exists': self.config_file.exists()
            }