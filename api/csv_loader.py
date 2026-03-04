"""Reads CSV files from the data/ folder and inserts them into MongoDB collections."""

import csv
import os
from db import db

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Mapping: filename -> (collection_name, column_headers)
CSV_CONFIG = {
    "totals_data.csv": {
        "collection": "totals_data",
        "columns": [
            "row_id", "account_code", "account_name",
            "opening_balance", "activity", "closing_balance", "level",
        ],
        "types": {
            "row_id": int,
            "opening_balance": float,
            "activity": float,
            "closing_balance": float,
            "level": int,
        },
    },
    "table_property.csv": {
        "collection": "properties",
        "columns": [
            "property_id", "col_2", "col_3", "property_code", "property_name",
            "col_6", "property_type", "address", "city", "province", "postal_code",
            "col_12", "area_sqft", "col_14", "col_15", "col_16", "col_17",
            "col_18", "col_19", "col_20", "col_21", "col_22", "col_23",
            "col_24", "col_25", "col_26", "col_27", "col_28", "col_29",
            "col_30", "col_31", "col_32", "col_33", "market_value", "col_35",
            "col_36", "col_37", "col_38", "acquisition_date",
        ],
        "types": {
            "property_id": int,
            "property_type": int,
            "area_sqft": float,
            "market_value": float,
        },
        "max_columns": 39,
    },
    "fund_tree.csv": {
        "collection": "fund_tree",
        "columns": ["h_fund", "h_investor", "h_investment"],
        "has_header": True,
        "types": {
            "h_fund": int,
            "h_investor": int,
            "h_investment": int,
        },
    },
}


def cast_value(value, target_type):
    """Cast a string value to the target type, returning None for NULL/empty."""
    if value is None or value.strip() == "" or value.strip().upper() == "NULL":
        return None
    try:
        return target_type(value.strip())
    except (ValueError, TypeError):
        return value.strip()


def load_csv(filename, config):
    """Parse a single CSV file and return a list of documents."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return []

    documents = []
    columns = config["columns"]
    types = config.get("types", {})
    has_header = config.get("has_header", False)
    max_columns = config.get("max_columns", len(columns))

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        if has_header:
            next(reader, None)

        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue

            doc = {}
            for i, col_name in enumerate(columns):
                if i < len(row):
                    val = row[i]
                    if col_name in types:
                        val = cast_value(val, types[col_name])
                    else:
                        val = val.strip() if val else None
                        if val and val.upper() == "NULL":
                            val = None
                else:
                    val = None
                doc[col_name] = val

            # Store extra columns as-is for table_property
            if len(row) > max_columns:
                doc["_extra"] = [c.strip() for c in row[max_columns:]]

            documents.append(doc)

    return documents


def import_csv(filename):
    """Import a single CSV file into its MongoDB collection."""
    if filename not in CSV_CONFIG:
        return {"error": f"Unknown CSV file: {filename}"}

    config = CSV_CONFIG[filename]
    collection_name = config["collection"]
    collection = db[collection_name]

    documents = load_csv(filename, config)
    if not documents:
        return {"collection": collection_name, "inserted": 0, "message": "No data found"}

    collection.drop()
    result = collection.insert_many(documents)

    return {
        "collection": collection_name,
        "inserted": len(result.inserted_ids),
    }


def import_all():
    """Import all configured CSV files."""
    results = []
    for filename in CSV_CONFIG:
        result = import_csv(filename)
        results.append(result)
        status = f"  {filename} -> {result['collection']}: {result.get('inserted', 0)} docs"
        print(status)
    return results


if __name__ == "__main__":
    print("Importing CSV files...\n")
    import_all()
    print("\nDone.")
