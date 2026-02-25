import pytest
import os
import sys
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, init_db, get_db, normalize_date


@pytest.fixture
def client(tmp_path):
    """Create a test client with an isolated temporary database."""
    db_path = str(tmp_path / "test_expenses.db")
    app.config["TESTING"] = True

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
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "expenses.csv")}
    client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")
    return client


class TestGetExpenses:
    def test_empty_database(self, client):
        """GET /api/expenses returns an empty list when no data exists."""
        resp = client.get("/api/expenses")
        assert resp.status_code == 200
        assert [] == resp.get_json()

    def test_returns_all_expenses(self, seeded_client):
        """GET /api/expenses returns all seeded expenses."""
        resp = seeded_client.get("/api/expenses")
        assert resp.status_code == 200
        data = resp.get_json()
        assert 5 == len(data)

    def test_expenses_ordered_by_date_desc(self, seeded_client):
        """Expenses are returned newest-first."""
        resp = seeded_client.get("/api/expenses")
        data = resp.get_json()
        dates = [row["date"] for row in data]
        assert sorted(dates, reverse=True) == dates

    def test_expense_fields(self, seeded_client):
        """Each expense has the expected fields."""
        resp = seeded_client.get("/api/expenses")
        expense = resp.get_json()[0]
        assert {"id", "description", "amount", "date", "category"} == set(expense.keys())

    def test_expense_data_types(self, seeded_client):
        """Field values have the correct types."""
        resp = seeded_client.get("/api/expenses")
        expense = resp.get_json()[0]
        assert isinstance(expense["id"], int)
        assert isinstance(expense["description"], str)
        assert isinstance(expense["amount"], (int, float))
        assert isinstance(expense["date"], str)
        assert isinstance(expense["category"], str)

    def test_response_content_type_is_json(self, client):
        """GET /api/expenses returns a JSON content type."""
        resp = client.get("/api/expenses")
        assert "application/json" in resp.content_type

    def test_expense_values_match_seeded_data(self, seeded_client):
        """Returned expense values match the seeded CSV data."""
        resp = seeded_client.get("/api/expenses")
        data = resp.get_json()
        descriptions = {row["description"] for row in data}
        assert {"Groceries", "Electric bill", "Restaurant", "Gas", "Internet"} == descriptions

    def test_expense_amounts_match_seeded_data(self, seeded_client):
        """Returned amounts match the seeded CSV amounts."""
        resp = seeded_client.get("/api/expenses")
        data = resp.get_json()
        amounts = {row["description"]: row["amount"] for row in data}
        assert 50.00 == pytest.approx(amounts["Groceries"])
        assert 120.00 == pytest.approx(amounts["Electric bill"])
        assert 35.50 == pytest.approx(amounts["Restaurant"])
        assert 40.00 == pytest.approx(amounts["Gas"])
        assert 60.00 == pytest.approx(amounts["Internet"])

    def test_expense_categories_match_seeded_data(self, seeded_client):
        """Returned categories match the seeded CSV categories."""
        resp = seeded_client.get("/api/expenses")
        data = resp.get_json()
        categories = {row["description"]: row["category"] for row in data}
        assert "Food" == categories["Groceries"]
        assert "Utilities" == categories["Electric bill"]
        assert "Food" == categories["Restaurant"]
        assert "Transport" == categories["Gas"]
        assert "Utilities" == categories["Internet"]

    def test_single_expense(self, client):
        """GET /api/expenses returns a single expense when only one exists."""
        csv_content = "description,amount,date,category\nCoffee,4.50,2026-02-01,Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "single.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses")
        assert resp.status_code == 200
        expenses = resp.get_json()
        assert 1 == len(expenses)
        assert "Coffee" == expenses[0]["description"]
        assert 4.50 == pytest.approx(expenses[0]["amount"])

    def test_expenses_have_auto_incremented_ids(self, seeded_client):
        """Each expense has a unique auto-incremented integer id."""
        resp = seeded_client.get("/api/expenses")
        data = resp.get_json()
        ids = [row["id"] for row in data]
        assert len(ids) == len(set(ids))
        for expense_id in ids:
            assert isinstance(expense_id, int)
            assert expense_id > 0

    def test_returns_list(self, client):
        """GET /api/expenses always returns a list."""
        resp = client.get("/api/expenses")
        assert isinstance(resp.get_json(), list)


class TestNormalizeDate:
    """Tests for the normalize_date helper."""

    def test_iso_format_unchanged(self):
        assert "2026-02-22" == normalize_date("2026-02-22")

    def test_slash_format_single_digit_month(self):
        assert "2026-02-22" == normalize_date("2/22/2026")

    def test_slash_format_double_digit_month(self):
        assert "2026-12-05" == normalize_date("12/05/2026")

    def test_dash_format_us(self):
        assert "2026-01-15" == normalize_date("01-15-2026")

    def test_whitespace_stripped(self):
        assert "2026-02-22" == normalize_date("  2/22/2026  ")

    def test_unknown_format_returned_as_is(self):
        assert "22.02.2026" == normalize_date("22.02.2026")


class TestUploadDateNormalization:
    """CSV upload should store dates in YYYY-MM-DD regardless of input format."""

    def test_slash_dates_normalized_on_upload(self, client):
        csv_content = "description,amount,date,category\nLunch,12.00,2/15/2026,Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "dates.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses")
        assert "2026-02-15" == resp.get_json()[0]["date"]

    def test_iso_dates_unchanged_on_upload(self, client):
        csv_content = "description,amount,date,category\nLunch,12.00,2026-02-15,Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "dates.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses")
        assert "2026-02-15" == resp.get_json()[0]["date"]


class TestAvailablePeriods:
    """The /api/expenses/periods endpoint should detect data in current periods."""

    def test_periods_with_current_year_data(self, client):
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        csv_content = f"description,amount,date,category\nTest,10.00,{date_str},Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "now.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/periods")
        periods = resp.get_json()
        assert periods["year"] is True

    def test_periods_empty_database(self, client):
        resp = client.get("/api/expenses/periods")
        periods = resp.get_json()
        assert periods["week"] is False
        assert periods["month"] is False
        assert periods["year"] is False

    def test_periods_with_slash_format_dates(self, client):
        from datetime import datetime
        now = datetime.now()
        date_str = f"{now.month}/{now.day}/{now.year}"
        csv_content = f"description,amount,date,category\nTest,10.00,{date_str},Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "slash.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/periods")
        periods = resp.get_json()
        assert periods["year"] is True


class TestTimeSeriesOffset:
    """The timeseries endpoint should support an offset parameter."""

    def test_month_offset_negative(self, client):
        """Offset -1 should return data for the previous month."""
        from datetime import datetime
        import calendar
        now = datetime.now()
        # Calculate previous month
        if now.month == 1:
            prev_year, prev_month = now.year - 1, 12
        else:
            prev_year, prev_month = now.year, now.month - 1
        prev_date = f"{prev_year}-{prev_month:02d}-10"
        csv_content = f"description,amount,date,category\nOld,25.00,{prev_date},Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "prev.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/timeseries?period=month&offset=-1")
        assert resp.status_code == 200
        ts = resp.get_json()
        days_in_prev = calendar.monthrange(prev_year, prev_month)[1]
        assert days_in_prev == len(ts)
        # Day 10 should have data
        assert ts[9]["total"] == pytest.approx(25.00)

    def test_year_offset_negative(self, client):
        """Offset -1 should return data for the previous year."""
        from datetime import datetime
        now = datetime.now()
        last_year_date = f"{now.year - 1}-06-15"
        csv_content = f"description,amount,date,category\nOld,50.00,{last_year_date},Travel\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "lastyear.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/timeseries?period=year&offset=-1")
        assert resp.status_code == 200
        ts = resp.get_json()
        assert 12 == len(ts)
        # June (index 5) should have data
        assert ts[5]["total"] == pytest.approx(50.00)

    def test_week_offset_negative(self, client):
        """Offset -1 should return data for the previous week."""
        from datetime import datetime, timedelta
        now = datetime.now()
        prev_week_monday = now - timedelta(days=now.weekday()) - timedelta(weeks=1)
        prev_monday_str = prev_week_monday.strftime("%Y-%m-%d")
        csv_content = f"description,amount,date,category\nOld,15.00,{prev_monday_str},Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "prevweek.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/timeseries?period=week&offset=-1")
        assert resp.status_code == 200
        ts = resp.get_json()
        assert 7 == len(ts)
        assert ts[0]["total"] == pytest.approx(15.00)

    def test_offset_zero_is_default(self, client):
        """Offset 0 should return the same as no offset."""
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        csv_content = f"description,amount,date,category\nNow,10.00,{date_str},Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "now.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp_default = client.get("/api/expenses/timeseries?period=month")
        resp_zero = client.get("/api/expenses/timeseries?period=month&offset=0")
        assert resp_default.get_json() == resp_zero.get_json()


class TestPeriodLabel:
    """The /api/expenses/period-label endpoint should return readable labels."""

    def test_month_label_current(self, client):
        from datetime import datetime
        now = datetime.now()
        expected = now.strftime("%B %Y")
        resp = client.get("/api/expenses/period-label?period=month&offset=0")
        assert resp.status_code == 200
        assert expected == resp.get_json()["label"]

    def test_year_label_current(self, client):
        from datetime import datetime
        now = datetime.now()
        resp = client.get("/api/expenses/period-label?period=year&offset=0")
        assert resp.status_code == 200
        assert str(now.year) == resp.get_json()["label"]

    def test_year_label_previous(self, client):
        from datetime import datetime
        now = datetime.now()
        resp = client.get("/api/expenses/period-label?period=year&offset=-1")
        assert resp.status_code == 200
        assert str(now.year - 1) == resp.get_json()["label"]

    def test_week_label_contains_dash(self, client):
        """Week labels should contain a date range separator."""
        resp = client.get("/api/expenses/period-label?period=week&offset=0")
        assert resp.status_code == 200
        label = resp.get_json()["label"]
        assert "–" in label or "-" in label

    def test_invalid_period(self, client):
        resp = client.get("/api/expenses/period-label?period=invalid")
        assert resp.status_code == 400


class TestTimeSeriesGapFilling:
    """The /api/expenses/timeseries endpoint should return all dates in the period."""

    def test_week_returns_all_seven_days(self, client):
        """Week period should return 7 entries even if only some days have data."""
        from datetime import datetime, timedelta
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        # Insert expense only on Monday of this week
        monday = start_of_week.strftime("%Y-%m-%d")
        csv_content = f"description,amount,date,category\nCoffee,5.00,{monday},Food\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "week.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/timeseries?period=week")
        assert resp.status_code == 200
        ts = resp.get_json()
        assert 7 == len(ts)
        # Monday should have data, other days should be 0
        assert ts[0]["total"] == pytest.approx(5.00)
        for entry in ts[1:]:
            assert entry["total"] == pytest.approx(0)

    def test_month_returns_all_days(self, client):
        """Month period should return one entry per day of the current month."""
        import calendar
        from datetime import datetime
        now = datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        # Insert one expense on the 1st
        first_day = now.strftime("%Y-%m-01")
        csv_content = f"description,amount,date,category\nRent,500.00,{first_day},Housing\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "month.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/timeseries?period=month")
        assert resp.status_code == 200
        ts = resp.get_json()
        assert days_in_month == len(ts)
        assert ts[0]["total"] == pytest.approx(500.00)

    def test_year_returns_all_twelve_months(self, client):
        """Year period should return 12 entries (one per month)."""
        from datetime import datetime
        now = datetime.now()
        jan_date = f"{now.year}-01-15"
        csv_content = f"description,amount,date,category\nSub,10.00,{jan_date},Services\n"
        data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "year.csv")}
        client.post("/api/expenses/upload", data=data, content_type="multipart/form-data")

        resp = client.get("/api/expenses/timeseries?period=year")
        assert resp.status_code == 200
        ts = resp.get_json()
        assert 12 == len(ts)
        # January should have data
        assert ts[0]["total"] == pytest.approx(10.00)
        # Other months should be 0
        for entry in ts[1:]:
            assert entry["total"] == pytest.approx(0)
