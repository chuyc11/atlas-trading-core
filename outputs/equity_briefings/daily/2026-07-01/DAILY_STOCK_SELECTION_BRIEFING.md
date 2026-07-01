# A 股全市场 AI 选股研究简报 - 2026-07-01

- as_of_date: 2026-07-01
- generated_at: 2026-07-01T16:11:52.856045Z
- current_version: v0.7.7-a-share-daily-stock-selection-briefing
- input_chain: v0.7.3 features -> v0.7.4 scores -> v0.7.5 candidates -> v0.7.6 virtual portfolios -> v0.7.7 briefing
- data_sources: existing score, candidate, virtual portfolio, exposure, risk/liquidity, and audit artifacts

## 今日总体结论

- strict tradable universe 覆盖 3699 只，评分覆盖 3699 只。
- 长期/中期/短期研究候选数量分别为 30 / 30 / 30，本简报各展示前 10 / 10 / 10 只。
- 多周期共振候选 50 只，本简报展示前 10 只；这只是多周期相对评分靠前。
- 风险降级股票 289 只，说明部分高分股票仍被风险、流动性或置信度约束排除。
- 长期/中期/短期虚拟组合持仓数量为 30 / 30 / 20。
- 主要集中方向：长期 Unclassified/CHINEXT/300 (25.00%)，中期 Unclassified/STAR/688 (25.00%)，短期 Unclassified/CHINEXT/300 (25.03%)。
- 风险与流动性概览：长期均值 71.210887 / 65.780552，中期均值 48.551286 / 62.319024，短期均值 68.59814 / 69.289183。
- 本阶段只做每日中文信息简报，不重新生成评分、候选股或虚拟组合。

## 数据日期和覆盖状态

- strict tradable universe: 3699
- scored symbols: 3699
- candidate version: v0.7.5-a-share-candidate-generation-system
- score version: v0.7.4-a-share-long-mid-short-scoring-system
- feature version: v0.7.3-a-share-multi-horizon-feature-engineering
- portfolio version: v0.7.6-a-share-virtual-portfolio-construction
- source_trace_complete: true

## 长期研究候选 Top 10

| Rank | Symbol | Name | Industry | LongScore | LongRank | Risk | Liquidity | FundamentalScore | Composite | Inclusion | Risk Notes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 688002.SH | 睿创微纳 | Unclassified | 71.072920 | 1 | 65.635870 | 58.592863 | 69.553287 | 71.791812 | high_long_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 2 | 688127.SH | 蓝特光学 | Unclassified | 69.864234 | 2 | 52.035911 | 62.837141 | 66.438016 | 72.015105 | high_long_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 3 | 603259.SH | 药明康德 | Unclassified | 69.238700 | 3 | 79.651257 | 77.551365 | 70.826337 | 75.542604 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 4 | 600999.SH | 招商证券 | Unclassified | 68.595152 | 4 | 91.510656 | 77.597098 | 68.593825 | 77.055801 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 5 | 300308.SZ | 中际旭创 | Unclassified | 68.428953 | 5 | 52.811458 | 70.994526 | 67.133171 | 69.243849 | high_long_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 6 | 603268.SH | 松发股份 | Unclassified | 67.608725 | 6 | 62.856065 | 60.868027 | 67.145535 | 66.690074 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 7 | 688059.SH | 华锐精密 | Unclassified | 67.509033 | 7 | 54.081734 | 50.262909 | 66.541054 | 72.423280 | high_long_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 8 | 300750.SZ | 宁德时代 | Unclassified | 67.338073 | 8 | 79.433180 | 63.437753 | 66.483787 | 61.355375 | high_long_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 9 | 301345.SZ | 涛涛车业 | Unclassified | 67.252653 | 9 | 63.073466 | 44.730107 | 68.957909 | 61.784048 | high_long_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score | low_liquidity_score |
| 10 | 600909.SH | 华安证券 | Unclassified | 67.056812 | 10 | 72.779805 | 80.475128 | 58.747461 | 72.726574 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |

## 中期研究候选 Top 10

| Rank | Symbol | Name | Industry | MidScore | MidRank | Risk | Liquidity | IndustryScore | Composite | Inclusion | Risk Notes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 300408.SZ | 三环集团 | Unclassified | 85.042274 | 2 | 42.662657 | 76.508741 | 73.781878 | 73.380774 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 2 | 300604.SZ | 长川科技 | Unclassified | 84.903833 | 3 | 39.600680 | 65.217626 | 74.050419 | 72.580798 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | low_risk_score |
| 3 | 688059.SH | 华锐精密 | Unclassified | 84.179654 | 6 | 54.081734 | 50.262909 | 83.893395 | 72.423280 | high_mid_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 4 | 300308.SZ | 中际旭创 | Unclassified | 83.150367 | 9 | 52.811458 | 70.994526 | 71.365009 | 69.243849 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 5 | 300201.SZ | 海伦哲 | Unclassified | 83.004257 | 10 | 59.439713 | 62.349284 | 71.903893 | 71.903387 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_trend_component | no_major_risk_flag_detected |
| 6 | 688127.SH | 蓝特光学 | Unclassified | 82.619624 | 14 | 52.035911 | 62.837141 | 81.676579 | 72.015105 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 7 | 301536.SZ | 星宸科技 | Unclassified | 82.367116 | 17 | 59.259034 | 60.396954 | 72.967243 | 70.617221 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 8 | 301200.SZ | 大族数控 | Unclassified | 82.358878 | 18 | 40.069501 | 53.561323 | 73.477291 | 69.062355 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 9 | 600176.SH | 中国巨石 | Unclassified | 82.072794 | 20 | 40.674732 | 76.289763 | 53.082567 | 70.958526 | high_mid_percentile, strong_composite_percentile, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 10 | 300054.SZ | 鼎龙股份 | Unclassified | 81.810561 | 22 | 40.529873 | 66.151888 | 73.453861 | 71.247664 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |

## 短期研究候选 Top 10

| Rank | Symbol | Name | Industry | ShortScore | ShortRank | Risk | Liquidity | IndustryScore | Composite | Inclusion | Risk Notes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 600999.SH | 招商证券 | Unclassified | 82.713029 | 2 | 91.510656 | 77.597098 | 51.473123 | 77.055801 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |
| 2 | 603379.SH | 三美股份 | Unclassified | 82.371569 | 3 | 52.146977 | 70.603204 | 51.408241 | 71.271601 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | overheat_risk |
| 3 | 300759.SZ | 康龙化成 | Unclassified | 82.361303 | 4 | 69.081283 | 75.809453 | 68.326349 | 69.761465 | high_short_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | overheat_risk |
| 4 | 000783.SZ | 长江证券 | Unclassified | 82.283084 | 5 | 73.058146 | 83.837298 | 40.562100 | 73.168657 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | overheat_risk |
| 5 | 603259.SH | 药明康德 | Unclassified | 81.052783 | 10 | 79.651257 | 77.551365 | 50.833311 | 75.542604 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | overheat_risk |
| 6 | 601108.SH | 财通证券 | Unclassified | 79.143202 | 18 | 84.878683 | 70.045283 | 49.517640 | 70.216601 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |
| 7 | 300873.SZ | 海晨股份 | Unclassified | 78.804159 | 22 | 69.549878 | 53.144544 | 70.561188 | 68.326115 | high_short_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_momentum_component | no_major_risk_flag_detected |
| 8 | 300121.SZ | 阳谷华泰 | Unclassified | 78.780864 | 23 | 36.042399 | 58.855547 | 69.692484 | 63.595967 | high_short_percentile, strong_composite_percentile, strong_industry_score, strong_momentum_component | low_risk_score, overheat_risk |
| 9 | 601162.SH | 天风证券 | Unclassified | 78.445502 | 25 | 70.712693 | 77.658827 | 46.570898 | 59.700317 | high_short_percentile, strong_liquidity_score, acceptable_risk_score, strong_momentum_component | no_major_risk_flag_detected |
| 10 | 300434.SZ | 金石亚药 | Unclassified | 78.178573 | 27 | 59.246756 | 53.176309 | 68.535415 | 64.909279 | high_short_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | overheat_risk |

## 多周期共振候选

多周期共振只是多周期评分靠前，不代表确定上涨；这里用于后续研究跟踪排序。

| Symbol | Name | Overlap | Best Horizon | Long | Mid | Short | Composite | Strengths | Risk Notes |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 600999.SH | 招商证券 | Long+Mid+Short | Short | 68.595152 | 78.124600 | 82.713029 | 77.055801 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 603259.SH | 药明康德 | Long+Mid+Short | Long | 69.238700 | 76.136191 | 81.052783 | 75.542604 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 300408.SZ | 三环集团 | Long+Mid+Short | Mid | 66.071744 | 85.042274 | 71.343539 | 73.380774 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 000783.SZ | 长江证券 | Long+Mid+Short | Short | 64.513833 | 72.568469 | 82.283084 | 73.168657 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 600160.SH | 巨化股份 | Long+Mid+Short | Long | 66.753591 | 77.039033 | 76.486825 | 73.106134 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 688766.SH | 普冉股份 | Long+Mid+Short | Mid | 65.603814 | 85.670168 | 74.532757 | 72.893715 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | low_risk_score |
| 300566.SZ | 激智科技 | Long+Mid+Short | Long | 65.188586 | 80.339981 | 77.419190 | 72.853506 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 600909.SH | 华安证券 | Long+Mid+Short | Long | 67.056812 | 78.503190 | 69.882670 | 72.726574 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 688432.SH | 有研硅 | Long+Mid+Short | Short | 60.632683 | 82.383482 | 80.711059 | 72.593308 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | low_risk_score |
| 300604.SZ | 长川科技 | Long+Mid+Short | Mid | 64.586796 | 84.903833 | 72.990008 | 72.580798 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | low_risk_score |

## 风险降级股票摘要

- 风险降级数量: 289
- 这些股票分数靠前，但由于风险、流动性或置信度问题，不应进入主虚拟组合。

| Symbol | Name | Trigger | Score | Downgrade Reason | Risk | Liquidity | Confidence |
|---|---|---|---:|---|---:|---:|---:|
| 688766.SH | 普冉股份 | Mid | 85.670168 | low_risk_score | 28.719699 | 63.176759 | 1.000000 |
| 688519.SH | 南亚新材 | Mid | 84.232687 | low_risk_score | 21.275795 | 62.742633 | 1.000000 |
| 300975.SZ | 商络电子 | Mid | 83.231819 | low_risk_score | 24.171398 | 65.028386 | 1.000000 |
| 300666.SZ | 江丰电子 | Mid | 83.230726 | low_risk_score | 34.160922 | 66.501307 | 1.000000 |
| 301377.SZ | 鼎泰高科 | Mid | 82.979780 | low_risk_score | 32.646211 | 53.497342 | 1.000000 |
| 688545.SH | 兴福电子 | Mid | 82.850344 | low_risk_score | 28.663941 | 63.115031 | 1.000000 |
| 688300.SH | 联瑞新材 | Mid | 82.841610 | low_risk_score | 24.688317 | 64.752411 | 1.000000 |
| 688008.SH | 澜起科技 | Mid | 82.415533 | low_risk_score | 29.308372 | 67.459448 | 1.000000 |
| 301526.SZ | 国际复材 | Mid | 82.030279 | low_risk_score | 24.487249 | 66.113139 | 1.000000 |
| 300475.SZ | 香农芯创 | Mid | 81.757148 | low_risk_score | 26.397562 | 65.351672 | 1.000000 |

## 长期虚拟组合摘要

- holding_count: 30
- weight_sum: 1.000000
- max_single_weight: 3.61%
- max_industry_weight: 25.00%
- 虚拟组合仅用于研究跟踪，不是实盘配置建议。

| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 600999.SH | 招商证券 | 3.61% | 68.595152 | 91.510656 | 77.597098 | Unclassified/SSE_MAIN/600 |
| 2 | 601995.SH | 中金公司 | 3.59% | 66.010918 | 94.293953 | 66.058619 | Unclassified/SSE_MAIN/601 |
| 3 | 688002.SH | 睿创微纳 | 3.54% | 71.072920 | 65.635870 | 58.592863 | Unclassified/STAR/688 |
| 4 | 601066.SH | 中信建投 | 3.52% | 66.819322 | 83.618996 | 73.542399 | Unclassified/SSE_MAIN/601 |
| 5 | 603259.SH | 药明康德 | 3.51% | 69.238700 | 79.651257 | 77.551365 | Unclassified/SSE_MAIN/603 |
| 6 | 688578.SH | 艾力斯 | 3.50% | 66.764039 | 65.136523 | 56.954920 | Unclassified/STAR/688 |
| 7 | 600030.SH | 中信证券 | 3.50% | 64.954834 | 90.064094 | 79.616338 | Unclassified/SSE_MAIN/600 |
| 8 | 601939.SH | 建设银行 | 3.46% | 64.889194 | 95.941020 | 61.159097 | Unclassified/SSE_MAIN/601 |
| 9 | 000333.SZ | 美的集团 | 3.44% | 64.961129 | 94.385082 | 60.494954 | Unclassified/SZSE_MAIN/000 |
| 10 | 688131.SH | 皓元医药 | 3.42% | 64.514924 | 66.750924 | 62.392426 | Unclassified/STAR/688 |

主要风险说明：
- avg RiskScore=71.210887, avg LiquidityScore=65.780552
- min RiskScore=52.035911, min LiquidityScore=44.730107

## 中期虚拟组合摘要

- holding_count: 30
- weight_sum: 0.920000
- max_single_weight: 6.00%
- max_industry_weight: 25.00%
- 虚拟组合仅用于研究跟踪，不是实盘配置建议。

| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 002636.SZ | 金安国纪 | 6.00% | 80.400656 | 40.047085 | 68.234433 | Unclassified/SZSE_MAIN/002 |
| 2 | 301200.SZ | 大族数控 | 6.00% | 82.358878 | 40.069501 | 53.561323 | Unclassified/CHINEXT/301 |
| 3 | 301536.SZ | 星宸科技 | 6.00% | 82.367116 | 59.259034 | 60.396954 | Unclassified/CHINEXT/301 |
| 4 | 600176.SH | 中国巨石 | 6.00% | 82.072794 | 40.674732 | 76.289763 | Unclassified/SSE_MAIN/600 |
| 5 | 600206.SH | 有研新材 | 6.00% | 80.745426 | 48.739412 | 72.108227 | Unclassified/SSE_MAIN/600 |
| 6 | 603663.SH | 三祥新材 | 6.00% | 78.963088 | 50.070965 | 69.430026 | Unclassified/SSE_MAIN/603 |
| 7 | 603823.SH | 百合花 | 6.00% | 78.845394 | 54.864152 | 62.465306 | Unclassified/SSE_MAIN/603 |
| 8 | 688127.SH | 蓝特光学 | 2.56% | 82.619624 | 52.035911 | 62.837141 | Unclassified/STAR/688 |
| 9 | 688669.SH | 聚石化学 | 2.55% | 79.258290 | 62.626048 | 52.603857 | Unclassified/STAR/688 |
| 10 | 688002.SH | 睿创微纳 | 2.55% | 79.419390 | 65.635870 | 58.592863 | Unclassified/STAR/688 |

主要风险说明：
- avg RiskScore=48.551286, avg LiquidityScore=62.319024
- min RiskScore=39.60068, min LiquidityScore=49.329323

## 短期虚拟组合摘要

- holding_count: 20
- weight_sum: 1.000000
- max_single_weight: 5.43%
- max_industry_weight: 25.03%
- 虚拟组合仅用于研究跟踪，不是实盘配置建议。

| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 600999.SH | 招商证券 | 5.43% | 82.713029 | 91.510656 | 77.597098 | Unclassified/SSE_MAIN/600 |
| 2 | 300759.SZ | 康龙化成 | 5.40% | 82.361303 | 69.081283 | 75.809453 | Unclassified/CHINEXT/300 |
| 3 | 603259.SH | 药明康德 | 5.32% | 81.052783 | 79.651257 | 77.551365 | Unclassified/SSE_MAIN/603 |
| 4 | 000783.SZ | 长江证券 | 5.26% | 82.283084 | 73.058146 | 83.837298 | Unclassified/SZSE_MAIN/000 |
| 5 | 300024.SZ | 机器人 | 5.25% | 77.190412 | 54.284153 | 75.964900 | Unclassified/CHINEXT/300 |
| 6 | 603019.SH | 中科曙光 | 5.22% | 78.105545 | 69.792511 | 79.541317 | Unclassified/SSE_MAIN/603 |
| 7 | 000776.SZ | 广发证券 | 5.17% | 76.766784 | 80.933924 | 79.465396 | Unclassified/SZSE_MAIN/000 |
| 8 | 601108.SH | 财通证券 | 5.12% | 79.143202 | 84.878683 | 70.045283 | Unclassified/SSE_MAIN/601 |
| 9 | 601995.SH | 中金公司 | 5.07% | 76.624548 | 94.293953 | 66.058619 | Unclassified/SSE_MAIN/601 |
| 10 | 601162.SH | 天风证券 | 5.05% | 78.445502 | 70.712693 | 77.658827 | Unclassified/SSE_MAIN/601 |

主要风险说明：
- avg RiskScore=68.59814, avg LiquidityScore=69.289183
- min RiskScore=36.042399, min LiquidityScore=53.144544
- 短期组合需要重点观察过热风险、短期波动和流动性变化。

## 行业分布和集中度

- 部分股票原始行业字段为 Unclassified，系统已使用 fallback industry buckets 做集中度校验；后续仍需提升行业分类质量。
- long top industries: Unclassified/CHINEXT/300 25.00%; Unclassified/STAR/688 20.59%; Unclassified/SSE_MAIN/601 17.41%; Unclassified/SSE_MAIN/600 13.66%; Unclassified/SZSE_MAIN/000 13.23%
- long industry concentration warning: false
- mid top industries: Unclassified/STAR/688 25.00%; Unclassified/CHINEXT/300 25.00%; Unclassified/CHINEXT/301 12.00%; Unclassified/SSE_MAIN/600 12.00%; Unclassified/SSE_MAIN/603 12.00%
- mid industry concentration warning: false
- short top industries: Unclassified/CHINEXT/300 25.03%; Unclassified/SSE_MAIN/603 24.97%; Unclassified/SSE_MAIN/601 15.24%; Unclassified/SZSE_MAIN/002 13.96%; Unclassified/SZSE_MAIN/000 10.42%
- short industry concentration warning: false

## 风险与流动性提示

- long avg RiskScore / LiquidityScore: 71.210887 / 65.780552
- long low liquidity notes: 301345.SZ 涛涛车业 LiquidityScore=44.730107, 688059.SH 华锐精密 LiquidityScore=50.262909, 601198.SH 东兴证券 LiquidityScore=53.418829
- long high risk notes: 未触发显著提示。
- mid avg RiskScore / LiquidityScore: 48.551286 / 62.319024
- mid low liquidity notes: 688383.SH 新益昌 LiquidityScore=49.329323, 688059.SH 华锐精密 LiquidityScore=50.262909, 688359.SH 三孚新科 LiquidityScore=51.14986, 688669.SH 聚石化学 LiquidityScore=52.603857, 301200.SZ 大族数控 LiquidityScore=53.561323
- mid high risk notes: 300604.SZ 长川科技 RiskScore=39.60068, 300319.SZ 麦捷科技 RiskScore=39.764463, 002636.SZ 金安国纪 RiskScore=40.047085, 301200.SZ 大族数控 RiskScore=40.069501, 688378.SH 奥来德 RiskScore=40.389632
- short avg RiskScore / LiquidityScore: 68.598140 / 69.289183
- short low liquidity notes: 300873.SZ 海晨股份 LiquidityScore=53.144544, 300434.SZ 金石亚药 LiquidityScore=53.176309
- short high risk notes: 300121.SZ 阳谷华泰 RiskScore=36.042399
- short overheat notes: no_severe_overheat_flag_detected, overheat_risk

## 数据与审计状态

- feature: overall_passed=true, blocking=[], warnings=0
- score: overall_passed=true, blocking=[], warnings=1
- candidate: overall_passed=true, blocking=[], warnings=0
- portfolio: overall_passed=true, blocking=[], warnings=3
- briefing_only: true
- scores_regenerated: false
- candidates_regenerated: false
- virtual_portfolios_regenerated: false
- broker_connected: false
- real_orders_placed: false

## 不要误读

- 候选股不是买入建议。
- 虚拟组合不是实盘组合。
- 目标权重不是下单指令。
- 评分是相对评分，不代表确定盈利。
- 当前还没有真实交易验证。
- 当前没有 broker 连接。
- 当前没有真实订单。

## 下一步跟踪建议

- 下一步应进入虚拟组合跟踪和纸面账本。
- 跟踪每日涨跌、组合收益、回撤、行业暴露变化。
- 比较长期/中期/短期组合与基准指数。
- 持续记录风险降级股票是否改善风险、流动性或置信度状态。

## 明确免责声明

- 本简报仅汇总既有研究 artifacts，面向人工阅读和后续虚拟跟踪。
- 本简报不生成新的评分、候选或虚拟组合。
- 本简报不构成投资建议、收益承诺或实盘操作依据。
