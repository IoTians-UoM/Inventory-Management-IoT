from tinydb import TinyDB, Query

class LocalDBUtility:
    """Utility class for interacting with a local TinyDB database."""
    def __init__(self, db_path='db.json'):
        self.db = TinyDB(db_path)
        self.query = Query()

    def insert(self, data):
        """Insert data into the database."""
        try:
            self.db.insert(data)
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Insert failed: {e}")

    def read_all(self):
        """Read all records from the database."""
        try:
            data = self.db.all()
            print("Data read successfully.")
            return data
        except Exception as e:
            print(f"Read failed: {e}")
            return []

    def search(self, field, value):
        """Search for records where the specified field matches the given value."""
        try:
            results = self.db.search(self.query[field] == value)
            print(f"Search completed: {results}")
            return results
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def update(self, updates, field, value):
        """Update records matching the field-value pair with new data."""
        try:
            self.db.update(updates, self.query[field] == value)
            print("Update successful.")
        except Exception as e:
            print(f"Update failed: {e}")

    def delete(self, field, value):
        """Delete records where the specified field matches the given value."""
        try:
            self.db.remove(self.query[field] == value)
            print("Delete successful.")
        except Exception as e:
            print(f"Delete failed: {e}")

    def clear(self):
        """Clear the entire database."""
        try:
            self.db.truncate()
            print("Database cleared.")
        except Exception as e:
            print(f"Clear failed: {e}")


