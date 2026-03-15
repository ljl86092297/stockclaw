#!/usr/bin/env python3
"""
Baostock数据工具函数
用于替换所有skills中的akshare接口
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# 全局登录状态
_bs_logged_in = False

def bs_login():
    """登录Baostock"""
    global _bs_logged_in
    if not _bs_logged_in:
        lg = bs.login()
        if lg.error_code == '0':
            _bs_logged_in = True
            print("✅ Baostock登录成功")
        else:
            raise Exception(f"Baostock登录失败: {lg.error_msg}")
    return True

def bs_logout():
    """登出Baostock"""
    global _bs_logged_in
    if _bs_logged_in:
        bs.logout()
        _bs_logged_in = False
        print("✅ Baostock已登出")

def get_stock_data(code, start_date=None, end_date=None, frequency='d', adjustflag='3'):
    """
    获取股票K线数据
    
    Args:
        code: 股票代码，如 'sh.600000' 或 'sz.000001'
        start_date: 开始日期，格式 'YYYY-MM-DD'
        end_date: 结束日期，格式 'YYYY-MM-DD'
        frequency: 频率，'d'=日线，'w'=周线，'m'=月线
        adjustflag: 复权类型，'1'=后复权，'2'=前复权，'3'=不复权
    
    Returns:
        pandas.DataFrame
    """
    bs_login()
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 标准化股票代码
    if not code.startswith(('sh.', 'sz.', 'bj.')):
        if code.startswith('6'):
            code = f'sh.{code}'
        else:
            code = f'sz.{code}'
    
    fields = 'date,code,open,high,low,close,volume,amount,turn,pctChg'
    
    rs = bs.query_history_k_data_plus(
        code, 
        fields,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        adjustflag=adjustflag
    )
    
    if rs.error_code != '0':
        raise Exception(f"获取K线数据失败: {rs.error_msg}")
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        raise Exception("未获取到数据")
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 转换数据类型
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 重命名列以兼容现有代码
    df = df.rename(columns={
        'open': '开盘',
        'high': '最高', 
        'low': '最低',
        'close': '收盘',
        'volume': '成交量',
        'amount': '成交额',
        'turn': '换手率',
        'pctChg': '涨跌幅'
    })
    
    return df

def get_financial_data(code, year=None, quarter=None):
    """
    获取财务数据
    
    Args:
        code: 股票代码
        year: 年份，如2024
        quarter: 季度，1-4
    
    Returns:
        dict: 包含各种财务数据的字典
    """
    bs_login()
    
    if not year:
        year = datetime.now().year - 1
    if not quarter:
        quarter = 4
    
    # 标准化股票代码
    if not code.startswith(('sh.', 'sz.', 'bj.')):
        if code.startswith('6'):
            code = f'sh.{code}'
        else:
            code = f'sz.{code}'
    
    financial_data = {}
    
    # 1. 利润表数据
    try:
        rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
        if rs.error_code == '0':
            profit_data = []
            while (rs.error_code == '0') & rs.next():
                profit_data.append(rs.get_row_data())
            if profit_data:
                financial_data['profit'] = pd.DataFrame(profit_data, columns=rs.fields)
    except:
        pass
    
    # 2. 资产负债表
    try:
        rs = bs.query_balance_data(code=code, year=year, quarter=quarter)
        if rs.error_code == '0':
            balance_data = []
            while (rs.error_code == '0') & rs.next():
                balance_data.append(rs.get_row_data())
            if balance_data:
                financial_data['balance'] = pd.DataFrame(balance_data, columns=rs.fields)
    except:
        pass
    
    # 3. 现金流量表
    try:
        rs = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
        if rs.error_code == '0':
            cashflow_data = []
            while (rs.error_code == '0') & rs.next():
                cashflow_data.append(rs.get_row_data())
            if cashflow_data:
                financial_data['cashflow'] = pd.DataFrame(cashflow_data, columns=rs.fields)
    except:
        pass
    
    # 4. 成长能力指标
    try:
        rs = bs.query_growth_data(code=code, year=year, quarter=quarter)
        if rs.error_code == '0':
            growth_data = []
            while (rs.error_code == '0') & rs.next():
                growth_data.append(rs.get_row_data())
            if growth_data:
                financial_data['growth'] = pd.DataFrame(growth_data, columns=rs.fields)
    except:
        pass
    
    # 5. 营运能力指标
    try:
        rs = bs.query_operation_data(code=code, year=year, quarter=quarter)
        if rs.error_code == '0':
            operation_data = []
            while (rs.error_code == '0') & rs.next():
                operation_data.append(rs.get_row_data())
            if operation_data:
                financial_data['operation'] = pd.DataFrame(operation_data, columns=rs.fields)
    except:
        pass
    
    # 6. 杜邦分析
    try:
        rs = bs.query_dupont_data(code=code, year=year, quarter=quarter)
        if rs.error_code == '0':
            dupont_data = []
            while (rs.error_code == '0') & rs.next():
                dupont_data.append(rs.get_row_data())
            if dupont_data:
                financial_data['dupont'] = pd.DataFrame(dupont_data, columns=rs.fields)
    except:
        pass
    
    return financial_data

def get_valuation_data(code, start_date=None, end_date=None):
    """
    获取估值数据
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        pandas.DataFrame
    """
    bs_login()
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 标准化股票代码
    if not code.startswith(('sh.', 'sz.', 'bj.')):
        if code.startswith('6'):
            code = f'sh.{code}'
        else:
            code = f'sz.{code}'
    
    # 使用query_history_k_data_plus获取估值指标
    fields = 'date,code,close,turn,pctChg,peTTM,pbMRQ,psTTM'
    
    rs = bs.query_history_k_data_plus(
        code,
        fields,
        start_date=start_date,
        end_date=end_date,
        frequency='d',
        adjustflag='3'
    )
    
    if rs.error_code != '0':
        raise Exception(f"获取估值数据失败: {rs.error_msg}")
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        raise Exception("未获取到估值数据")
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 转换数据类型
    numeric_cols = ['close', 'turn', 'pctChg', 'peTTM', 'pbMRQ', 'psTTM']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 重命名列
    df = df.rename(columns={
        'date': 'trade_date',
        'close': '收盘价',
        'turn': '换手率',
        'pctChg': '涨跌幅',
        'peTTM': '市盈率TTM',
        'pbMRQ': '市净率MRQ',
        'psTTM': '市销率TTM'
    })
    
    return df

def get_stock_basic_info(code):
    """
    获取股票基本信息
    
    Args:
        code: 股票代码
    
    Returns:
        dict: 股票基本信息
    """
    bs_login()
    
    # 标准化股票代码
    if not code.startswith(('sh.', 'sz.', 'bj.')):
        if code.startswith('6'):
            code = f'sh.{code}'
        else:
            code = f'sz.{code}'
    
    rs = bs.query_stock_basic(code=code)
    
    if rs.error_code != '0':
        raise Exception(f"获取股票基本信息失败: {rs.error_msg}")
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        raise Exception("未获取到股票基本信息")
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 转换为字典
    info = {}
    for col in df.columns:
        info[col] = df[col].iloc[0] if not df[col].isna().all() else None
    
    return info

def get_industry_info(code=None):
    """
    获取行业信息
    
    Args:
        code: 股票代码（可选）
    
    Returns:
        pandas.DataFrame: 行业信息
    """
    bs_login()
    
    rs = bs.query_stock_industry()
    
    if rs.error_code != '0':
        raise Exception(f"获取行业信息失败: {rs.error_msg}")
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        raise Exception("未获取到行业信息")
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 如果指定了股票代码，筛选该股票
    if code:
        # 标准化股票代码
        if not code.startswith(('sh.', 'sz.', 'bj.')):
            if code.startswith('6'):
                code = f'sh.{code}'
            else:
                code = f'sz.{code}'
        
        df = df[df['code'] == code]
    
    return df

def get_market_data(codes, start_date=None, end_date=None):
    """
    批量获取多只股票数据
    
    Args:
        codes: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        dict: 股票代码到DataFrame的映射
    """
    result = {}
    
    for code in codes:
        try:
            df = get_stock_data(code, start_date, end_date)
            result[code] = df
            time.sleep(0.1)  # 避免请求过快
        except Exception as e:
            print(f"获取股票 {code} 数据失败: {e}")
            result[code] = None
    
    return result

# 测试函数
if __name__ == "__main__":
    try:
        # 测试K线数据
        print("测试K线数据获取...")
        df = get_stock_data('600000', '2025-01-01', '2025-01-10')
        print(f"获取到 {len(df)} 条K线数据")
        print(df.head())
        
        # 测试基本信息
        print("\n测试股票基本信息获取...")
        info = get_stock_basic_info('600000')
        print(f"股票名称: {info.get('code_name', 'N/A')}")
        print(f"上市日期: {info.get('ipoDate', 'N/A')}")
        print(f"行业: {info.get('industry', 'N/A')}")
        
        # 测试估值数据
        print("\n测试估值数据获取...")
        valuation = get_valuation_data('600000', '2025-01-01', '2025-01-10')
        print(f"获取到 {len(valuation)} 条估值数据")
        print(valuation[['trade_date', '市盈率TTM', '市净率MRQ', '市销率TTM']].head())
        
        bs_logout()
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        bs_logout()