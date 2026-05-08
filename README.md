# Portolan

**Publish geospatial data without the portal.**

Portolan is an open-source toolkit for publishing geospatial data as cloud-native files on object storage. It combines [STAC](https://stacspec.org/), [GeoParquet](https://geoparquet.org/), and [Cloud-Optimized GeoTIFF](https://www.cogeo.org/) to let governments and open data publishers share spatial datasets at minimal cost — no servers, databases, or proprietary licenses required.

## Why Portolan

- **Open** — 100% open source (Apache-2.0), open formats, and open governance. Your data stays portable.
- **Cost-effective** — Only pay for storage and egress. Small catalogs run for dollars a month.
- **Sovereign** — Data lives in your buckets on AWS, GCS, Azure, MinIO, or any S3-compatible storage.
- **Scalable** — Cloud-native formats serve range requests over petabyte-scale datasets. P95 latency under 120 ms globally.
- **AI-ready** — STAC metadata is structured for retrieval and queryable by LLM agents.
- **Tool-agnostic** — Query with DuckDB, Snowflake, BigQuery, Databricks, or Pandas — not just GIS tools.

## How It Works

Portolan converts local geospatial files (Shapefiles, GeoTIFFs, etc.) into cloud-native formats, validates them, and syncs the results to object storage as a STAC catalog:

```
portolan ingest ./gov-data --to s3://my-catalog
```

The resulting catalog is browsable via standard URLs and queryable from any analytical tool that speaks Parquet or COG.

## Repositories

### Core

| Repository | Description | Language |
|---|---|---|
| [portolan](https://github.com/portolan-sdi/portolan) | Core tools for cloud-native geospatial SDI | TypeScript |
| [portolan-cli](https://github.com/portolan-sdi/portolan-cli) | CLI for converting, validating, and syncing geospatial data to S3 catalogs | Python |
| [portolan-spec](https://github.com/portolan-sdi/portolan-spec) | Spec and best practices for Portolan SDI | — |

### Extensions

| Repository | Description |
|---|---|
| [stac-iceberg-extension](https://github.com/portolan-sdi/stac-iceberg-extension) | STAC extension for Apache Iceberg table access and versioning metadata |
| [stac-partition-extension](https://github.com/portolan-sdi/stac-partition-extension) | STAC extension for partitioned datasets |
| [portolake](https://github.com/portolan-sdi/portolake) | Lakehouse-grade versioning for Portolan catalogs (Python) |

### Applications

| Repository | Description | Language |
|---|---|---|
| [portolan-browser](https://github.com/portolan-sdi/portolan-browser) | UI for browsing and searching static STAC catalogs and STAC APIs | JavaScript |
| [portolan-nl-demo](https://github.com/portolan-sdi/portolan-nl-demo) | Demo catalog browser for Netherlands data | JavaScript |

### Tooling

| Repository | Description |
|---|---|
| [portolan-skills](https://github.com/portolan-sdi/portolan-skills) | Claude Code skills for working with Portolan catalogs |
| [portolan-bootstrapper](https://github.com/portolan-sdi/portolan-bootstrapper) | Bootstrapping core open data for local use |

## Learn More

Visit [portolan-one.vercel.app](https://portolan-one.vercel.app/) for the full overview, architecture details, and getting started guide.

## License

[Apache 2.0](LICENSE)
