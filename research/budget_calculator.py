#!/usr/bin/env python3
"""Offline scenario calculator. No API calls, provisioning, or credential reads.

Rates are planning snapshots, not live quotes. Output tokens include ALL billable
output, including internal reasoning when charged. Human labor is not included.
"""

import argparse
import json
import math


def nonnegative(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("must be finite and nonnegative")
    return result


def positive_int(value):
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("must be at least one")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", type=positive_int, default=24)
    parser.add_argument("--providers", type=positive_int, default=2)
    parser.add_argument("--calls-per-item", type=positive_int, default=1)
    parser.add_argument("--input-tokens", type=nonnegative, default=1500)
    parser.add_argument("--output-tokens", type=nonnegative, default=2000)
    parser.add_argument("--input-rate", type=nonnegative, default=5)
    parser.add_argument("--output-rate", type=nonnegative, default=25)
    parser.add_argument("--retry-factor", type=nonnegative, default=1)
    parser.add_argument("--jev-total-input-per-item", type=nonnegative, default=1500)
    parser.add_argument("--jev-input-rate", type=nonnegative, default=0.042)
    parser.add_argument("--gpu-hours", type=nonnegative, default=1)
    parser.add_argument("--gpu-hourly-rate", type=nonnegative, default=0.75)
    parser.add_argument("--storage-cpu-usd", type=nonnegative, default=1)
    args = parser.parse_args()
    if args.retry_factor < 1:
        parser.error("--retry-factor must be at least one")

    per_call = (args.input_tokens * args.input_rate
                + args.output_tokens * args.output_rate) / 1_000_000
    per_provider = (per_call * args.examples * args.calls_per_item
                    * args.retry_factor)
    frontier_total = per_provider * args.providers
    jev_total = (args.examples * args.jev_total_input_per_item
                 * args.jev_input_rate * args.retry_factor / 1_000_000)
    gpu_total = args.gpu_hours * args.gpu_hourly_rate
    result = {
        "status": "offline_scenario_not_a_live_quote_or_spending_authorization",
        "assumptions": vars(args),
        "frontier_cost_per_call_usd": round(per_call, 6),
        "frontier_cost_per_provider_usd": round(per_provider, 6),
        "frontier_total_usd": round(frontier_total, 6),
        "jev_total_usd": round(jev_total, 6),
        "gpu_total_usd": round(gpu_total, 6),
        "total_scenario_usd": round(frontier_total + jev_total + gpu_total
                                    + args.storage_cpu_usd, 6),
        "exclusions": ["human labor", "unconfigured extra baselines",
                       "actual idle and download time beyond gpu-hours",
                       "cache-specific pricing", "taxes and currency conversion"],
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
