"""Regenerate the prime tables of 2019/spirals with a sieve of Eratosthenes.

Exact mathematical data, with no downloads or private data. The three tables are
saved once in _lib/data/2019/spirals and the scenes share them."""
from pathlib import Path
import json
import math

OUT = Path(__file__).resolve().parents[4] / "data/2019/spirals"


def primes_up_to(limit):
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start:limit + 1:prime] = b"\x00" * ((limit - start) // prime + 1)
    return [number for number in range(2, limit + 1) if sieve[number]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    primes = primes_up_to(10_000_000)
    for exponent, expected in ((5, 9592), (6, 78498), (7, 664579)):
        values = [p for p in primes if p <= 10 ** exponent]
        assert len(values) == expected, (exponent, len(values))
        path = OUT / f"primes_1e{exponent}.json"
        path.write_text(json.dumps(values, separators=(",", ":")) + "\n")
        print(f"{path.name}: {len(values)} primos")


if __name__ == "__main__":
    main()
