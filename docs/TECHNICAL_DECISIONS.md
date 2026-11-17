# Technical decisions

| Decision | Reason | Revisit when |
|---|---|---|
| Treat RL Studio as a Krita-based downstream product | The available project is the full Krita source architecture | Product direction changes explicitly |
| Reuse Krita canvas, document, brush, tablet, layer, and undo systems | Replacing them duplicates mature behavior and adds risk | A measured requirement cannot be met safely |
| Keep internal IDs and user data paths until migration is designed | Settings, plugins, presets, and user data may depend on them | Parallel install and migration behavior are tested |
| Preserve Qt 5/Qt 6 options until build evidence selects a path | Source exposes both paths with different maturity | A supported RL Studio platform matrix is chosen |
| Preserve inherited assets and notices | Source includes GPL and third-party materials under distinct terms | File-level distribution review is complete |
| Require before/after data for performance claims | No source-matched baseline is available and benchmark status is uncertain | Reproducible build/workload exists |

These decisions protect compatibility while recovering the source baseline.
