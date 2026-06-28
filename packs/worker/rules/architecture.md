---
code: ARCH-001
title: Keep worker business logic independent from transport infrastructure
label: curated
---

# Keep worker business logic independent from transport infrastructure

Queue, scheduler, and broker SDK types must remain at adapter boundaries. Business decisions belong in
framework-independent handlers and domain services.
