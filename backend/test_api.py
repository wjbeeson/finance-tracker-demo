import pytest
import os
import tempfile
import io
from app import app, init_db, get_db, DATABASE


@pytest.fixture
def client(tmp_path):
    """Create a test client with an isolated temporary database."""
    db_path = str(tmp_path / "test_expenses.db")
    app.config["TESTING"] = True

    # Patch DATABASE at module level
    import app as app_module
    original_db = app_module.DATABASE
    app_module.DATABASE = db_path

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    app_module.DATABASE = original_db


@pytest.fixture
def seeded_client(client):
    """Client with pre-populated expense data."""
    csv_content = (
        "description,amount,date,category\n"
        "Groceries,50.00,2026-01-15,Food\n"
        "Electric bill,120.00,2026-01-10,Utilities\n"
        "Restaurant,35.50,2026-01-20,Food\n"
        "Gas,40.00,2026-01-18,Transport\n"
        "Internet,60.00,2026-01-05,Utilities\n"
    )
    pass
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "expenses.csv")}
    client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
    return client


# ─── GET /api/expenses ────────────────────────────────────────────────────────

class TestGetExpenses:
    def test_empty_database(self, client):
        """GET /api/expenses returns an empty list when no data exists."""
        resp = client.get("/api/expenses")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_all_expenses(self, seeded_client):
        """GET /api/expenses returns all seeded expenses."""
        resp = seeded_client.get("/api/expenses")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 5

    def test_expenses_ordered_by_date_desc(self, seeded_client):
        """Expenses are returned newest-first."""
        resp = seeded_client.get("/api/expenses")
        data = resp.get_json()
        dates = [row["date"] for row in data]
        assert dates == sorted(dates, reverse=True)

    def test_expense_fields(self, seeded_client):
        """Each expense has the expected fields."""
        resp = seeded_client.get("/api/expenses")
        expense = resp.get_json()[0]
        assert set(expense.keys()) == {"id", "description", "amount", "date", "category"}

    def test_expense_data_types(self, seeded_client):
        """Field values have the correct types."""
        resp = seeded_client.get("/api/expenses")
        expense = resp.get_json()[0]
        assert isinstance(expense["id"], int)
        assert isinstance(expense["description"], str)
        assert isinstance(expense["amount"], (int, float))
        assert isinstance(expense["date"], str)
        assert isinstance(expense["category"], str)


# ─── POST /api/expenses/upload ────────────────────────────────────────────────

class TestUploadCSV:
    def test_successful_upload(self, client):
        """Uploading a valid CSV imports rows and returns a success message."""
        csv_content = (
            "description,amount,date,category\n"
            "Coffee,4.50,2026-02-01,Food\n"
            "Taxi,15.00,2026-02-02,Transport\n"
        )
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "test.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        body = resp.get_json()
        assert "Successfully imported 2 expenses" in body["message"]

    def test_uploaded_data_persists(self, client):
        """After upload, expenses are retrievable via GET."""
        csv_content = "description,amount,date,category\nLunch,12.00,2026-02-10,Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "test.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses")
        expenses = resp.get_json()
        assert len(expenses) == 1
        assert expenses[0]["description"] == "Lunch"
        assert expenses[0]["amount"] == 12.00

    def test_no_file_provided(self, client):
        """Request without a file part returns 400."""
        resp = client.post("/api/expenses/upload", data={}, content_type="multipart/form-data")
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "No file provided"

    def test_empty_filename(self, client):
        """File with an empty filename returns 400."""
        data = {"file": (io.BytesIO(b""), "")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "No file selected"

    def test_non_csv_file_rejected(self, client):
        """Uploading a non-CSV file returns 400."""
        data = {"file": (io.BytesIO(b"some data"), "data.txt")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "File must be a CSV"

    def test_capitalized_column_names(self, client):
        """CSV with capitalized column headers (Description, Amount, etc.) works."""
        csv_content = (
            "Description,Amount,Date,Category\n"
            "Gym membership,30.00,2026-03-01,Health\n"
        )
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "caps.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200

        expenses = client.get("/api/expenses").get_json()
        assert len(expenses) == 1
        assert expenses[0]["description"] == "Gym membership"
        assert expenses[0]["amount"] == 30.00
        assert expenses[0]["category"] == "Health"

    def test_upload_multiple_files_sequentially(self, client):
        """Multiple uploads accumulate expenses."""
        for i in range(3):
            csv = f"description,amount,date,category\nItem{i},{i + 1}.00,2026-01-0{i + 1},Cat{i}\n"
            data = {"file": (io.BytesIO(csv.encode("utf-8")), f"batch{i}.csv")}
            client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        expenses = client.get("/api/expenses").get_json()
        assert len(expenses) == 3

    def test_duplicate_csv_upload(self, client):
        """Uploading the same CSV twice doubles the data and summary totals."""
        csv_content = (
            "description,amount,date,category\n"
            "Coffee,4.50,2026-01-10,Food\n"
            "Bus ticket,2.00,2026-01-11,Transport\n"
        )

        # First upload
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "dup.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "2 expenses" in resp.get_json()["message"]

        # Second identical upload
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "dup.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "2 expenses" in resp.get_json()["message"]

        # All 4 rows should be present
        expenses = client.get("/api/expenses").get_json()
        assert len(expenses) == 4

        # Summary totals should reflect both uploads
        summary = client.get("/api/expenses/summary").get_json()
        totals = {row["category"]: row["total"] for row in summary}
        assert totals["Food"] == pytest.approx(9.00)       # 4.50 * 2
        assert totals["Transport"] == pytest.approx(4.00)   # 2.00 * 2

    def test_malformed_csv_returns_500(self, client):
        """A CSV with non-numeric amount triggers a 500 error."""
        csv_content = "description,amount,date,category\nBad,not_a_number,2026-01-01,Misc\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "bad.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_empty_csv_imports_zero(self, client):
        """A CSV with only headers and no data rows imports 0 expenses."""
        csv_content = "description,amount,date,category\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "empty.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "0 expenses" in resp.get_json()["message"]

    def test_single_row_csv(self, client):
        """A CSV with exactly one data row imports 1 expense."""
        csv_content = "description,amount,date,category\nSingle,9.99,2026-06-15,Misc\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "single.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "1 expenses" in resp.get_json()["message"]

    def test_special_characters_in_fields(self, client):
        """CSV with quoted fields containing commas and special characters imports correctly."""
        csv_content = (
            'description,amount,date,category\n'
            '"Lunch, dinner & drinks",55.00,2026-04-10,"Food & Drink"\n'
            '"Hotel ""Grand Palace""",200.00,2026-04-11,Travel\n'
        )
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "special.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "2 expenses" in resp.get_json()["message"]

        expenses = client.get("/api/expenses").get_json()
        assert len(expenses) == 2

        descs = {e["description"] for e in expenses}
        assert "Lunch, dinner & drinks" in descs
        assert 'Hotel "Grand Palace"' in descs

        cats = {e["category"] for e in expenses}
        assert "Food & Drink" in cats
        assert "Travel" in cats

        amounts = {e["description"]: e["amount"] for e in expenses}
        assert amounts["Lunch, dinner & drinks"] == pytest.approx(55.00)
        assert amounts['Hotel "Grand Palace"'] == pytest.approx(200.00)

    def test_large_csv_upload(self, client):
        """Uploading a CSV with 500 rows imports all of them correctly."""
        header = "description,amount,date,category\n"
        rows = "".join(
            f"Item {i},{i * 1.5:.2f},2026-01-{(i % 28) + 1:02d},Cat{i % 5}\n"
            for i in range(500)
        )
        csv_content = header + rows
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "large.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "500 expenses" in resp.get_json()["message"]

        expenses = client.get("/api/expenses").get_json()
        assert len(expenses) == 500

        # Summary should have exactly 5 categories (Cat0–Cat4)
        summary = client.get("/api/expenses/summary").get_json()
        assert len(summary) == 5
        assert {row["category"] for row in summary} == {"Cat0", "Cat1", "Cat2", "Cat3", "Cat4"}

    def test_csv_with_extra_columns_ignored(self, client):
        """CSV with extra columns beyond the expected ones still imports correctly."""
        csv_content = (
            "description,amount,date,category,notes,priority\n"
            "Dinner,42.00,2026-05-01,Food,business meal,high\n"
            "Taxi,15.00,2026-05-02,Transport,airport run,low\n"
        )
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "extra_cols.csv")}
        resp = client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert "2 expenses" in resp.get_json()["message"]

        expenses = client.get("/api/expenses").get_json()
        assert len(expenses) == 2

        # Verify the core fields are correct
        descs = {e["description"] for e in expenses}
        assert descs == {"Dinner", "Taxi"}
        amounts = {e["description"]: e["amount"] for e in expenses}
        assert amounts["Dinner"] == pytest.approx(42.00)
        assert amounts["Taxi"] == pytest.approx(15.00)

        # Extra columns should NOT appear in the response
        for e in expenses:
            assert "notes" not in e
            assert "priority" not in e


# ─── GET /api/expenses/summary ────────────────────────────────────────────────

class TestGetSummary:
    def test_empty_summary(self, client):
        """Summary of an empty database returns an empty list."""
        resp = client.get("/api/expenses/summary")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_summary_groups_by_category(self, seeded_client):
        """Summary groups expenses by category."""
        resp = seeded_client.get("/api/expenses/summary")
        data = resp.get_json()
        categories = [row["category"] for row in data]
        assert set(categories) == {"Food", "Utilities", "Transport"}

    def test_summary_totals_are_correct(self, seeded_client):
        """Category totals are summed correctly."""
        resp = seeded_client.get("/api/expenses/summary")
        data = resp.get_json()
        totals = {row["category"]: row["total"] for row in data}
        assert totals["Food"] == pytest.approx(85.50)       # 50 + 35.50
        assert totals["Utilities"] == pytest.approx(180.00)  # 120 + 60
        assert totals["Transport"] == pytest.approx(40.00)

    def test_summary_ordered_by_total_desc(self, seeded_client):
        """Summary rows are ordered by total descending."""
        resp = seeded_client.get("/api/expenses/summary")
        data = resp.get_json()
        totals = [row["total"] for row in data]
        assert totals == sorted(totals, reverse=True)

    def test_summary_fields(self, seeded_client):
        """Each summary row has 'category' and 'total' fields."""
        resp = seeded_client.get("/api/expenses/summary")
        for row in resp.get_json():
            assert set(row.keys()) == {"category", "total"}

    def test_summary_after_additional_upload(self, seeded_client):
        """Summary updates correctly after adding more data."""
        csv_content = "description,amount,date,category\nBus pass,25.00,2026-02-01,Transport\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "more.csv")}
        seeded_client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = seeded_client.get("/api/expenses/summary")
        totals = {row["category"]: row["total"] for row in resp.get_json()}
        assert totals["Transport"] == pytest.approx(65.00)  # 40 + 25

    def test_single_category(self, client):
        """Summary with only one category returns a single row."""
        csv_content = (
            "description,amount,date,category\n"
            "A,10.00,2026-01-01,OnlyCat\n"
            "B,20.00,2026-01-02,OnlyCat\n"
        )
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "one_cat.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/summary")
        summary = resp.get_json()
        assert len(summary) == 1
        assert summary[0]["category"] == "OnlyCat"
        assert summary[0]["total"] == pytest.approx(30.00)
