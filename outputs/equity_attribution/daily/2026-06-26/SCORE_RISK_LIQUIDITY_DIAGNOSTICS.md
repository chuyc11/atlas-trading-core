# Score Risk Liquidity Diagnostics

## Score Bucket Exposure
### long_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.000000 | 0 | not_applicable |
| 60-80 | 1.000000 | 30 | insufficient_history |
| 80-100 | 0.000000 | 0 | not_applicable |

### mid_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.000000 | 0 | not_applicable |
| 60-80 | 1.000000 | 30 | insufficient_history |
| 80-100 | 0.000000 | 0 | not_applicable |

### short_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.000000 | 0 | not_applicable |
| 60-80 | 1.000000 | 20 | insufficient_history |
| 80-100 | 0.000000 | 0 | not_applicable |

## Risk Bucket Exposure
### long_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.196506 | 6 | insufficient_history |
| 60-80 | 0.372925 | 11 | insufficient_history |
| 80-100 | 0.430568 | 13 | insufficient_history |

### mid_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.866469 | 26 | insufficient_history |
| 60-80 | 0.133531 | 4 | insufficient_history |
| 80-100 | 0.000000 | 0 | not_applicable |

### short_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.236182 | 5 | insufficient_history |
| 60-80 | 0.410410 | 8 | insufficient_history |
| 80-100 | 0.353408 | 7 | insufficient_history |

## Liquidity Bucket Exposure
### long_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.270093 | 8 | insufficient_history |
| 60-80 | 0.696077 | 21 | insufficient_history |
| 80-100 | 0.033829 | 1 | insufficient_history |

### mid_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.219072 | 7 | insufficient_history |
| 60-80 | 0.743947 | 22 | insufficient_history |
| 80-100 | 0.036981 | 1 | insufficient_history |

### short_virtual_portfolio
| Bucket | Weight | Count | Status |
|---|---:|---:|---|
| 0-20 | 0.000000 | 0 | not_applicable |
| 20-40 | 0.000000 | 0 | not_applicable |
| 40-60 | 0.232089 | 5 | insufficient_history |
| 60-80 | 0.712493 | 14 | insufficient_history |
| 80-100 | 0.055418 | 1 | insufficient_history |

## Weighted Average Scores
- long_virtual_portfolio: {'CompositeOpportunityScore': 69.62040987832962, 'LongScore': 66.74571761766903, 'MidScore': 72.10322728986498, 'ShortScore': 69.5841818078028, 'RiskScore': 74.67428204756652, 'LiquidityScore': 64.61611078807985, 'IndustryScore': 61.4641048004566, 'FundamentalScore': 65.79523899905794}
- mid_virtual_portfolio: {'CompositeOpportunityScore': 70.3160084917874, 'LongScore': 62.77079437728484, 'MidScore': 80.45012277444646, 'ShortScore': 70.03203711953189, 'RiskScore': 50.44508458600029, 'LiquidityScore': 65.93927526094768, 'IndustryScore': 67.46553619000456, 'FundamentalScore': 55.840330067657085}
- short_virtual_portfolio: {'CompositeOpportunityScore': 68.68957294745942, 'LongScore': 60.0431303416266, 'MidScore': 68.08895340940829, 'ShortScore': 79.62569537730658, 'RiskScore': 71.62475685205135, 'LiquidityScore': 67.1567718692914, 'IndustryScore': 53.31891839447028, 'FundamentalScore': 55.939235630030076}

## Diagnostic Flags
- long_virtual_portfolio: {'concentrated_top5': False, 'concentrated_industry': True, 'contains_risk_downgraded': False, 'contains_excluded_universe': False, 'low_liquidity_cluster': False, 'unclassified_industry_high': True}
- mid_virtual_portfolio: {'concentrated_top5': False, 'concentrated_industry': True, 'contains_risk_downgraded': False, 'contains_excluded_universe': False, 'low_liquidity_cluster': False, 'unclassified_industry_high': True}
- short_virtual_portfolio: {'concentrated_top5': False, 'concentrated_industry': True, 'contains_risk_downgraded': False, 'contains_excluded_universe': False, 'low_liquidity_cluster': False, 'unclassified_industry_high': True}

- risk downgrade exposure: 0
- low liquidity exposure: {'long_virtual_portfolio': {'low_liquidity_exposure': 0.0, 'high_liquidity_exposure': 0.03382932129999999, 'weighted_average_liquidity_score': 64.61611078807985, 'minimum_liquidity_score_holding': {'symbol': '301345.SZ', 'score': 44.601696, 'weight': 0.0335893579}, 'top_illiquidity_contributors': [{'symbol': '301345.SZ', 'liquidity_score': 44.601696, 'weight': 0.0335893579}, {'symbol': '688578.SH', 'liquidity_score': 49.093217, 'weight': 0.0363932815}, {'symbol': '688059.SH', 'liquidity_score': 49.406964, 'weight': 0.0338981217}, {'symbol': '601198.SH', 'liquidity_score': 51.706565, 'weight': 0.0307364759}, {'symbol': '603156.SH', 'liquidity_score': 54.477466, 'weight': 0.0324628564}]}, 'mid_virtual_portfolio': {'low_liquidity_exposure': 0.0, 'high_liquidity_exposure': 0.036981015, 'weighted_average_liquidity_score': 65.93927526094768, 'minimum_liquidity_score_holding': {'symbol': '688359.SH', 'score': 49.252811, 'weight': 0.030305141100000002}, 'top_illiquidity_contributors': [{'symbol': '688359.SH', 'liquidity_score': 49.252811, 'weight': 0.030305141100000002}, {'symbol': '688059.SH', 'liquidity_score': 49.406964, 'weight': 0.0306841481}, {'symbol': '688383.SH', 'liquidity_score': 50.039218, 'weight': 0.0305587731}, {'symbol': '688669.SH', 'liquidity_score': 51.582789, 'weight': 0.031779591}, {'symbol': '603125.SH', 'liquidity_score': 51.616907, 'weight': 0.033071297}]}, 'short_virtual_portfolio': {'low_liquidity_exposure': 0.0, 'high_liquidity_exposure': 0.0554175282, 'weighted_average_liquidity_score': 67.1567718692914, 'minimum_liquidity_score_holding': {'symbol': '002668.SZ', 'score': 51.832041, 'weight': 0.0451820468}, 'top_illiquidity_contributors': [{'symbol': '002668.SZ', 'liquidity_score': 51.832041, 'weight': 0.0451820468}, {'symbol': '603713.SH', 'liquidity_score': 54.680586, 'weight': 0.0471423606}, {'symbol': '300200.SZ', 'liquidity_score': 55.404198, 'weight': 0.0468864853}, {'symbol': '002559.SZ', 'liquidity_score': 58.681311, 'weight': 0.0450562666}, {'symbol': '603341.SH', 'liquidity_score': 59.824991, 'weight': 0.0478218891}]}}
