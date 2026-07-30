"""Replication entry point. Keep the original paper's pipeline stages
explicit so differences can be isolated stage by stage."""
from __future__ import annotations


def load_data() -> None:
    """Load the dataset described in data/README.md."""
    raise NotImplementedError


def run_pipeline() -> None:
    """Re-run the paper's pipeline. Log seeds, versions, and config."""
    raise NotImplementedError


def main() -> None:
    load_data()
    run_pipeline()


if __name__ == "__main__":
    main()
