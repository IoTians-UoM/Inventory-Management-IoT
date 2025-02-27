from tinydb import TinyDB, Query
from typing import Dict, Type, TypedDict


class LocalDBUtility:
    """Utility class for interacting with a local TinyDB database using TypedDict for schema validation."""

    def __init__(self, db_path='db.json', schemas: Dict[str, Type[TypedDict]] = None):
        """
        Initialize the database with TypedDict-based schemas.
        :param db_path: Path to the TinyDB JSON file.
        :param schemas: Dictionary mapping table names to TypedDict classes.
        """
        self.db = TinyDB(db_path)
        self.query = Query()
        self.schemas = schemas if schemas else {}

    def get_table(self, table_name):
        """Retrieve a specific table from the database."""
        return self.db.table(table_name)

    def validate_schema(self, table_name, data):
        """Validate data against the TypedDict schema for a table."""
        if table_name in self.schemas:
            expected_fields = set(self.schemas[table_name].__annotations__.keys())
            actual_fields = set(data.keys())

            missing_fields = expected_fields - actual_fields
            extra_fields = actual_fields - expected_fields

            if missing_fields:
                raise ValueError(f"Schema validation failed for '{table_name}'. Missing fields: {missing_fields}")

            if extra_fields:
                print(f"Warning: Extra fields found in '{table_name}': {extra_fields}")

        return True

    def insert(self, table_name, data):
        """Insert data after validating against TypedDict schema."""
        try:
            self.validate_schema(table_name, data)
            self.get_table(table_name).insert(data)
            print(f"Data inserted successfully into '{table_name}'.")
        except Exception as e:
            raise RuntimeError(f"Insert failed in '{table_name}': {e}")

    def read_all(self, table_name):
        """Read all records from the specified table."""
        try:
            return self.get_table(table_name).all()
        except Exception as e:
            raise RuntimeError(f"Read failed in '{table_name}': {e}")

    def search(self, table_name, field, value):
        """Search for records where field == value in the specified table."""
        try:
            return self.get_table(table_name).search(self.query[field] == value)
        except Exception as e:
            raise RuntimeError(f"Search failed in '{table_name}': {e}")

    def update(self, table_name, updates, field, value):
        """Update records in the specified table."""
        try:
            self.get_table(table_name).update(updates, self.query[field] == value)
            print(f"Update successful in '{table_name}'.")
        except Exception as e:
            raise RuntimeError(f"Update failed in '{table_name}': {e}")

    def delete(self, table_name, field, value):
        """Delete records in the specified table."""
        try:
            self.get_table(table_name).remove(self.query[field] == value)
            print(f"Delete successful in '{table_name}'.")
        except Exception as e:
            raise RuntimeError(f"Delete failed in '{table_name}': {e}")

    def clear(self, table_name):
        """Clear all records from the specified table."""
        try:
            self.get_table(table_name).truncate()
            print(f"Table '{table_name}' cleared.")
        except Exception as e:
            raise RuntimeError(f"Clear failed in '{table_name}': {e}")

    def upsert(self, table_name, data, field):
        """
        Upsert operation: Update the record if it exists; otherwise, insert it.

        :param table_name: Name of the table to upsert data into.
        :param data: Data dictionary to insert or update.
        :param field: Field to match existing records for the update.
        """
        try:
            self.validate_schema(table_name, data)
            table = self.get_table(table_name)
            
            # Ensure data[field] exists before querying
            field_value = data.get(field)
            if field_value is None:
                raise ValueError(f"Field '{field}' is missing in the provided data")

            existing_records = table.search(self.query[field] == field_value)

            if existing_records:  # Ensure it's a non-empty list
                for record in existing_records:
                    table.update(data, self.query[field] == field_value)
                print(f"Upsert: Existing record(s) updated in '{table_name}'.")
            else:
                table.insert(data)
                print(f"Upsert: New record inserted into '{table_name}'.")
        
        except Exception as e:
            raise RuntimeError(f"Upsert failed in '{table_name}': {e}")

