from tinydb import TinyDB, Query
from tinydb.table import Table
from typing import Type, TypedDict


class LocalDBUtility:
    """Utility class for interacting with a local TinyDB database using TypedDict for schema validation."""

    def __init__(self, db_path='db.json', schemas: dict[str, Type[TypedDict]] = None):
        """
        Initialize the database with TypedDict-based schemas.
        :param db_path: Path to the TinyDB JSON file.
        :param schemas: Dictionary mapping table names to TypedDict classes.
        """
        self.db = TinyDB(db_path)
        self.query = Query()
        self.schemas = schemas if schemas else {}

    def get_table(self, table_name) -> Table:
        """Retrieve a specific table from the database."""
        return self.db.table(table_name)

    def validate_schema(self, table_name, data):
        """Validate data against the TypedDict schema for a table."""
        if table_name in self.schemas:
            expected_fields = set(self.schemas[table_name].__annotations__.keys())
            actual_fields = set(data.keys())
            if not expected_fields.issubset(actual_fields):
                missing_fields = expected_fields - actual_fields
                raise ValueError(f"Schema validation failed for '{table_name}'. Missing fields: {missing_fields}")
        return True

    def insert(self, table_name, data):
        """Insert data after validating against TypedDict schema."""
        try:
            self.validate_schema(table_name, data)
            self.get_table(table_name).insert(data)
            print(f"Data inserted successfully into '{table_name}'.")
        except Exception as e:
            print(f"Insert failed in '{table_name}': {e}")

    def read_all(self, table_name):
        """Read all records from the specified table."""
        try:
            data = self.get_table(table_name).all()
            print(f"Data read successfully from '{table_name}'.")
            return data
        except Exception as e:
            print(f"Read failed in '{table_name}': {e}")
            return []

    def search(self, table_name, field, value):
        """Search for records where field == value in the specified table."""
        try:
            results = self.get_table(table_name).search(self.query[field] == value)
            print(f"Search in '{table_name}' completed: {results}")
            return results
        except Exception as e:
            print(f"Search failed in '{table_name}': {e}")
            return []

    def update(self, table_name, updates, field, value):
        """Update records in the specified table."""
        try:
            self.get_table(table_name).update(updates, self.query[field] == value)
            print(f"Update successful in '{table_name}'.")
        except Exception as e:
            print(f"Update failed in '{table_name}': {e}")

    def delete(self, table_name, field, value):
        """Delete records in the specified table."""
        try:
            self.get_table(table_name).remove(self.query[field] == value)
            print(f"Delete successful in '{table_name}'.")
        except Exception as e:
            print(f"Delete failed in '{table_name}': {e}")

    def clear(self, table_name):
        """Clear all records from the specified table."""
        try:
            self.get_table(table_name).truncate()
            print(f"Table '{table_name}' cleared.")
        except Exception as e:
            print(f"Clear failed in '{table_name}': {e}")

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
            existing_records = table.search(self.query[field] == data.get(field))

            if existing_records:
                # Update existing record(s)
                table.update(data, self.query[field] == data.get(field))
                print(f"Upsert: Existing record updated in '{table_name}'.")
            else:
                # Insert new record
                table.insert(data)
                print(f"Upsert: New record inserted into '{table_name}'.")
        except Exception as e:
            print(f"Upsert failed in '{table_name}': {e}")
