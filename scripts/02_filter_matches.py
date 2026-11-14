"""Stage 2: apply the match filters and write the inclusion/exclusion audit."""
import _bootstrap  # noqa: F401

from batnet import config, ingest, pipeline, tables
from batnet.logutil import get_logger

log = get_logger("02_filter")


def main() -> None:
    audit = pipeline.audit_matches(ingest.iter_match_files(ingest.ensure_extracted()))
    tables.write_csv(audit, config.INTERIM_DIR / "file_audit.csv")
    included = audit[audit["included"]].drop(columns=["included", "exclusion_reason"])
    tables.write_csv(included, config.PROCESSED_DIR / "match_metadata.csv")
    log.info("files audited: %d, included: %d", len(audit), len(included))
    log.info("exclusion reasons:\n%s", audit.loc[~audit["included"], "exclusion_reason"].value_counts().to_string())
    log.info("included by format:\n%s", included["format"].value_counts().reindex(list(config.FORMATS)).to_string())
    log.info("included window: %s .. %s", included["start_date"].min(), included["start_date"].max())
    no_inn = included[included["n_innings_england"] == 0]
    log.info("included matches with no England innings: %d %s", len(no_inn), no_inn["match_id"].tolist())


if __name__ == "__main__":
    main()
