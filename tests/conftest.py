"""
Pytest fixtures for the weekly-analytics project.

This module contains fixtures that can be used across test modules.
"""

import os
import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from models.data_models import FunnelEntry, FunnelData


@pytest.fixture
def sample_excel_path() -> str:
    """
    Return a path to a sample Excel file for testing.

    In a real test environment, this would point to a test file.
    For the test suite to work, this file must exist.
    """
    # For testing, you would create or use a dedicated test file
    # Here we'll use a path that will be replaced by a mock
    return os.path.join(os.path.dirname(__file__), "test_data", "sample_funnel.xlsx")


@pytest.fixture
def mock_excel_data() -> Dict[str, pd.DataFrame]:
    """
    Create a mock DataFrame similar to what would be read from an Excel file.
    """
    # Create a sample DataFrame representing funnel data
    data = {
        "Company": ["ABC Corp", "XYZ Ltd", "123 Inc"],
        "Project": ["Website Redesign", "Mobile App", "Data Migration"],
        "Value": [50000.0, 75000.0, 100000.0],
        "Probability (%)": [80.0, 50.0, 30.0],
        "Status": ["High", "Medium", "Low"],
        "Start Date": [
            datetime(2025, 1, 1),
            datetime(2025, 2, 1),
            datetime(2025, 3, 1),
        ],
        "Expected Close": [
            datetime(2025, 3, 31),
            datetime(2025, 6, 30),
            datetime(2025, 9, 30),
        ],
        "Notes": [
            "Redesign of corporate website",
            "Mobile app development",
            "Data migration project",
        ],
        "Last Updated": [
            datetime(2025, 1, 15),
            datetime(2025, 2, 15),
            datetime(2025, 3, 15),
        ],
    }

    # Return a dictionary with sheet names as keys and DataFrames as values
    return {"Sheet1": pd.DataFrame(data)}


@pytest.fixture
def sample_funnel_entries() -> List[FunnelEntry]:
    """
    Create sample FunnelEntry objects for testing.
    """
    entries = [
        FunnelEntry(
            company_name="ABC Corp",
            project_name="Website Redesign",
            value=50000.0,
            probability=80.0,
            status="High",
            start_date=datetime(2025, 1, 1),
            expected_close_date=datetime(2025, 3, 31),
            notes="Redesign of corporate website",
            last_updated=datetime(2025, 1, 15),
        ),
        FunnelEntry(
            company_name="XYZ Ltd",
            project_name="Mobile App",
            value=75000.0,
            probability=50.0,
            status="Medium",
            start_date=datetime(2025, 2, 1),
            expected_close_date=datetime(2025, 6, 30),
            notes="Mobile app development",
            last_updated=datetime(2025, 2, 15),
        ),
        FunnelEntry(
            company_name="123 Inc",
            project_name="Data Migration",
            value=100000.0,
            probability=30.0,
            status="Low",
            start_date=datetime(2025, 3, 1),
            expected_close_date=datetime(2025, 9, 30),
            notes="Data migration project",
            last_updated=datetime(2025, 3, 15),
        ),
    ]
    return entries


@pytest.fixture
def sample_funnel_data(sample_funnel_entries, sample_excel_path) -> FunnelData:
    """
    Create a sample FunnelData object for testing.
    """
    return FunnelData(
        entries=sample_funnel_entries,
        extraction_date=datetime(2025, 4, 16),
        source_file=sample_excel_path,
        sheet_name="Sheet1",
    )


@pytest.fixture
def temp_excel_file(tmp_path, mock_excel_data):
    """
    Create a temporary Excel file for testing.

    Returns:
        Path to the temporary Excel file
    """
    # Create test_data directory if it doesn't exist
    test_data_dir = tmp_path / "test_data"
    test_data_dir.mkdir(exist_ok=True)

    # Create the Excel file
    file_path = test_data_dir / "sample_funnel.xlsx"

    # Write the mock data to the Excel file
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in mock_excel_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return str(file_path)


@pytest.fixture
def temp_excel_files(tmp_path, mock_excel_data):
    """
    Create multiple temporary Excel files for testing folder scanning.

    Returns:
        Tuple of (folder_path, list_of_file_paths)
    """
    # Create test_data directory
    test_data_dir = tmp_path / "test_data"
    test_data_dir.mkdir(exist_ok=True)

    file_paths = []

    # Create multiple Excel files
    for i in range(3):
        file_path = test_data_dir / f"sample_funnel_{i}.xlsx"

        # Write the mock data to the Excel file
        with pd.ExcelWriter(file_path) as writer:
            for sheet_name, df in mock_excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        file_paths.append(str(file_path))

    # Also create a non-Excel file to test filtering
    txt_file = test_data_dir / "not_an_excel.txt"
    txt_file.write_text("This is not an Excel file")

    return str(test_data_dir), file_paths
