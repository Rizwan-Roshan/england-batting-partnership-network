"""Stage 1: extract the archive (if needed) and write the source manifest."""
import _bootstrap  # noqa: F401
import json
from datetime import datetime, timezone

from batnet import config, ingest
from batnet.logutil import get_logger

log = get_logger("01_manifest")


def main() -> None:
    json_dir = ingest.ensure_extracted()
    manifest = ingest.build_manifest(json_dir)
    manifest.to_csv(config.INTERIM_DIR / "source_manifest.csv", index=False)
    zip_stat = config.RAW_ZIP.stat()
    summary = {
        "source_url": config.SOURCE_URL,
        "archive": config.RAW_ZIP.name,
        "archive_bytes": zip_stat.st_size,
        "archive_sha256": ingest.sha256_of(config.RAW_ZIP),
        # The download date was not recorded; the file timestamp is the best evidence.
        "archive_file_modified_utc": datetime.fromtimestamp(zip_stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
        "json_files": int(len(manifest)),
        "unreadable_files": int((~manifest["readable"]).sum()),
        "data_versions": manifest["data_version"].value_counts().to_dict(),
        "other_files": sorted(p.name for p in json_dir.iterdir() if p.suffix != ".json"),
    }
    (config.INTERIM_DIR / "source_summary.json").write_text(json.dumps(summary, indent=2))
    log.info("manifest: %s", summary)


if __name__ == "__main__":
    main()
