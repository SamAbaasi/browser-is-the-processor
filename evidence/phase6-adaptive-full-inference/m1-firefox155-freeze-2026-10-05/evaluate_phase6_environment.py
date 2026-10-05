#!/usr/bin/env python3

import argparse
import json
import math
import statistics
from pathlib import Path


WORKLOADS = [
    "p32",
    "p64",
    "p128",
    "p256",
    "decode64",
]

KERNELS = [
    "generic",
    "dot",
    "pairwise",
]

GATE = 1.05


def load(path):
    return json.loads(Path(path).read_text())


def static_samples(session, kernel, workload):
    variant = next(
        x for x in session["variants"]
        if x["kernel_key"] == kernel
    )

    record = next(
        x for x in variant["workloads"]
        if x["workload"] == workload
    )

    return [
        x["wall_ms"]
        for x in record["samples"]
    ]


def geo_mean(xs):
    return math.exp(
        sum(math.log(x) for x in xs)
        / len(xs)
    )


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--static1", required=True)
    ap.add_argument("--static2", required=True)
    ap.add_argument("--adaptive1", required=True)
    ap.add_argument("--adaptive2", required=True)
    ap.add_argument("--out", required=True)

    args = ap.parse_args()

    s1 = load(args.static1)
    s2 = load(args.static2)

    adaptive = [
        load(args.adaptive1),
        load(args.adaptive2),
    ]

    canonical = {}

    for kernel in KERNELS:
        canonical[kernel] = {}

        for workload in WORKLOADS:
            samples = (
                static_samples(
                    s1,
                    kernel,
                    workload
                )
                +
                static_samples(
                    s2,
                    kernel,
                    workload
                )
            )

            assert len(samples) == 6

            canonical[kernel][workload] = {
                "samples_ms": samples,
                "median_ms":
                    statistics.median(samples)
            }

    oracle = {}

    for workload in WORKLOADS:
        ranking = sorted(
            KERNELS,
            key=lambda k:
                canonical[k][workload]
                ["median_ms"]
        )

        best = ranking[0]

        oracle[workload] = {
            "best_kernel": best,
            "best_ms":
                canonical[best][workload]
                ["median_ms"],
            "ranking": ranking
        }

    adaptive_results = []

    for session in adaptive:
        selected = (
            session["selector"]
            ["selector"]
            ["selected_variant"]
        )

        regrets = {}

        for workload in WORKLOADS:
            selected_ms = (
                canonical[selected]
                [workload]
                ["median_ms"]
            )

            best_ms = (
                oracle[workload]
                ["best_ms"]
            )

            regrets[workload] = (
                selected_ms / best_ms
            )

        gm = geo_mean(
            list(regrets.values())
        )

        adaptive_results.append({
            "session_index":
                session["session_index"],

            "selected_kernel":
                selected,

            "selector_wall_ms":
                session["selector"]
                ["selector"]
                ["selector_wall_ms"],

            "selector_decision_mode":
                session["selector"]
                ["selector"]
                ["decision_mode"],

            "regret_by_workload":
                regrets,

            "environment_gm_regret":
                gm,

            "gate":
                GATE,

            "pass":
                gm <= GATE
        })

    environment_pass = all(
        x["pass"]
        for x in adaptive_results
    )

    result = {
        "schema":
            "p1-phase6-environment-evaluation-v1",

        "static_aggregation":
            "median of 6 retained samples "
            "(3 per static session), "
            "no outlier removal",

        "regret_definition":
            "canonical static time of selected "
            "kernel / best canonical static time",

        "gate":
            GATE,

        "canonical_static":
            canonical,

        "oracle":
            oracle,

        "adaptive_sessions":
            adaptive_results,

        "environment_pass":
            environment_pass
    }

    out = Path(args.out)
    out.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    out.write_text(
        json.dumps(
            result,
            indent=2
        )
        + "\n"
    )

    print("=== CANONICAL STATIC ORACLE ===")

    for workload in WORKLOADS:
        row = oracle[workload]

        print(
            f"{workload:8s} "
            f"best={row['best_kernel']:8s} "
            f"{row['best_ms']:.3f} ms"
        )

    print()

    for x in adaptive_results:
        print(
            "Adaptive",
            x["session_index"],
            "selected=",
            x["selected_kernel"],
            "selector_wall_ms=",
            f"{x['selector_wall_ms']:.3f}",
            "GM_regret=",
            f"{x['environment_gm_regret']:.6f}",
            "PASS=",
            x["pass"]
        )

        for workload in WORKLOADS:
            print(
                " ",
                workload,
                f"{x['regret_by_workload'][workload]:.6f}"
            )

    print()
    print(
        "ENVIRONMENT PASS:",
        environment_pass
    )


if __name__ == "__main__":
    main()
