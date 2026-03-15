#!/usr/bin/env python3
"""
数据源管理器
支持多数据源自动切换和备用方案
"""

import sys
import os
from typing import Dict, List, Optional, Any
import logging
import time
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceManager:
    """
    数据源管理器
    支持多数据源优先级和自动切换
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化数据源管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.sources = {}
        self.source_priority = []
        self.cache_enabled = True
        self.cache_ttl = 3600  # 1小时
        self.data_cache = {}
        
        # 加载配置
        self._load_config(config_path)
        
        # 初始化数据源
        self._init_sources()
    
    def _load_config(self, config_path: Optional[str]):
        """加载配置文件"""
        default_config = {
            'primary_source': 'baostock',
            'fallback_sources': ['akshare'],
            'cache': {
                'enabled': True,
                'ttl_seconds': 3600,
                'max_size_mb': 1024
            },
            'rate_limits': {
                'baostock': 10,  # 请求/秒
                'akshare': 5
            }
        }
        
        # TODO: 从文件加载配置
        self.config = default_config
        self.source_priority = [self.config['primary_source']] + self.config['fallback_sources']
    
    def _init_sources(self):
        """初始化所有数据源"""
        # 尝试初始化Baostock
        if self._try_init_baostock():
            logger.info("✅ Baostock数据源初始化成功")
        
        # 尝试初始化akshare（作为备用）
        if 'akshare' in self.source_priority:
            if self._try_init_akshare():
                logger.info("✅ akshare数据源初始化成功")
            else:
                logger.warning("⚠️ akshare数据源初始化失败，将从备用列表中移除")
                self.source_priority.remove('akshare')
    
    def _try_init_baostock(self) -> bool:
        """尝试初始化Baostock"""
        try:
            import baostock as bs
            self.sources['baostock'] = {
                'module': bs,
                'initialized': False,
                'last_used': None,
                'error_count': 0
            }
            return True
        except ImportError:
            logger.error("❌ Baostock模块未安装，请运行: pip install baostock")
            return False
    
    def _try_init_akshare(self) -> bool:
        """尝试初始化akshare"""
        try:
            import akshare as ak
            self.sources['akshare'] = {
                'module': ak,
                'initialized': True,
                'last_used': None,
                'error_count': 0
            }
            return True
        except ImportError:
            logger.warning("⚠️ akshare模块未安装，将无法使用新闻数据功能")
            logger.info("💡 如需新闻数据功能，请运行: pip install akshare")
            return False
    
    def get_stock_data(self, code: str, start_date: str = None, end_date: str = None, 
                      frequency: str = 'd', **kwargs) -> Optional[Any]:
        """
        获取股票数据（自动选择数据源）
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率 (d=日线, 5=5分钟线等)
            **kwargs: 其他参数
        
        Returns:
            股票数据（DataFrame或None）
        """
        # 检查缓存
        cache_key = f"stock_{code}_{start_date}_{end_date}_{frequency}"
        if self.cache_enabled:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                logger.debug(f"从缓存获取数据: {cache_key}")
                return cached_data
        
        # 按优先级尝试数据源
        for source_name in self.source_priority:
            if source_name not in self.sources:
                continue
                
            try:
                data = self._get_from_source(source_name, 'stock_data', 
                                           code=code, start_date=start_date,
                                           end_date=end_date, frequency=frequency, **kwargs)
                
                if data is not None:
                    # 更新数据源状态
                    self.sources[source_name]['last_used'] = datetime.now()
                    
                    # 缓存数据
                    if self.cache_enabled:
                        self._save_to_cache(cache_key, data)
                    
                    logger.info(f"✅ 从 {source_name} 获取股票数据成功: {code}")
                    return data
                    
            except Exception as e:
                logger.warning(f"❌ 从 {source_name} 获取数据失败: {e}")
                self.sources[source_name]['error_count'] += 1
        
        logger.error(f"❌ 所有数据源均失败，无法获取股票数据: {code}")
        return None
    
    def get_news_data(self, code: str, days: int = 7) -> Optional[List[Dict]]:
        """
        获取新闻数据（优先使用akshare）
        
        Args:
            code: 股票代码
            days: 最近天数
        
        Returns:
            新闻数据列表
        """
        # 检查缓存
        cache_key = f"news_{code}_{days}"
        if self.cache_enabled:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # 新闻数据优先使用akshare
        if 'akshare' in self.sources:
            try:
                news_data = self._get_news_from_akshare(code, days)
                if news_data:
                    if self.cache_enabled:
                        self._save_to_cache(cache_key, news_data)
                    return news_data
            except Exception as e:
                logger.warning(f"❌ 从akshare获取新闻数据失败: {e}")
        
        logger.warning("⚠️ 无法获取新闻数据，Baostock不支持此功能")
        return []
    
    def _get_from_source(self, source_name: str, data_type: str, **kwargs) -> Optional[Any]:
        """从指定数据源获取数据"""
        if source_name == 'baostock':
            return self._get_from_baostock(data_type, **kwargs)
        elif source_name == 'akshare':
            return self._get_from_akshare(data_type, **kwargs)
        else:
            return None
    
    def _get_from_baostock(self, data_type: str, **kwargs) -> Optional[Any]:
        """从Baostock获取数据"""
        try:
            import baostock as bs
            import pandas as pd
            
            # 确保登录
            if not self.sources['baostock']['initialized']:
                lg = bs.login()
                if lg.error_code == '0':
                    self.sources['baostock']['initialized'] = True
                else:
                    raise Exception(f"Baostock登录失败: {lg.error_msg}")
            
            if data_type == 'stock_data':
                code = kwargs.get('code')
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                frequency = kwargs.get('frequency', 'd')
                
                # 转换代码格式
                if not code.startswith(('sh.', 'sz.', 'bj.')):
                    if code.startswith('6'):
                        bs_code = f'sh.{code}'
                    else:
                        bs_code = f'sz.{code}'
                else:
                    bs_code = code
                
                # 构建查询字段
                if frequency == 'd':
                    fields = 'date,code,open,high,low,close,volume,amount,turn,pctChg'
                else:
                    fields = 'date,time,code,open,high,low,close,volume,amount'
                
                rs = bs.query_history_k_data_plus(
                    bs_code, fields,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    adjustflag='3'
                )
                
                if rs.error_code != '0':
                    raise Exception(f"Baostock查询失败: {rs.error_msg}")
                
                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())
                
                if not data_list:
                    return None
                
                df = pd.DataFrame(data_list, columns=rs.fields)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Baostock数据获取异常: {e}")
            raise
    
    def _get_from_akshare(self, data_type: str, **kwargs) -> Optional[Any]:
        """从akshare获取数据"""
        try:
            import akshare as ak
            import pandas as pd
            
            if data_type == 'stock_data':
                # akshare获取股票数据
                code = kwargs.get('code')
                # 这里可以根据需要实现akshare的数据获取
                # 暂时返回None，让Baostock处理
                return None
                
            return None
            
        except Exception as e:
            logger.error(f"akshare数据获取异常: {e}")
            raise
    
    def _get_news_from_akshare(self, code: str, days: int) -> List[Dict]:
        """从akshare获取新闻数据"""
        try:
            import akshare as ak
            import pandas as pd
            from datetime import datetime, timedelta
            
            # 获取新闻数据
            news_df = ak.stock_news_em(symbol=code)
            
            if news_df.empty:
                return []
            
            # 转换时间格式
            news_df['发布时间'] = pd.to_datetime(news_df['发布时间'])
            
            # 筛选最近N天的新闻
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_news = news_df[news_df['发布时间'] >= cutoff_date]
            
            news_list = []
            for _, news in recent_news.iterrows():
                news_item = {
                    'title': news.get('新闻标题', ''),
                    'content': news.get('新闻内容', ''),
                    'source': news.get('新闻来源', ''),
                    'publish_time': news.get('发布时间'),
                    'url': news.get('新闻链接', ''),
                    'importance': 0
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            logger.error(f"akshare新闻获取异常: {e}")
            return []
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if key in self.data_cache:
            cached_item = self.data_cache[key]
            if datetime.now() - cached_item['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_item['data']
            else:
                # 缓存过期，删除
                del self.data_cache[key]
        return None
    
    def _save_to_cache(self, key: str, data: Any):
        """保存数据到缓存"""
        self.data_cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
        # 简单的缓存大小管理（可优化）
        if len(self.data_cache) > 1000:
            # 删除最旧的缓存项
            oldest_key = min(self.data_cache.keys(), 
                           key=lambda k: self.data_cache[k]['timestamp'])
            del self.data_cache[oldest_key]
    
    def get_status(self) -> Dict:
        """获取数据源状态"""
        status = {
            'sources': {},
            'cache': {
                'enabled': self.cache_enabled,
                'size': len(self.data_cache),
                'ttl_seconds': self.cache_ttl
            }
        }
        
        for name, source in self.sources.items():
            status['sources'][name] = {
                'initialized': source.get('initialized', False),
                'last_used': source.get('last_used'),
                'error_count': source.get('error_count', 0),
                'priority': self.source_priority.index(name) if name in self.source_priority else -1
            }
        
        return status


# 全局实例
_data_source_manager = None

def get_data_source_manager() -> DataSourceManager:
    """获取全局数据源管理器实例"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


if __name__ == "__main__":
    # 测试代码
    manager = DataSourceManager()
    
    print("📊 数据源管理器测试")
    print("=" * 50)
    
    # 显示状态
    status = manager.get_status()
    print("数据源状态:")
    for name, info in status['sources'].items():
        print(f"  {name}: {'✅' if info['initialized'] else '❌'} "
              f"(错误数: {info['error_count']})")
    
    # 测试获取股票数据
    print("\n测试获取股票数据...")
    data = manager.get_stock_data('600000', '2025-01-01', '2025-01-10')
    if data is not None:
        print(f"✅ 获取到 {len(data)} 条数据")
    else:
        print("❌ 获取数据失败")
    
    # 测试获取新闻数据
    print("\n测试获取新闻数据...")
    news = manager.get_news_data('600000', days=7)
    if news:
        print(f"✅ 获取到 {len(news)} 条新闻")
    else:
        print("⚠️ 未获取到新闻（可能akshare未安装）")
    
    print("\n测试完成！")