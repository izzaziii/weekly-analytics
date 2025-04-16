import pandas as pd
import os
import glob
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

from models.data_models import (
    FunnelData,
    FunnelEntry,
    ExcelFileMetadata,
    ExcelSheetMetadata,
)
from utils.logging_utils import ContextLogger


class ExcelExtractor:
    """
    Class for extracting data from Excel files.
    """

    def __init__(
        self, file_path: str = "Z:\\FUNNEL with PROBABILITY TRACKING_Teefa.xlsx"
    ):
        """
        Initialize the Excel extractor with the path to the Excel file.

        Args:
            file_path: Path to the Excel file to extract data from
        """
        self.file_path = file_path
        self.logger = ContextLogger("extraction")
        self.logger.add_context(file_path=file_path)

    def extract_data(self, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        Extract data from the Excel file.

        Args:
            sheet_name: Name of the sheet to extract data from
            **kwargs: Additional arguments to pass to pandas.read_excel

        Returns:
            DataFrame containing the extracted data

        Raises:
            FileNotFoundError: If the file cannot be found
            PermissionError: If VPN connection is needed but not active
            Exception: For other errors during extraction
        """
        if sheet_name:
            self.logger.add_context(sheet_name=sheet_name)

        self.logger.info(f"Extracting data from Excel file")

        try:
            if not os.path.exists(self.file_path):
                self.logger.error(f"Excel file not found")
                raise FileNotFoundError(f"Excel file not found: {self.file_path}")

            df = pd.read_excel(self.file_path, sheet_name=sheet_name, **kwargs)
            self.logger.info(f"Successfully extracted data with shape {df.shape}")
            return df

        except FileNotFoundError as e:
            self.logger.error(f"Excel file not found", exc_info=True)
            raise FileNotFoundError(
                f"Excel file not found: {self.file_path}. Make sure the path is correct."
            )

        except PermissionError as e:
            self.logger.error(
                f"Permission error when accessing Excel file", exc_info=True
            )
            raise PermissionError(
                f"Cannot access {self.file_path}. Please check your VPN connection and try again."
            )

        except Exception as e:
            self.logger.error(
                f"Error extracting data from Excel file: {str(e)}", exc_info=True
            )
            raise Exception(f"Error extracting data from Excel file: {str(e)}")

    def get_sheet_names(self) -> list:
        """
        Get the names of all sheets in the Excel file.

        Returns:
            List of sheet names

        Raises:
            Same exceptions as extract_data
        """
        self.logger.info(f"Getting sheet names from Excel file")

        try:
            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names
            self.logger.info(f"Found {len(sheet_names)} sheets")
            return sheet_names

        except FileNotFoundError:
            self.logger.error(f"Excel file not found", exc_info=True)
            raise FileNotFoundError(
                f"Excel file not found: {self.file_path}. Make sure the path is correct."
            )

        except PermissionError:
            self.logger.error(
                f"Permission error when accessing Excel file", exc_info=True
            )
            raise PermissionError(
                f"Cannot access {self.file_path}. Please check your VPN connection and try again."
            )

        except Exception as e:
            self.logger.error(f"Error reading Excel file: {str(e)}", exc_info=True)
            raise Exception(f"Error reading Excel file: {str(e)}")

    def get_file_metadata(self) -> ExcelFileMetadata:
        """
        Get metadata about the Excel file.

        Returns:
            ExcelFileMetadata object with file metadata

        Raises:
            Same exceptions as extract_data
        """
        self.logger.info(f"Getting metadata for Excel file")

        try:
            if not os.path.exists(self.file_path):
                self.logger.error(f"Excel file not found")
                raise FileNotFoundError(f"Excel file not found: {self.file_path}")

            # Get file metadata
            file_stats = os.stat(self.file_path)
            last_modified = datetime.fromtimestamp(file_stats.st_mtime)
            file_size = file_stats.st_size

            self.logger.info(
                f"File size: {file_size} bytes, Last modified: {last_modified}"
            )

            # Get sheet metadata
            sheet_metadata_list = []
            excel_file = pd.ExcelFile(self.file_path)

            for sheet_name in excel_file.sheet_names:
                self.logger.info(f"Processing metadata for sheet: {sheet_name}")

                # Read just the header row to get column names
                df_header = pd.read_excel(
                    self.file_path, sheet_name=sheet_name, nrows=0
                )
                column_headers = df_header.columns.tolist()

                # Get row and column counts
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                row_count = len(df)
                column_count = len(df.columns)

                self.logger.info(
                    f"Sheet {sheet_name}: {row_count} rows, {column_count} columns"
                )

                sheet_metadata = ExcelSheetMetadata(
                    sheet_name=sheet_name,
                    row_count=row_count,
                    column_count=column_count,
                    column_headers=column_headers,
                )
                sheet_metadata_list.append(sheet_metadata)

            metadata = ExcelFileMetadata(
                file_path=self.file_path,
                file_size=file_size,
                last_modified=last_modified,
                sheets=sheet_metadata_list,
            )

            self.logger.info(
                f"Successfully gathered metadata for {len(sheet_metadata_list)} sheets"
            )
            return metadata

        except FileNotFoundError:
            self.logger.error(f"Excel file not found", exc_info=True)
            raise FileNotFoundError(
                f"Excel file not found: {self.file_path}. Make sure the path is correct."
            )

        except PermissionError:
            self.logger.error(
                f"Permission error when accessing Excel file", exc_info=True
            )
            raise PermissionError(
                f"Cannot access {self.file_path}. Please check your VPN connection and try again."
            )

        except Exception as e:
            self.logger.error(f"Error getting file metadata: {str(e)}", exc_info=True)
            raise Exception(f"Error getting file metadata: {str(e)}")

    def extract_validated_data(
        self, sheet_name: Optional[str] = None, mapping: Dict[str, str] = None
    ) -> FunnelData:
        """
        Extract data from Excel and validate it using Pydantic models.

        Args:
            sheet_name: Name of the sheet to extract data from
            mapping: Dictionary mapping Excel column names to FunnelEntry field names

        Returns:
            FunnelData object with validated data

        Raises:
            ValueError: If data validation fails
            Other exceptions same as extract_data
        """
        context = {"sheet_name": sheet_name} if sheet_name else {}
        self.logger.add_context(**context)
        self.logger.info(f"Extracting and validating data")

        try:
            # Default mapping if none provided
            if mapping is None:
                mapping = {
                    "Company": "company_name",
                    "Project": "project_name",
                    "Value": "value",
                    "Probability (%)": "probability",
                    "Status": "status",
                    "Start Date": "start_date",
                    "Expected Close": "expected_close_date",
                    "Notes": "notes",
                    "Last Updated": "last_updated",
                }
                self.logger.info(f"Using default column mapping")
            else:
                self.logger.info(f"Using custom column mapping")

            # Extract raw data
            df = self.extract_data(sheet_name=sheet_name)
            self.logger.info(f"Extracted {len(df)} rows of raw data")

            # Rename columns according to mapping
            df_mapped = df.rename(
                columns={k: v for k, v in mapping.items() if k in df.columns}
            )

            mapped_columns = [k for k in mapping.keys() if k in df.columns]
            self.logger.info(f"Mapped columns: {', '.join(mapped_columns)}")

            # Convert DataFrame to list of dictionaries
            records = df_mapped.to_dict(orient="records")

            # Create and validate FunnelEntry objects
            entries = []
            validation_errors = []

            for i, record in enumerate(records):
                try:
                    # Filter out None/NaN values to avoid validation errors for optional fields
                    cleaned_record = {k: v for k, v in record.items() if pd.notna(v)}
                    entry = FunnelEntry(**cleaned_record)
                    entries.append(entry)
                except Exception as e:
                    error_msg = f"Row {i + 2}: {str(e)}"
                    validation_errors.append(error_msg)
                    self.logger.warning(f"Validation error: {error_msg}")

            if validation_errors:
                self.logger.error(f"Found {len(validation_errors)} validation errors")
                raise ValueError(
                    f"Data validation errors: {'; '.join(validation_errors)}"
                )

            # Create FunnelData object
            funnel_data = FunnelData(
                entries=entries,
                extraction_date=datetime.now(),
                source_file=self.file_path,
                sheet_name=sheet_name,
            )

            self.logger.info(
                f"Successfully validated {len(entries)} entries with total value {funnel_data.total_value}"
            )
            return funnel_data

        except Exception as e:
            if isinstance(e, ValueError) and "Data validation errors" in str(e):
                # Already logged individual validation errors above
                raise
            self.logger.error(
                f"Error extracting and validating data: {str(e)}", exc_info=True
            )
            raise Exception(f"Error extracting and validating data: {str(e)}")

    def scan_folder_for_excel_files(
        self, folder_path: str, pattern: str = "*.xlsx"
    ) -> List[str]:
        """
        Scan a folder for Excel files matching the given pattern.

        Args:
            folder_path: Path to the folder to scan
            pattern: Glob pattern for matching files (default: "*.xlsx")

        Returns:
            List of file paths

        Raises:
            FileNotFoundError: If the folder cannot be found
            PermissionError: If access is denied
        """
        self.logger.add_context(folder_path=folder_path, pattern=pattern)
        self.logger.info(f"Scanning folder for Excel files")

        try:
            if not os.path.exists(folder_path):
                self.logger.error(f"Folder not found")
                raise FileNotFoundError(f"Folder not found: {folder_path}")

            if not os.path.isdir(folder_path):
                self.logger.error(f"Not a directory")
                raise ValueError(f"Not a directory: {folder_path}")

            # Use glob to find all files matching the pattern
            file_paths = glob.glob(os.path.join(folder_path, pattern))
            self.logger.info(f"Found {len(file_paths)} Excel files")

            # Log the found files
            for file_path in file_paths:
                self.logger.debug(f"Found file: {file_path}")

            return file_paths

        except FileNotFoundError:
            self.logger.error(f"Folder not found", exc_info=True)
            raise FileNotFoundError(
                f"Folder not found: {folder_path}. Make sure the path is correct."
            )

        except PermissionError:
            self.logger.error(f"Permission error when accessing folder", exc_info=True)
            raise PermissionError(
                f"Cannot access {folder_path}. Please check your VPN connection and permissions."
            )

        except Exception as e:
            self.logger.error(
                f"Error scanning folder for Excel files: {str(e)}", exc_info=True
            )
            raise Exception(f"Error scanning folder for Excel files: {str(e)}")
