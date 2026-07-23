#!/usr/bin/env python3
from __future__ import annotations

import argparse

from feature_state import FeatureStateError, rebuild_feature_state


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild layout-v2 internal state from durable human artifacts"
    )
    parser.add_argument("feature_dir")
    args = parser.parse_args()
    try:
        _, state, report = rebuild_feature_state(args.feature_dir)
    except FeatureStateError as exc:
        print(f"REFUSED: {exc}")
        return 2
    print(
        f"DONE: {report['status']} | tasks={len(report['task_dispositions'])} "
        f"| next={state['next_command']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

