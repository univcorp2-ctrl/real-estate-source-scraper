# Inventory Notes

The first source inventory contains 100+ real estate and real estate investment websites across Japanese residential portals, investment property portals, commercial real estate, public auction/public sale data, market data, REIT information, and major international listing portals.

`data/sources.yml` is the main inventory file. `data/sources.extra.yml` is automatically merged by the loader for incremental expansion without rewriting the large base file.

The inventory is intentionally conservative: most commercial portals are marked `needs_review`, while public-sector sources and pilot-friendly sources are separated for low-load auditing first.
