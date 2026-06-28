---
code: ARCH-001
title: Keep domain code independent from frameworks
label: curated
---

# Keep domain code independent from frameworks

Domain entities, aggregates, and value objects must not depend on framework or transport SDK types.
Translate those types at adapter boundaries.
