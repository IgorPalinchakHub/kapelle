#!/usr/bin/env python3
from __future__ import annotations

import argparse

from feature_state import FeatureStateError, initialize_feature_state, refresh_feature_status


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build layout-v2 STATUS.md, recovering internal state when required"
    )
    parser.add_argument("feature_dir")
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="Initialize a brand-new feature without recording recovery evidence loss",
    )
    args = parser.parse_args()
    try:
        if args.initialize:
            _, state = initialize_feature_state(args.feature_dir)
            recovered = False
            action = "initialized"
        else:
            _, state, recovered = refresh_feature_status(args.feature_dir)
            action = "recovered and built" if recovered else "built"
    except FeatureStateError as exc:
        print(f"REFUSED: {exc}")
        return 2
    print(
        f"DONE: {action} STATUS.md | state={state['feature_state']} "
        f"| next={state['next_command']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
