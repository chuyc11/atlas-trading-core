# Daily Input Freeze Manifest - 2024-12-31

Daily workflow binding is research-only preview infrastructure and does not start forward dry-run.

## Sources
- market_data: exists=true sha256=1a4fb642d99bebea0470b779263a1c0058504af429c26d298369d21f0d2e565a
- benchmark_data: exists=true sha256=9b850b6540c544756947bf0999e84fdcebff7af7d8f2619fd6c5340555da009b
- risk_proxy: exists=true sha256=ea0cf204339df93ed569b603306c74e4e8a04f058f51c7613210edda60a95ada
- baseline_strategy_registry: exists=true sha256=3d3bbe5ed1b4ea19fc8c8e72d1d08d6ab6f7094c9d5178e1d23938b2a43fc580
- baseline_strategy_contract: exists=true sha256=d031724403b6dd162dc6d3b3b5a0c7b245e5ae3857b56da80733db0427a26fd7
- virtual_execution_contract: exists=true sha256=dd6ca83b391eaf41aec09e7ce5e9f4af816db68b8ed2b60fd4fe108333894c36
- trading_calendar_contract: exists=true sha256=ea104fdc22117e21dbdd3f823aea66257bbdba6e8f9b87278c4fa40ad7c2d93d
- price_status_contract: exists=true sha256=d8c443ff41851ee8c1445c64dec3afa790bb3ca1ee578a8086694542d7cc28e8
- lot_position_contract: exists=true sha256=fb27df5c2456c2b1711ce2d92b4ba6b39faba78dbb40bce7f9530b36f572129d
- cost_contract: exists=true sha256=37b5ff259b69c1d65f0f0d0680ecbf39a7d6a2eb2ecd7229320975ca01a9efcd
- data_quality_audit: exists=true sha256=65c042d6755e9518d1cbb4140d3c77753f3c497904324a9ad34ed46dfcc7f350
- daily_market_data_snapshot: exists=true sha256=1f7f94537f5d7dcded752fb5640dec356e1bd8ccca5b620431d470fb743d3528

## Boundary
- daily input freeze manifest only
- run-daily not called
- forward dry-run not started
- main ledger not written
- no real-time market data download
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
