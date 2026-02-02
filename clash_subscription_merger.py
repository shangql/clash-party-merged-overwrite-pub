#!/usr/bin/env python3
"""
Clash订阅合并工具 - Python版本
用于从多个订阅源下载配置，合并代理节点，生成统一的Clash配置文件

功能特性：
- 读取订阅配置文件
- HTTP下载订阅文件
- 解析和合并YAML配置
- 格式转换为JSON格式
- 生成完整的Clash配置
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.config_parser import ConfigParser
from modules.http_downloader import HTTPDownloader
from modules.yaml_processor import YAMLProcessor
from modules.format_converter import FormatConverter
from modules.config_generator import ConfigGenerator


class ClashSubscriptionMerger:
    """Clash订阅合并工具主类"""
    
    def __init__(self, config_file: str = "subscriptions.conf", 
                 output_dir: str = "merged-yamls",
                 download_dir: str = "sub-yamls"):
        """
        初始化Clash订阅合并工具
        
        Args:
            config_file: 订阅配置文件路径
            output_dir: 输出目录路径
            download_dir: 下载目录路径
        """
        self.config_file = config_file
        self.output_dir = Path(output_dir)
        self.download_dir = Path(download_dir)
        self.output_file = self.output_dir / "sub_by_opencode.yaml"
        
        # 初始化各个模块
        self.config_parser = ConfigParser(config_file)
        self.downloader = HTTPDownloader(download_dir)
        self.yaml_processor = YAMLProcessor()
        self.format_converter = FormatConverter()
        self.config_generator = ConfigGenerator()
        
        # 设置日志
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/clash_merger.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run(self, dry_run: bool = False) -> bool:
        """
        运行订阅合并流程
        
        Args:
            dry_run: 是否为预演模式
            
        Returns:
            bool: 是否成功完成
        """
        try:
            self.logger.info("=" * 50)
            self.logger.info("Clash订阅合并工具启动")
            self.logger.info("=" * 50)
            
            # 步骤1：读取订阅配置
            self.logger.info("步骤1：读取订阅配置...")
            subscriptions = self.config_parser.parse_subscriptions()
            self.logger.info(f"成功读取 {len(subscriptions)} 个订阅配置")
            
            # 步骤2：下载订阅文件
            self.logger.info("步骤2：下载订阅文件...")
            downloaded_files = []
            for filename, url in subscriptions:
                success = self.downloader.download_subscription(filename, url)
                if success:
                    downloaded_files.append(self.download_dir / filename)
                    
            if not downloaded_files:
                self.logger.error("没有可用的订阅文件")
                return False
                
            # 步骤3：解析YAML文件
            self.logger.info("步骤3：解析YAML文件...")
            all_proxies = []
            for file_path in downloaded_files:
                proxies = self.yaml_processor.extract_proxies(file_path)
                if proxies:
                    all_proxies.extend(proxies)
                    self.logger.info(f"从 {file_path.name} 提取了 {len(proxies)} 个代理节点")
                    
            if not all_proxies:
                self.logger.error("没有提取到任何代理节点")
                return False
                
            # 步骤4：格式转换为JSON格式（仅用于日志）
            self.logger.info("步骤4：转换为JSON格式...")
            json_proxy_count = len(self.format_converter.convert_proxies_to_json(all_proxies))
            
            # 步骤5：生成最终配置
            self.logger.info("步骤5：生成最终配置...")
            
            # 确保输出目录存在
            self.output_dir.mkdir(exist_ok=True)
            
            if dry_run:
                # 预演模式，只显示结果不保存
                config_preview = self.config_generator.generate_config_preview(
                    all_proxies, self.output_file
                )
                self.logger.info("预演模式：生成的配置预览")
                print("=" * 50)
                print(config_preview)
                print("=" * 50)
            else:
                # 正式模式，生成配置文件
                success = self.config_generator.generate_config(
                    all_proxies, self.output_file
                )
                if success:
                    self.logger.info(f"配置文件已生成: {self.output_file}")
                    self.logger.info(f"文件大小: {self.output_file.stat().st_size} 字节")
                else:
                    self.logger.error("生成配置文件失败")
                    return False
                    
            self.logger.info("=" * 50)
            self.logger.info("任务完成！")
            self.logger.info(f"总共处理了 {len(all_proxies)} 个代理节点")
            self.logger.info(f"来自 {len(downloaded_files)} 个订阅源")
            self.logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            self.logger.error(f"执行过程中发生错误: {str(e)}")
            return False
            
    def cleanup(self):
        """清理临时文件"""
        self.downloader.cleanup()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Clash订阅合并工具 - 从多个订阅源合并代理配置"
    )
    parser.add_argument(
        "--config", "-c",
        default="subscriptions.conf",
        help="订阅配置文件路径 (默认: subscriptions.conf)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="merged-yamls",
        help="输出目录路径 (默认: merged-yamls)"
    )
    parser.add_argument(
        "--download-dir", "-d",
        default="sub-yamls",
        help="下载目录路径 (默认: sub-yamls)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="预演模式，只显示结果不保存文件"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细日志输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建合并工具实例
    merger = ClashSubscriptionMerger(
        config_file=args.config,
        output_dir=args.output_dir,
        download_dir=args.download_dir
    )
    
    try:
        # 运行合并流程
        success = merger.run(dry_run=args.dry_run)
        
        # 清理临时文件
        merger.cleanup()
        
        # 退出程序
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
        merger.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"程序异常退出: {e}")
        merger.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()