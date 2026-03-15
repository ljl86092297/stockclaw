        if rating in ["strong_buy", "buy"]:
            conditions["buy"].append(f"价格跌至¥{ma20:.2f}附近（支撑位）")
            conditions["buy"].append("出现重大利好新闻")
            conditions["buy"].append("成交量放大至平均1.5倍以上")
        
        # 卖出条件
        if rating not in ["strong_sell", "sell"]:
            conditions["sell"].append(f"价格涨至目标位¥{current_price*1.15:.2f}")
            conditions["sell"].append("出现重大利空新闻")
            conditions["sell"].append("技术形态转弱（如跌破MA20）")
        
        # 止损条件
        stop_loss = current_price - atr * 2
        conditions["stop"].append(f"价格跌破止损位¥{stop_loss:.2f}")
        conditions["stop"].append("基本面恶化（如业绩大幅下滑）")
        
        # 重新评估条件
        conditions["re_evaluate"].append("出现重大新闻事件")
        conditions["re_evaluate"].append("价格波动率增加50%以上")
        conditions["re_evaluate"].append("成交量异常变化")
        conditions["re_evaluate"].append("技术指标发出矛盾信号")
        
        return conditions
    
    def _save_analysis(self, stock_code: str, technical: Dict, 
                      fundamental: Dict, recommendation: Dict):
        """保存分析结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO analysis_results (
                stock_code, analysis_time, current_price, ma5, ma10, ma20,
                atr_value, volume_ratio, price_position, pe_ratio, pb_ratio,
                revenue, net_profit, recommendation, buy_price_min, buy_price_max,
                target_price_1, target_price_2, stop_loss_price, holding_days,
                buy_conditions, sell_conditions, stop_conditions, re_evaluate_conditions,
                raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_code,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                technical.get("current_price"),
                technical.get("ma5"),
                technical.get("ma10"),
                technical.get("ma20"),
                technical.get("atr_value"),
                technical.get("volume_ratio"),
                technical.get("price_position"),
                fundamental.get("pe_ratio"),
                fundamental.get("pb_ratio"),
                fundamental.get("revenue", 0),
                fundamental.get("net_profit", 0),
                recommendation.get("investment_rating"),
                recommendation.get("buy_price_min"),
                recommendation.get("buy_price_max"),
                recommendation.get("target_price_1"),
                recommendation.get("target_price_2"),
                recommendation.get("stop_loss_price"),
                recommendation.get("holding_days"),
                json.dumps(recommendation.get("buy_conditions", [])),
                json.dumps(recommendation.get("sell_conditions", [])),
                json.dumps(recommendation.get("stop_conditions", [])),
                json.dumps(recommendation.get("re_evaluate_conditions", [])),
                json.dumps({
                    "technical": technical,
                    "fundamental": fundamental,
                    "recommendation": recommendation
                })
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ 分析结果已保存到数据库")
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def _print_report(self, stock_code: str, technical: Dict, fundamental: Dict,
                     news: Dict, recommendation: Dict):
        """打印分析报告"""
        print(f"\n{'='*80}")
        print(f"🎯 {stock_code} 具体投资建议报告")
        print(f"{'='*80}")
        
        # 基本信息
        print(f"\n📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"📊 当前价格: ¥{technical.get('current_price', 0):.2f}")
        
        # 技术指标
        print(f"\n📈 技术指标（具体数值）:")
        print(f"  MA5: ¥{technical.get('ma5', 0):.2f}")
        print(f"  MA10: ¥{technical.get('ma10', 0):.2f}")
        print(f"  MA20: ¥{technical.get('ma20', 0):.2f} (支撑位)")
        print(f"  ATR: {technical.get('atr_value', 0):.4f}")
        print(f"  量比: {technical.get('volume_ratio', 0):.2f}")
        print(f"  价格位置: {technical.get('price_position', 0):.1f}%")
        print(f"  近期高点: ¥{technical.get('period_high', 0):.2f}")
        print(f"  近期低点: ¥{technical.get('period_low', 0):.2f}")
        
        # 基本面
        print(f"\n🏢 基本面指标:")
        print(f"  市盈率(PE): {fundamental.get('pe_ratio', 'N/A')}")
        print(f"  市净率(PB): {fundamental.get('pb_ratio', 'N/A')}")
        
        # 新闻情绪
        print(f"\n📰 新闻情绪:")
        print(f"  新闻数量: {news.get('news_count', 0)} 条")
        print(f"  情绪得分: {news.get('sentiment_score', 0):.2f}")
        
        # 综合评分
        print(f"\n🏆 综合评分: {recommendation.get('composite_score', 0):.1f}/10")
        print(f"📊 投资评级: {recommendation.get('investment_rating', '未知')}")
        print(f"💡 建议: {recommendation.get('buy_recommendation', '未知')}")
        
        # 具体操作建议
        print(f"\n{'─'*40}")
        print("🎯 具体操作建议")
        print(f"{'─'*40}")
        
        rating = recommendation.get("investment_rating", "")
        
        if rating == "strong_buy":
            print("✅ 决策: 立即买入")
            print(f"   买入价格: ¥{recommendation.get('buy_price_min', 0):.2f} - ¥{recommendation.get('buy_price_max', 0):.2f}")
            print(f"   目标价位: ¥{recommendation.get('target_price_1', 0):.2f} (第一目标)")
            print(f"              ¥{recommendation.get('target_price_2', 0):.2f} (第二目标)")
            print(f"   止损价位: ¥{recommendation.get('stop_loss_price', 0):.2f}")
            print(f"   建议持有: {recommendation.get('holding_days', 0)} 天")
            
        elif rating == "buy":
            print("✅ 决策: 建议买入")
            print(f"   买入价格: ¥{recommendation.get('buy_price_min', 0):.2f} - ¥{recommendation.get('buy_price_max', 0):.2f}")
            print(f"   目标价位: ¥{recommendation.get('target_price_1', 0):.2f}")
            print(f"   止损价位: ¥{recommendation.get('stop_loss_price', 0):.2f}")
            print(f"   建议持有: {recommendation.get('holding_days', 0)} 天")
            
        elif rating == "hold":
            print("🟡 决策: 观望/持有")
            print(f"   等待价格: ¥{recommendation.get('buy_price_min', 0):.2f} 以下")
            print(f"   如已持有，止损位: ¥{recommendation.get('stop_loss_price', 0):.2f}")
            
        elif rating == "sell":
            print("🔴 决策: 建议卖出")
            print(f"   如持有，建议卖出")
            print(f"   不建议买入")
            
        elif rating == "strong_sell":
            print("🔴 决策: 立即卖出")
            print(f"   如持有，立即卖出")
            print(f"   坚决不买入")
        
        # 触发条件
        print(f"\n⚡ 买入触发条件:")
        for condition in recommendation.get("buy_conditions", []):
            print(f"  • {condition}")
        
        print(f"\n🚨 卖出触发条件:")
        for condition in recommendation.get("sell_conditions", []):
            print(f"  • {condition}")
        
        print(f"\n🛑 止损触发条件:")
        for condition in recommendation.get("stop_conditions", []):
            print(f"  • {condition}")
        
        print(f"\n🔄 需要重新评估的情况:")
        for condition in recommendation.get("re_evaluate_conditions", []):
            print(f"  • {condition}")
        
        # 风险收益分析
        current_price = technical.get("current_price", 0)
        target1 = recommendation.get("target_price_1", 0)
        stop_loss = recommendation.get("stop_loss_price", 0)
        
        if current_price > 0 and target1 > 0 and stop_loss > 0:
            potential_return = (target1 - current_price) / current_price * 100
            potential_loss = (current_price - stop_loss) / current_price * 100
            risk_reward_ratio = potential_return / potential_loss if potential_loss > 0 else 0
            
            print(f"\n📊 风险收益分析:")
            print(f"   潜在收益: {potential_return:.1f}% (到第一目标)")
            print(f"   潜在亏损: {potential_loss:.1f}% (到止损位)")
            print(f"   风险收益比: {risk_reward_ratio:.2f}")
            
            if risk_reward_ratio > 2:
                print(f"   ✅ 风险收益比较佳")
            elif risk_reward_ratio > 1:
                print(f"   ⚠️ 风险收益比一般")
            else:
                print(f"   ❌ 风险收益比较差")
        
        print(f"\n{'='*80}")
        print("💎 核心观点:")
        
        if rating in ["strong_buy", "buy"]:
            print("   当前估值合理/偏低，技术面支持，建议买入")
        elif rating == "hold":
            print("   无明显优势，建议等待更好时机")
        else:
            print("   存在明显风险，建议规避")
        
        print(f"\n📅 下次评估: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}")
        print(f"{'='*80}\n")
    
    def export_database_schema(self, output_path: str = "database_schema.sql"):
        """导出数据库结构（用于移植）"""
        conn = sqlite3.connect(self.db_path)
        
        with open(output_path, 'w') as f:
            # 获取表结构
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            f.write("-- StockAnalyzer 数据库结构\n")
            f.write("-- 导出时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            f.write("-- 用于系统移植\n\n")
            
            for table in tables:
                table_name = table[0]
                f.write(f"-- 表: {table_name}\n")
                
                # 获取创建语句
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                create_stmt = cursor.fetchone()[0]
                f.write(create_stmt + ";\n\n")
        
        conn.close()
        print(f"✅ 数据库结构已导出到: {output_path}")
    
    def create_portable_package(self, output_dir: str = "stock_analyzer_portable"):
        """创建可移植包"""
        import shutil
        
        # 创建目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "config"), exist_ok=True)
        
        # 1. 复制代码文件
        shutil.copy2(__file__, os.path.join(output_dir, "stock_analyzer.py"))
        
        # 2. 复制依赖
        shutil.copy2("/home/openclaw/.openclaw/workspace/utils/data_source_manager.py", 
                    os.path.join(output_dir, "data_source_manager.py"))
        
        # 3. 创建配置文件
        config_content = {
            "database_path": "stock_analysis.db",
            "analysis_days": 60,
            "news_days": 14,
            "atr_period": 14,
            "atr_multiplier": 2.0,
            "risk_tolerance": "medium",
            "investment_horizon": "medium"
        }
        
        import yaml
        with open(os.path.join(output_dir, "config", "analyzer_config.yaml"), 'w') as f:
            yaml.dump(config_content, f, default_flow_style=False)
        
        # 4. 创建安装脚本
        install_script = '''#!/bin/bash
# StockAnalyzer 安装脚本

echo "🚀 安装 StockAnalyzer..."
echo "========================"

# 创建必要目录
mkdir -p ~/.stock_analyzer
mkdir -p ~/.stock_analyzer/data

# 复制文件
cp stock_analyzer.py ~/.stock_analyzer/
cp data_source_manager.py ~/.stock_analyzer/
cp -r config ~/.stock_analyzer/

# 创建启动脚本
cat > ~/.stock_analyzer/analyze.sh << 'EOF'
#!/bin/bash
cd ~/.stock_analyzer
python3 stock_analyzer.py "$@"
EOF

chmod +x ~/.stock_analyzer/analyze.sh

# 添加到PATH
echo 'export PATH="$PATH:$HOME/.stock_analyzer"' >> ~/.bashrc

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  分析股票: ~/.stock_analyzer/analyze.sh 600096"
echo "  或: analyze.sh 600096 (重新打开终端后)"
echo ""
echo "数据库位置: ~/.stock_analyzer/data/stock_analysis.db"
echo ""
'''
        
        with open(os.path.join(output_dir, "install.sh"), 'w') as f:
            f.write(install_script)
        
        os.chmod(os.path.join(output_dir, "install.sh"), 0o755)
        
        # 5. 导出数据库结构
        self.export_database_schema(os.path.join(output_dir, "database_schema.sql"))
        
        # 6. 创建README
        readme_content = '''# StockAnalyzer 可移植包

## 包含内容
1. `stock_analyzer.py` - 主分析程序
2. `data_source_manager.py` - 数据源管理器
3. `config/analyzer_config.yaml` - 配置文件
4. `install.sh` - 安装脚本
5. `database_schema.sql` - 数据库结构

## 安装方法
```bash
# 1. 解压
tar -xzf stock_analyzer_portable.tar.gz
cd stock_analyzer_portable

# 2. 运行安装脚本
./install.sh

# 3. 重新打开终端或运行
source ~/.bashrc
```

## 使用方法
```bash
# 分析单只股票
analyze.sh 600096

# 分析结果存储在
# ~/.stock_analyzer/data/stock_analysis.db
```

## 数据库结构
- `analysis_results` - 分析结果
- `performance_log` - 绩效记录

## 配置说明
编辑 `~/.stock_analyzer/config/analyzer_config.yaml` 修改:
- 分析天数
- 风险偏好
- 投资期限
- 等参数

## 数据迁移
如需迁移数据，复制 `~/.stock_analyzer/data/stock_analysis.db` 到新系统即可。
'''
        
        with open(os.path.join(output_dir, "README.md"), 'w') as f:
            f.write(readme_content)
        
        # 7. 打包
        shutil.make_archive("stock_analyzer_portable", 'gztar', output_dir)
        
        print(f"✅ 可移植包已创建: stock_analyzer_portable.tar.gz")
        print(f"   包含: 代码 + 配置 + 安装脚本 + 数据库结构")


# 主函数
if __name__ == "__main__":
    # 创建分析器
    analyzer = StockAnalyzer()
    
    # 分析云天化
    analyzer.analyze("600096")
    
    # 创建可移植包
    analyzer.create_portable_package()
    
    print("\n📦 系统已准备好移植！")
    print("   1. 代码: stock_analyzer.py")
    print("   2. 数据库: stock_analysis.db (本地存储，不上传Git)")
    print("   3. 移植包: stock_analyzer_portable.tar.gz")
    print("   4. 安装脚本: install.sh")