"""Stage 3: extract partnership observations from every included match."""
import _bootstrap  # noqa: F401

from batnet import config, ingest, pipeline, tables
from batnet.logutil import get_logger

log = get_logger("03_extract")


def main() -> None:
    ingest.ensure_extracted()
    included = tables.read_csv(config.PROCESSED_DIR / "match_metadata.csv")
    obs, innings, warnings = pipeline.extract_all(included)
    tables.write_csv(obs, config.PROCESSED_DIR / "partnership_observations.csv")
    tables.write_csv(innings, config.PROCESSED_DIR / "innings_summary.csv")
    tables.write_csv(warnings, config.PROCESSED_DIR / "extraction_warnings.csv")
    log.info("matches: %d, England innings: %d (qualifying %d), observations: %d, warnings: %d",
             len(included), len(innings), int(innings["qualifying"].sum()), len(obs), len(warnings))
    log.info("observations by format:\n%s", obs["format"].value_counts().reindex(list(config.FORMATS)).to_string())
    log.info("boundary reasons:\n%s", obs["boundary_reason"].value_counts().to_string())
    for w in warnings.to_dict("records"):
        log.warning("extraction warning: %s", w)


if __name__ == "__main__":
    main()
