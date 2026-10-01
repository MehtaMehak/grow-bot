"""Phase 2 pipeline: Load sources, chunk text, save results."""

import json
import os
import sys

# Add project root to path so imports work when run from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.loader import load_source
from ingestion.chunker import create_chunks, save_chunks_to_file

# Define the 15 approved sources
SOURCES = [
    # Groww web pages (1-5)
    {
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "source_type": "web_page",
        "scheme_name": "HDFC Large Cap Fund",
        "source_title": "HDFC Large Cap Fund - Direct Growth",
        "document_date": None,
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "source_type": "web_page",
        "scheme_name": "HDFC Flexi Cap Fund",
        "source_title": "HDFC Flexi Cap Fund - Direct Growth",
        "document_date": None,
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        "source_type": "web_page",
        "scheme_name": "HDFC ELSS Tax Saver Fund",
        "source_title": "HDFC ELSS Tax Saver Fund - Direct Plan Growth",
        "document_date": None,
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "source_type": "web_page",
        "scheme_name": "HDFC Small Cap Fund",
        "source_title": "HDFC Small Cap Fund - Direct Growth",
        "document_date": None,
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
        "source_type": "web_page",
        "scheme_name": "HDFC Balanced Advantage Fund",
        "source_title": "HDFC Balanced Advantage Fund - Direct Growth",
        "document_date": None,
    },
    # HDFC AMC scheme pages (6-10)
    {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
        "source_type": "web_page",
        "scheme_name": "HDFC Flexi Cap Fund",
        "source_title": "HDFC Flexi Cap Fund - Direct",
        "document_date": None,
    },
    {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-large-cap-fund/direct",
        "source_type": "web_page",
        "scheme_name": "HDFC Large Cap Fund",
        "source_title": "HDFC Large Cap Fund - Direct",
        "document_date": None,
    },
    {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-mid-cap-fund/direct",
        "source_type": "web_page",
        "scheme_name": "HDFC Mid Cap Fund",
        "source_title": "HDFC Mid Cap Fund - Direct",
        "document_date": None,
    },
    {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-elss-tax-saver-fund/direct",
        "source_type": "web_page",
        "scheme_name": "HDFC ELSS Tax Saver Fund",
        "source_title": "HDFC ELSS Tax Saver Fund - Direct",
        "document_date": None,
    },
    {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        "source_type": "web_page",
        "scheme_name": "HDFC Balanced Advantage Fund",
        "source_title": "HDFC Balanced Advantage Fund - Direct",
        "document_date": None,
    },
    # HDFC Fund Facts PDFs (11-15)
    {
        "url": "https://files.hdfcfund.com/s3fs-public/Others/2026-09/Fund%20Facts%20-%20HDFC%20Flexi%20Cap%20Fund_September%202026_0.pdf",
        "source_type": "pdf",
        "scheme_name": "HDFC Flexi Cap Fund",
        "source_title": "Fund Facts - HDFC Flexi Cap Fund - September 2026",
        "document_date": "September 2026",
    },
    {
        "url": "https://files.hdfcfund.com/s3fs-public/Others/2026-09/Fund%20Facts%20-%20HDFC%20Large%20Cap%20Fund_September%202026.pdf",
        "source_type": "pdf",
        "scheme_name": "HDFC Large Cap Fund",
        "source_title": "Fund Facts - HDFC Large Cap Fund - September 2026",
        "document_date": "September 2026",
    },
    {
        "url": "https://files.hdfcfund.com/s3fs-public/Others/2026-09/Fund%20Facts%20-%20HDFC%20Mid-Cap%20Fund_September%202026.pdf",
        "source_type": "pdf",
        "scheme_name": "HDFC Mid Cap Fund",
        "source_title": "Fund Facts - HDFC Mid-Cap Fund - September 2026",
        "document_date": "September 2026",
    },
    {
        "url": "https://files.hdfcfund.com/s3fs-public/Others/2026-07/Fund%20Facts%20-%20HDFC%20TaxSaver%20Fund_July%202026.pdf",
        "source_type": "pdf",
        "scheme_name": "HDFC ELSS Tax Saver Fund",
        "source_title": "Fund Facts - HDFC TaxSaver Fund - July 2026",
        "document_date": "July 2026",
    },
    {
        "url": "https://files.hdfcfund.com/s3fs-public/Others/2026-09/Fund%20Facts%20-%20HDFC%20Balanced%20Advantage%20Fund_September%202026.pdf",
        "source_type": "pdf",
        "scheme_name": "HDFC Balanced Advantage Fund",
        "source_title": "Fund Facts - HDFC Balanced Advantage Fund - September 2026",
        "document_date": "September 2026",
    },
]


def main():
    # Create directories
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/chunks", exist_ok=True)

    all_chunks = []
    successful = 0
    failed = 0
    failed_sources = []
    chunk_count_per_source = {}
    chunk_count_per_scheme = {}

    print("=" * 70)
    print("PHASE 2 — LOADING & CHUNKING PIPELINE")
    print("=" * 70)
    print(f"Total sources to load: {len(SOURCES)}")
    print(f"Chunk size: 500 characters")
    print(f"Chunk overlap: 100 characters")
    print("=" * 70)

    for i, source in enumerate(SOURCES, 1):
        url = source["url"]
        scheme = source["scheme_name"]
        source_type = source["source_type"]

        print(f"\n[{i}/{len(SOURCES)}] Loading {source_type}: {scheme}")
        print(f"  URL: {url}")

        # Load the source
        source_data, error = load_source(source)

        if error:
            print(f"  FAILED: {error}")
            failed += 1
            failed_sources.append({
                "url": url,
                "scheme_name": scheme,
                "error": error,
            })
            continue

        # Save raw text
        raw_filename = f"{i:02d}_{source_type}_{scheme.replace(' ', '_').lower()}.txt"
        raw_path = os.path.join("data/raw", raw_filename)
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(source_data["raw_text"])
        print(f"  Raw text saved to: {raw_path}")
        print(f"  Raw text length: {len(source_data['raw_text'])} characters")

        # Chunk the text
        chunks = create_chunks(source_data, chunk_size=500, overlap=100)
        all_chunks.extend(chunks)

        # Update counts
        chunk_count_per_source[raw_filename] = len(chunks)
        chunk_count_per_scheme[scheme] = chunk_count_per_scheme.get(scheme, 0) + len(chunks)

        print(f"  Chunks created: {len(chunks)}")
        successful += 1

    # Save all chunks to chunks.txt
    chunks_path = "data/chunks/chunks.txt"
    save_chunks_to_file(all_chunks, chunks_path)

    # Print summary
    print("\n" + "=" * 70)
    print("PHASE 2 SUMMARY")
    print("=" * 70)
    print(f"Sources attempted: {len(SOURCES)}")
    print(f"Successfully loaded: {successful}")
    print(f"Failed: {failed}")
    print(f"Total chunks created: {len(all_chunks)}")

    print(f"\nChunk count per source:")
    for source, count in chunk_count_per_source.items():
        print(f"  {source}: {count}")

    print(f"\nChunk count per scheme:")
    for scheme, count in chunk_count_per_scheme.items():
        print(f"  {scheme}: {count}")

    if failed_sources:
        print(f"\nFailed sources:")
        for fs in failed_sources:
            print(f"  - {fs['scheme_name']}: {fs['url']}")
            print(f"    Error: {fs['error']}")

    print(f"\nChunks saved to: {chunks_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
