import pytest
import os
import tempfile
import io
import calendar
from datetime import datetime, timedelta
from unittest.mock import patch
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
        assert set(expense.keys()) == {"id", "description", "amount", "date", "category", "excluded"}

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


# ─── GET /api/expenses/timeseries ─────────────────────────────────────────────

class TestGetTimeSeries:
    def _upload(self, client, rows):
        header = "description,amount,date,category\n"
        body = "".join(f"{r[0]},{r[1]},{r[2]},{r[3]}\n" for r in rows)
        data = {"file": (io.BytesIO((header + body).encode("utf-8")), "ts.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

    def test_empty_timeseries(self, client):
        """Timeseries with no data returns gap-filled zeros for the full period."""
        resp = client.get("/api/expenses/timeseries?period=month")
        assert resp.status_code == 200
        data = resp.get_json()
        now = datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        assert len(data) == days_in_month
        assert all(row["total"] == 0 for row in data)

    def test_invalid_period(self, client):
        """Invalid period returns 400."""
        resp = client.get("/api/expenses/timeseries?period=decade")
        assert resp.status_code == 400
        assert "Invalid period" in resp.get_json()["error"]

    def test_month_period(self, client):
        """Month period returns all days in current month with gap-filled zeros."""
        now = datetime.now()
        date1 = f"{now.year}-{now.month:02d}-05"
        date2 = f"{now.year}-{now.month:02d}-05"
        date3 = f"{now.year}-{now.month:02d}-10"
        self._upload(client, [
            ("A", "10.00", date1, "Food"),
            ("B", "20.00", date2, "Food"),
            ("C", "30.00", date3, "Transport"),
        ])
        resp = client.get("/api/expenses/timeseries?period=month")
        assert resp.status_code == 200
        data = resp.get_json()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        assert len(data) == days_in_month
        totals = {row["date"]: row["total"] for row in data}
        assert totals[date1] == pytest.approx(30.00)
        assert totals[date3] == pytest.approx(30.00)
        # All other days should be zero-filled
        zero_days = [row for row in data if row["date"] not in (date1, date3)]
        assert all(row["total"] == 0 for row in zero_days)

    def test_week_period(self, client):
        """Week period returns all 7 days with gap-filled zeros."""
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        in_week = start_of_week.strftime("%Y-%m-%d")
        out_of_week = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        self._upload(client, [
            ("A", "10.00", in_week, "Food"),
            ("B", "50.00", out_of_week, "Food"),
        ])
        resp = client.get("/api/expenses/timeseries?period=week")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 7
        totals = {row["date"]: row["total"] for row in data}
        assert totals[in_week] == pytest.approx(10.00)
        # Out-of-week expense should not appear; remaining days are zero
        assert out_of_week not in totals
        zero_days = [row for row in data if row["date"] != in_week]
        assert all(row["total"] == 0 for row in zero_days)

    def test_year_period_groups_by_month(self, client):
        """Year period returns all 12 months with gap-filled zeros."""
        now = datetime.now()
        self._upload(client, [
            ("A", "10.00", f"{now.year}-01-15", "Food"),
            ("B", "20.00", f"{now.year}-01-20", "Food"),
            ("C", "30.00", f"{now.year}-03-10", "Transport"),
        ])
        resp = client.get("/api/expenses/timeseries?period=year")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 12
        totals = {row["date"]: row["total"] for row in data}
        assert totals[f"{now.year}-01"] == pytest.approx(30.00)
        assert totals[f"{now.year}-03"] == pytest.approx(30.00)
        # Months without data should be zero
        zero_months = [row for row in data if row["date"] not in (f"{now.year}-01", f"{now.year}-03")]
        assert all(row["total"] == 0 for row in zero_months)

    def test_default_period_is_month(self, client):
        """Default period is month when not specified, returns full month gap-filled."""
        now = datetime.now()
        date1 = f"{now.year}-{now.month:02d}-01"
        self._upload(client, [("A", "10.00", date1, "Food")])
        resp = client.get("/api/expenses/timeseries")
        assert resp.status_code == 200
        data = resp.get_json()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        assert len(data) == days_in_month
        totals = {row["date"]: row["total"] for row in data}
        assert totals[date1] == pytest.approx(10.00)

    def test_timeseries_ordered_by_date_asc(self, client):
        """Results are ordered by date ascending."""
        now = datetime.now()
        self._upload(client, [
            ("A", "10.00", f"{now.year}-{now.month:02d}-15", "Food"),
            ("B", "20.00", f"{now.year}-{now.month:02d}-05", "Food"),
            ("C", "30.00", f"{now.year}-{now.month:02d}-10", "Food"),
        ])
        resp = client.get("/api/expenses/timeseries?period=month")
        data = resp.get_json()
        dates = [row["date"] for row in data]
        assert dates == sorted(dates)


# ─── GET /api/expenses/periods ────────────────────────────────────────────────

class TestGetPeriods:
    def _upload(self, client, rows):
        header = "description,amount,date,category\n"
        body = "".join(f"{r[0]},{r[1]},{r[2]},{r[3]}\n" for r in rows)
        data = {"file": (io.BytesIO((header + body).encode("utf-8")), "p.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

    def test_all_false_when_empty(self, client):
        """All periods are false when no data exists."""
        resp = client.get("/api/expenses/periods")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {"week": False, "month": False, "year": False}

    def test_month_available(self, client):
        """Month is true when data exists in the current month."""
        now = datetime.now()
        date = f"{now.year}-{now.month:02d}-10"
        self._upload(client, [("A", "10.00", date, "Food")])
        resp = client.get("/api/expenses/periods")
        data = resp.get_json()
        assert data["month"] is True
        assert data["year"] is True

    def test_week_available(self, client):
        """Week is true when data exists in the current week."""
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        date = start_of_week.strftime("%Y-%m-%d")
        self._upload(client, [("A", "10.00", date, "Food")])
        resp = client.get("/api/expenses/periods")
        data = resp.get_json()
        assert data["week"] is True

    def test_old_data_not_in_current_periods(self, client):
        """Data from a past year doesn't show in current periods."""
        self._upload(client, [("A", "10.00", "2020-06-15", "Food")])
        resp = client.get("/api/expenses/periods")
        data = resp.get_json()
        assert data == {"week": False, "month": False, "year": False}
