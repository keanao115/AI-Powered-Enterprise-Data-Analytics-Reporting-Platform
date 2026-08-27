import sys
import os
import pytest

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from seed.seed_data import seed_synthetic_analytics_database
from app.core.database import get_analytics_db_path

@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    db_path = get_analytics_db_path()
    seed_synthetic_analytics_database(db_path)
