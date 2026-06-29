# A 股全市场 AI 选股研究简报 - 2026-06-26

- as_of_date: 2026-06-26
- generated_at: 2026-06-29T19:30:46.054944Z
- current_version: v0.7.7-a-share-daily-stock-selection-briefing
- input_chain: v0.7.3 features -> v0.7.4 scores -> v0.7.5 candidates -> v0.7.6 virtual portfolios -> v0.7.7 briefing
- data_sources: existing score, candidate, virtual portfolio, exposure, risk/liquidity, and audit artifacts

## 今日总体结论

- strict tradable universe 覆盖 3676 只，评分覆盖 3676 只。
- 长期/中期/短期研究候选数量分别为 30 / 30 / 30，本简报各展示前 10 / 10 / 10 只。
- 多周期共振候选 50 只，本简报展示前 10 只；这只是多周期相对评分靠前。
- 风险降级股票 294 只，说明部分高分股票仍被风险、流动性或置信度约束排除。
- 长期/中期/短期虚拟组合持仓数量为 30 / 30 / 20。
- 主要集中方向：长期 Unclassified/SSE_MAIN/601 (25.00%)，中期 Unclassified/STAR/688 (25.00%)，短期 Unclassified/SSE_MAIN/603 (30.00%)。
- 风险与流动性概览：长期均值 74.63222 / 64.595446，中期均值 50.355533 / 65.591302，短期均值 71.191002 / 66.66283。
- 本阶段只做每日中文信息简报，不重新生成评分、候选股或虚拟组合。

## 数据日期和覆盖状态

- strict tradable universe: 3676
- scored symbols: 3676
- candidate version: v0.7.5-a-share-candidate-generation-system
- score version: v0.7.4-a-share-long-mid-short-scoring-system
- feature version: v0.7.3-a-share-multi-horizon-feature-engineering
- portfolio version: v0.7.6-a-share-virtual-portfolio-construction
- source_trace_complete: true

## 长期研究候选 Top 10

| Rank | Symbol | Name | Industry | LongScore | LongRank | Risk | Liquidity | FundamentalScore | Composite | Inclusion | Risk Notes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 688002.SH | 睿创微纳 | Unclassified | 70.446463 | 1 | 61.811299 | 59.092424 | 69.594602 | 71.920580 | high_long_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 2 | 603259.SH | 药明康德 | Unclassified | 70.019217 | 2 | 79.417732 | 75.686775 | 70.826523 | 75.246618 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 3 | 688127.SH | 蓝特光学 | Unclassified | 69.482802 | 3 | 48.501655 | 62.993743 | 66.358771 | 73.753618 | high_long_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score | no_major_risk_flag_detected |
| 4 | 600999.SH | 招商证券 | Unclassified | 69.234704 | 4 | 94.734086 | 76.699311 | 68.275705 | 76.924652 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 5 | 603268.SH | 松发股份 | Unclassified | 68.721783 | 5 | 62.417596 | 61.142320 | 67.080885 | 68.977251 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 6 | 601066.SH | 中信建投 | Unclassified | 68.610117 | 6 | 82.991136 | 72.999637 | 71.541295 | 75.340861 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 7 | 600909.SH | 华安证券 | Unclassified | 68.266169 | 7 | 71.922493 | 80.629307 | 58.753271 | 76.936048 | high_long_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 8 | 300308.SZ | 中际旭创 | Unclassified | 67.746109 | 8 | 51.972026 | 71.185618 | 67.043566 | 71.421820 | high_long_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 9 | 600160.SH | 巨化股份 | Unclassified | 67.582925 | 9 | 61.303273 | 78.640959 | 65.592372 | 71.828795 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 10 | 601939.SH | 建设银行 | Unclassified | 67.109371 | 10 | 96.629149 | 61.003808 | 64.420099 | 67.453101 | high_long_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |

## 中期研究候选 Top 10

| Rank | Symbol | Name | Industry | MidScore | MidRank | Risk | Liquidity | IndustryScore | Composite | Inclusion | Risk Notes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 300408.SZ | 三环集团 | Unclassified | 84.120716 | 5 | 42.183079 | 76.653292 | 69.531148 | 71.705109 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 2 | 600183.SH | 生益科技 | Unclassified | 84.119404 | 6 | 45.096799 | 77.851152 | 60.998481 | 71.088467 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 3 | 688059.SH | 华锐精密 | Unclassified | 83.624883 | 8 | 50.900549 | 49.406964 | 83.981581 | 69.205613 | high_mid_percentile, strong_composite_percentile, strong_industry_score, acceptable_risk_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 4 | 600176.SH | 中国巨石 | Unclassified | 83.543432 | 9 | 41.061389 | 76.640823 | 61.442805 | 73.053616 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 5 | 300308.SZ | 中际旭创 | Unclassified | 83.523479 | 10 | 51.972026 | 71.185618 | 68.034956 | 71.421820 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 6 | 688127.SH | 蓝特光学 | Unclassified | 83.040462 | 13 | 48.501655 | 62.993743 | 82.559746 | 73.753618 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_fundamental_score, strong_trend_component | no_major_risk_flag_detected |
| 7 | 600206.SH | 有研新材 | Unclassified | 81.846066 | 21 | 47.928341 | 71.868653 | 61.328550 | 71.939656 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, strong_trend_component | no_major_risk_flag_detected |
| 8 | 301536.SZ | 星宸科技 | Unclassified | 81.727546 | 24 | 55.477534 | 60.652657 | 68.954434 | 71.635845 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 9 | 688383.SH | 新益昌 | Unclassified | 81.105906 | 31 | 49.944120 | 50.039218 | 84.629024 | 66.840433 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_trend_component | no_major_risk_flag_detected |
| 10 | 300201.SZ | 海伦哲 | Unclassified | 80.670654 | 39 | 59.490615 | 63.175440 | 66.380985 | 68.334747 | high_mid_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_trend_component | no_major_risk_flag_detected |

## 短期研究候选 Top 10

| Rank | Symbol | Name | Industry | ShortScore | ShortRank | Risk | Liquidity | IndustryScore | Composite | Inclusion | Risk Notes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 600909.SH | 华安证券 | Unclassified | 83.987027 | 1 | 71.922493 | 80.629307 | 60.813497 | 76.936048 | high_short_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | overheat_risk |
| 2 | 601066.SH | 中信建投 | Unclassified | 83.572843 | 2 | 82.991136 | 72.999637 | 59.003559 | 75.340861 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | overheat_risk |
| 3 | 600999.SH | 招商证券 | Unclassified | 81.992037 | 3 | 94.734086 | 76.699311 | 58.981796 | 76.924652 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |
| 4 | 603019.SH | 中科曙光 | Unclassified | 81.847882 | 4 | 68.114119 | 79.758342 | 58.087709 | 70.393616 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_momentum_component | no_major_risk_flag_detected |
| 5 | 300759.SZ | 康龙化成 | Unclassified | 81.290077 | 5 | 72.317963 | 73.143589 | 62.806447 | 67.202181 | high_short_percentile, strong_composite_percentile, strong_industry_score, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score | no_major_risk_flag_detected |
| 6 | 601995.SH | 中金公司 | Unclassified | 80.227529 | 7 | 94.496622 | 64.392456 | 56.954230 | 72.197890 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |
| 7 | 002668.SZ | TCL智家 | Unclassified | 79.727944 | 10 | 89.774211 | 51.832041 | 33.396049 | 67.175776 | high_short_percentile, strong_composite_percentile, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |
| 8 | 603259.SH | 药明康德 | Unclassified | 79.375170 | 11 | 79.417732 | 75.686775 | 58.891118 | 75.246618 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |
| 9 | 603010.SH | 万盛股份 | Unclassified | 79.288102 | 13 | 67.322384 | 61.781375 | 59.393476 | 69.975122 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_momentum_component | overheat_risk |
| 10 | 601108.SH | 财通证券 | Unclassified | 78.968404 | 17 | 86.074991 | 67.951578 | 57.041281 | 69.732831 | high_short_percentile, strong_composite_percentile, strong_liquidity_score, acceptable_risk_score, strong_fundamental_score, strong_momentum_component | no_major_risk_flag_detected |

## 多周期共振候选

多周期共振只是多周期评分靠前，不代表确定上涨；这里用于后续研究跟踪排序。

| Symbol | Name | Overlap | Best Horizon | Long | Mid | Short | Composite | Strengths | Risk Notes |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 600909.SH | 华安证券 | Long+Mid+Short | Short | 68.266169 | 79.519573 | 83.987027 | 76.936048 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 600999.SH | 招商证券 | Long+Mid+Short | Short | 69.234704 | 77.384462 | 81.992037 | 76.924652 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 601066.SH | 中信建投 | Long+Mid+Short | Short | 68.610117 | 74.471648 | 83.572843 | 75.340861 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 603259.SH | 药明康德 | Long+Mid+Short | Long | 70.019217 | 76.119530 | 79.375170 | 75.246618 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 688127.SH | 蓝特光学 | Long+Mid+Short | Long | 69.482802 | 83.040462 | 73.079384 | 73.753618 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 600176.SH | 中国巨石 | Long+Mid+Short | Mid | 65.022532 | 83.543432 | 73.686179 | 73.053616 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 600888.SH | 新疆众和 | Long+Mid+Short | Long | 65.187484 | 78.917021 | 76.821199 | 72.914472 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 300604.SZ | 长川科技 | Long+Mid+Short | Mid | 63.823762 | 84.081548 | 76.389835 | 72.877790 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | low_risk_score |
| 601995.SH | 中金公司 | Long+Mid+Short | Short | 66.762715 | 69.050683 | 80.227529 | 72.197890 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | no_major_risk_flag_detected |
| 300398.SZ | 飞凯材料 | Long+Mid+Short | Short | 62.794694 | 80.813617 | 78.523438 | 72.025286 | multi_horizon_overlap, high_long_percentile, high_mid_percentile, high_short_percentile | low_risk_score |

## 风险降级股票摘要

- 风险降级数量: 294
- 这些股票分数靠前，但由于风险、流动性或置信度问题，不应进入主虚拟组合。

| Symbol | Name | Trigger | Score | Downgrade Reason | Risk | Liquidity | Confidence |
|---|---|---|---:|---|---:|---:|---:|
| 688766.SH | 普冉股份 | Mid | 85.477234 | low_risk_score | 28.660455 | 62.884022 | 1.000000 |
| 688519.SH | 南亚新材 | Mid | 84.901538 | low_risk_score | 21.651818 | 62.710940 | 1.000000 |
| 688300.SH | 联瑞新材 | Mid | 84.258446 | low_risk_score | 26.272556 | 64.763783 | 1.000000 |
| 603256.SH | 宏和科技 | Mid | 83.046572 | low_risk_score | 32.619129 | 67.454207 | 1.000000 |
| 688456.SH | 有研粉材 | Mid | 82.561426 | low_risk_score | 28.130214 | 58.647080 | 1.000000 |
| 688525.SH | 佰维存储 | Mid | 82.412413 | low_risk_score | 28.497461 | 61.498458 | 1.000000 |
| 688308.SH | 欧科亿 | Mid | 82.260482 | low_risk_score | 21.065696 | 52.494786 | 1.000000 |
| 688072.SH | 拓荆科技 | Mid | 82.114831 | low_risk_score | 34.985151 | 67.773622 | 1.000000 |
| 300666.SZ | 江丰电子 | Mid | 82.087042 | low_risk_score | 32.784843 | 66.879987 | 1.000000 |
| 688545.SH | 兴福电子 | Mid | 82.001296 | low_risk_score | 28.395675 | 63.314291 | 1.000000 |

## 长期虚拟组合摘要

- holding_count: 30
- weight_sum: 1.000000
- max_single_weight: 3.71%
- max_industry_weight: 25.00%
- 虚拟组合仅用于研究跟踪，不是实盘配置建议。

| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 600999.SH | 招商证券 | 3.71% | 69.234704 | 94.734086 | 76.699311 | Unclassified/SSE_MAIN/600 |
| 2 | 600900.SH | 长江电力 | 3.67% | 65.993253 | 97.323177 | 64.698721 | Unclassified/SSE_MAIN/600 |
| 3 | 688578.SH | 艾力斯 | 3.64% | 66.379209 | 82.480391 | 49.093217 | Unclassified/STAR/688 |
| 4 | 600030.SH | 中信证券 | 3.59% | 65.772783 | 90.521853 | 79.107952 | Unclassified/SSE_MAIN/600 |
| 5 | 603259.SH | 药明康德 | 3.59% | 70.019217 | 79.417732 | 75.686775 | Unclassified/SSE_MAIN/603 |
| 6 | 688002.SH | 睿创微纳 | 3.53% | 70.446463 | 61.811299 | 59.092424 | Unclassified/STAR/688 |
| 7 | 300750.SZ | 宁德时代 | 3.47% | 66.751559 | 78.571590 | 63.745806 | Unclassified/CHINEXT/300 |
| 8 | 300031.SZ | 宝通科技 | 3.46% | 65.501032 | 72.770335 | 59.862396 | Unclassified/CHINEXT/300 |
| 9 | 000333.SZ | 美的集团 | 3.44% | 65.093132 | 93.996985 | 60.188157 | Unclassified/SZSE_MAIN/000 |
| 10 | 688059.SH | 华锐精密 | 3.39% | 66.788714 | 50.900549 | 49.406964 | Unclassified/STAR/688 |

主要风险说明：
- avg RiskScore=74.63222, avg LiquidityScore=64.595446
- min RiskScore=45.096799, min LiquidityScore=44.601696

## 中期虚拟组合摘要

- holding_count: 30
- weight_sum: 1.000000
- max_single_weight: 3.70%
- max_industry_weight: 25.00%
- 虚拟组合仅用于研究跟踪，不是实盘配置建议。

| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 600909.SH | 华安证券 | 3.70% | 79.519573 | 71.922493 | 80.629307 | Unclassified/SSE_MAIN/600 |
| 2 | 300408.SZ | 三环集团 | 3.57% | 84.120716 | 42.183079 | 76.653292 | Unclassified/CHINEXT/300 |
| 3 | 300308.SZ | 中际旭创 | 3.55% | 83.523479 | 51.972026 | 71.185618 | Unclassified/CHINEXT/300 |
| 4 | 600226.SH | 亨通股份 | 3.51% | 80.554750 | 57.285149 | 74.394496 | Unclassified/SSE_MAIN/600 |
| 5 | 600888.SH | 新疆众和 | 3.48% | 78.917021 | 59.170634 | 71.468761 | Unclassified/SSE_MAIN/600 |
| 6 | 600183.SH | 生益科技 | 3.48% | 84.119404 | 45.096799 | 77.851152 | Unclassified/SSE_MAIN/600 |
| 7 | 301536.SZ | 星宸科技 | 3.47% | 81.727546 | 55.477534 | 60.652657 | Unclassified/CHINEXT/301 |
| 8 | 300005.SZ | 探路者 | 3.47% | 78.714437 | 45.899642 | 68.263171 | Unclassified/CHINEXT/300 |
| 9 | 600176.SH | 中国巨石 | 3.46% | 83.543432 | 41.061389 | 76.640823 | Unclassified/SSE_MAIN/600 |
| 10 | 300201.SZ | 海伦哲 | 3.46% | 80.670654 | 59.490615 | 63.175440 | Unclassified/CHINEXT/300 |

主要风险说明：
- avg RiskScore=50.355533, avg LiquidityScore=65.591302
- min RiskScore=40.001247, min LiquidityScore=49.252811

## 短期虚拟组合摘要

- holding_count: 20
- weight_sum: 1.000000
- max_single_weight: 5.58%
- max_industry_weight: 30.00%
- 虚拟组合仅用于研究跟踪，不是实盘配置建议。

| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | 600999.SH | 招商证券 | 5.58% | 81.992037 | 94.734086 | 76.699311 | Unclassified/SSE_MAIN/600 |
| 2 | 600909.SH | 华安证券 | 5.54% | 83.987027 | 71.922493 | 80.629307 | Unclassified/SSE_MAIN/600 |
| 3 | 601066.SH | 中信建投 | 5.40% | 83.572843 | 82.991136 | 72.999637 | Unclassified/SSE_MAIN/601 |
| 4 | 603259.SH | 药明康德 | 5.40% | 79.375170 | 79.417732 | 75.686775 | Unclassified/SSE_MAIN/603 |
| 5 | 603019.SH | 中科曙光 | 5.36% | 81.847882 | 68.114119 | 79.758342 | Unclassified/SSE_MAIN/603 |
| 6 | 300759.SZ | 康龙化成 | 5.30% | 81.290077 | 72.317963 | 73.143589 | Unclassified/CHINEXT/300 |
| 7 | 601995.SH | 中金公司 | 5.22% | 80.227529 | 94.496622 | 64.392456 | Unclassified/SSE_MAIN/601 |
| 8 | 601108.SH | 财通证券 | 5.21% | 78.968404 | 86.074991 | 67.951578 | Unclassified/SSE_MAIN/601 |
| 9 | 600516.SH | XD方大炭 | 5.20% | 77.633263 | 64.862396 | 75.155967 | Unclassified/SSE_MAIN/600 |
| 10 | 603010.SH | 万盛股份 | 4.95% | 79.288102 | 67.322384 | 61.781375 | Unclassified/SSE_MAIN/603 |

主要风险说明：
- avg RiskScore=71.191002, avg LiquidityScore=66.66283
- min RiskScore=44.893566, min LiquidityScore=51.832041
- 短期组合需要重点观察过热风险、短期波动和流动性变化。

## 行业分布和集中度

- 部分股票原始行业字段为 Unclassified，系统已使用 fallback industry buckets 做集中度校验；后续仍需提升行业分类质量。
- long top industries: Unclassified/SSE_MAIN/601 25.00%; Unclassified/SSE_MAIN/600 24.00%; Unclassified/STAR/688 13.95%; Unclassified/CHINEXT/300 13.55%; Unclassified/SSE_MAIN/603 13.45%
- long industry concentration warning: false
- mid top industries: Unclassified/STAR/688 25.00%; Unclassified/SSE_MAIN/600 24.44%; Unclassified/SSE_MAIN/603 23.37%; Unclassified/CHINEXT/300 17.45%; Unclassified/CHINEXT/301 3.47%
- mid industry concentration warning: false
- short top industries: Unclassified/SSE_MAIN/603 30.00%; Unclassified/SSE_MAIN/600 21.14%; Unclassified/SSE_MAIN/601 15.83%; Unclassified/SZSE_MAIN/002 13.76%; Unclassified/CHINEXT/300 9.99%
- short industry concentration warning: false

## 风险与流动性提示

- long avg RiskScore / LiquidityScore: 74.632220 / 64.595446
- long low liquidity notes: 301345.SZ 涛涛车业 LiquidityScore=44.601696, 688578.SH 艾力斯 LiquidityScore=49.093217, 688059.SH 华锐精密 LiquidityScore=49.406964, 601198.SH 东兴证券 LiquidityScore=51.706565, 603156.SH 养元饮品 LiquidityScore=54.477466
- long high risk notes: 600183.SH 生益科技 RiskScore=45.096799, 688127.SH 蓝特光学 RiskScore=48.501655
- mid avg RiskScore / LiquidityScore: 50.355533 / 65.591302
- mid low liquidity notes: 688359.SH 三孚新科 LiquidityScore=49.252811, 688059.SH 华锐精密 LiquidityScore=49.406964, 688383.SH 新益昌 LiquidityScore=50.039218, 688669.SH 聚石化学 LiquidityScore=51.582789, 603125.SH 常青科技 LiquidityScore=51.616907
- mid high risk notes: 002636.SZ 金安国纪 RiskScore=40.001247, 603650.SH 彤程新材 RiskScore=40.91415, 600176.SH 中国巨石 RiskScore=41.061389, 600378.SH 昊华科技 RiskScore=41.819913, 300408.SZ 三环集团 RiskScore=42.183079
- short avg RiskScore / LiquidityScore: 71.191002 / 66.662830
- short low liquidity notes: 002668.SZ TCL智家 LiquidityScore=51.832041, 603713.SH 密尔克卫 LiquidityScore=54.680586
- short high risk notes: 603690.SH 至纯科技 RiskScore=44.893566, 300200.SZ 高盟新材 RiskScore=47.979008, 600877.SH 电科芯片 RiskScore=48.807354
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
