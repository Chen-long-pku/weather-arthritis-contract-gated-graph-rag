"""
Run the quote-first extraction prototype on an audit workbook.

The script is designed for reproducible method development. It does not use
human labels as prompts. If final adjudicated labels are present in the input
workbook, they are used only for post-hoc comparison.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from extraction.quote_first_extractor import extract_quote_first  # noqa: E402


def norm(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def wilson(x: int, n: int, z: float = 1.96):
    if n == 0:
        return 0.0, 0.0
    phat = x / n
    denom = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def read_records(path: Path, sheet_name: str) -> List[Dict]:
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet_name]
    headers = [cell.value for cell in ws[1]]
    records = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        item = dict(zip(headers, row))
        if item.get("audit_id") or item.get("pmid"):
            records.append(item)
    return records


def first_relationship(extraction: Dict) -> Dict:
    rels = extraction.get("selected_relationships", [])
    return rels[0] if rels else {}


def run(input_workbook: Path, sheet_name: str, output_dir: Path) -> Dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    records = read_records(input_workbook, sheet_name)
    rows: List[Dict] = []

    for record in records:
        abstract = norm(record.get("abstract_for_review") or record.get("abstract"))
        pmid = norm(record.get("pmid"))
        title = norm(record.get("title"))
        result = extract_quote_first(pmid=pmid, title=title, abstract=abstract)
        rel = first_relationship(result)
        evidence_sentences = result.get("evidence_sentences", [])
        in_scope_sentence_count = sum(1 for item in evidence_sentences if item.get("scope_status") == "in_scope")
        exact_sentence_count = sum(1 for item in evidence_sentences if item.get("evidence_quote_exact_match"))
        row = {
            "audit_id": norm(record.get("audit_id")),
            "pmid": pmid,
            "pubmed_url": norm(record.get("pubmed_url")),
            "title": title,
            "abstract_for_review": abstract,
            "candidate_generated": "YES" if rel else "NO",
            "climate_factor": rel.get("climate_factor", ""),
            "effect_on": rel.get("effect_on", ""),
            "relationship_type": rel.get("relationship_type", ""),
            "evidence_quote": rel.get("evidence_quote", ""),
            "quote_start_char": rel.get("quote_start_char", ""),
            "quote_end_char": rel.get("quote_end_char", ""),
            "exact_quote_match": "YES" if rel.get("evidence_quote_exact_match") else "NO",
            "scope_status": rel.get("scope_status", ""),
            "scope_reason": rel.get("scope_reason", ""),
            "graph_insertion_status": rel.get("graph_insertion_status", "no_candidate"),
            "evidence_sentence_count": len(evidence_sentences),
            "in_scope_sentence_count": in_scope_sentence_count,
            "exact_source_sentence_count": exact_sentence_count,
            "selected_relationship_count": len(result.get("selected_relationships", [])),
            "prior_final_extraction_correct_overall": norm(record.get("final_extraction_correct_overall")),
            "prior_final_in_scope_for_graph": norm(record.get("final_in_scope_for_graph")),
            "prior_final_relation_present_in_abstract": norm(record.get("final_relation_present_in_abstract")),
            "prior_final_evidence_quote_supports_relation": norm(record.get("final_evidence_quote_supports_relation")),
            "prior_final_strict_graph_eligible": norm(record.get("final_strict_graph_eligible")),
            "prior_final_evidence_trace_strict_eligible": norm(record.get("final_evidence_trace_strict_eligible")),
            "prior_final_error_type_primary": norm(record.get("final_error_type_primary")),
        }
        rows.append(row)

    n = len(rows)
    generated = sum(1 for row in rows if row["candidate_generated"] == "YES")
    exact = sum(1 for row in rows if row["exact_quote_match"] == "YES")
    in_scope_record = sum(1 for row in rows if int(row["in_scope_sentence_count"] or 0) > 0)
    old_exact = sum(1 for row in rows if row["prior_final_evidence_quote_supports_relation"] == "YES")
    old_strict = sum(1 for row in rows if row["prior_final_strict_graph_eligible"] == "YES")
    old_content = sum(
        1
        for row in rows
        if row["prior_final_in_scope_for_graph"] == "in_scope"
        and row["prior_final_relation_present_in_abstract"] == "YES"
        and row["prior_final_extraction_correct_overall"] in {"correct", "partially_correct"}
    )

    summary_rows = [
        ("Records processed", n, n),
        ("quote-first records with at least one in-scope source sentence", in_scope_record, n),
        ("quote-first generated at least one quote-first candidate", generated, n),
        ("quote-first generated candidate with exact evidence quote", exact, n),
        ("prior exact evidence quote support by expert adjudication", old_exact, n),
        ("prior content-level eligible by final adjudication", old_content, n),
        ("prior strict graph-eligible candidate by final adjudication", old_strict, n),
    ]

    workbook = Workbook()
    ws = workbook.active
    ws.title = "Summary"
    ws.append(["metric", "n", "N", "percent", "95CI_low", "95CI_high"])
    for label, x, denom in summary_rows:
        lo, hi = wilson(x, denom)
        ws.append([label, x, denom, x / denom * 100 if denom else 0, lo * 100, hi * 100])

    ws2 = workbook.create_sheet("Extracted_Candidates")
    headers = list(rows[0].keys()) if rows else []
    ws2.append(headers)
    for row in rows:
        ws2.append([row.get(header, "") for header in headers])

    ws3 = workbook.create_sheet("Category_Counts")
    ws3.append(["field", "category", "n"])
    for field in [
        "candidate_generated",
        "relationship_type",
        "exact_quote_match",
        "scope_status",
        "graph_insertion_status",
        "prior_final_evidence_quote_supports_relation",
        "prior_final_error_type_primary",
    ]:
        counts = Counter(row.get(field, "") or "(blank)" for row in rows)
        for category, count in sorted(counts.items()):
            ws3.append([field, category, count])

    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2"
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F4E78")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for col in range(1, sheet.max_column + 1):
            header = sheet.cell(1, col).value or ""
            width = 18
            if header in {"title", "abstract_for_review", "evidence_quote", "scope_reason"}:
                width = 48
            elif header == "pubmed_url":
                width = 32
            sheet.column_dimensions[get_column_letter(col)].width = width
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)

    out_xlsx = output_dir / "Quote_First_Extraction_QC_Internal_Audit_100.xlsx"
    workbook.save(out_xlsx)

    out_csv = output_dir / "Quote_First_Extraction_QC_Internal_Audit_100.csv"
    with out_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "records_processed": n,
        "records_with_in_scope_source_sentence": in_scope_record,
        "candidate_generated": generated,
        "exact_quote_match": exact,
        "prior_exact_evidence_quote_support": old_exact,
        "prior_content_level_eligible": old_content,
        "prior_strict_graph_eligible": old_strict,
        "xlsx": str(out_xlsx),
        "csv": str(out_csv),
    }
    (output_dir / "Quote_First_Extraction_QC_Internal_Audit_Summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-workbook", required=True)
    parser.add_argument("--sheet-name", default="Final_Adjudicated_Records")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    report = run(Path(args.input_workbook), args.sheet_name, Path(args.output_dir))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
