import argparse
import io
import os
import uuid
import zipfile
from datetime import datetime
from multiprocessing import Pool
from typing import Any, List

import pandas as pd
import pyarrow as pa
from data_processing.data_access import DataAccess, DataAccessFactory
from data_processing.utils import TransformUtils


def zip_to_table(data_access: DataAccess, file_path) -> pa.table:
    """
    Extracts contents from a ZIP file and converts them into a PyArrow table.

    :param data_access: DataAccess object for accessing data
    :param file_path: Path to the ZIP file
    :return: PyArrow table containing extracted data
    """
    data = []
    zip_name = os.path.basename(file_path)
    compressed_zip_bytes = data_access.get_file(file_path)

    with zipfile.ZipFile(io.BytesIO(bytes(compressed_zip_bytes))) as opened_zip:
        # Loop through each file member in the ZIP archive
        for member in opened_zip.infolist():
            if not member.is_dir():
                with opened_zip.open(member) as file:
                    try:
                        # Read the content of the file
                        content_bytes = file.read()
                        # Decode the content
                        content_string = TransformUtils.decode_content(content_bytes)
                        if content_string and len(content_string) > 0:
                            data.append(
                                {
                                    "file_path": member.filename,
                                    "document": zip_name,
                                    "contents": content_string,
                                    "document_id": str(uuid.uuid4()),
                                    "ext": TransformUtils.get_file_extension(
                                        member.filename
                                    ),
                                    "hash": TransformUtils.str_to_hash(content_string),
                                    "size": TransformUtils.deep_get_size(
                                        content_string
                                    ),
                                    "date_acquired": datetime.now().isoformat(),
                                }
                            )
                        else:
                            raise Exception("No contents decoded")

                    except Exception as e:
                        print(f" skipping {member.filename} Error: {str(e)}")

    table = pa.Table.from_pandas(pd.DataFrame(data))
    return table


def raw_to_parquet(
    data_access_factory: DataAccessFactory, file_path
) -> tuple[bool, dict[str:Any]]:
    """
    Converts raw data file (ZIP) to Parquet format and saves it.

    :param data_access_factory: DataAccessFactory object for accessing data
    :param file_path: Path to the raw data file
    :return: Tuple indicating success (True/False) and additional metadata
    """

    try:
        # Create a DataAccess object for accessing data
        data_access = data_access_factory.create_data_access()

        # Get the file extension
        ext = TransformUtils.get_file_extension(file_path)
        if ext == ".zip":
            table = zip_to_table(data_access, file_path)
        else:
            raise Exception(f"Got {ext} file, not supported")

        # Get the output file name for the Parquet file
        output_file_name = data_access.get_output_location(file_path).replace(
            ".zip", ".parquet"
        )
        # Save the PyArrow table as a Parquet file and get metadata
        print("output_file_name", output_file_name)
        metadata = data_access.save_table(output_file_name, table)
        if metadata[1]:
            return (
                True,
                {
                    "path": file_path,
                    "bytes_in_memory": metadata[0],
                    "row_count": table.num_rows,
                },
            )
        else:
            raise Exception("Failed to upload")

    except Exception as e:
        return (False, {"path": file_path, "error": str(e)})


def generate_stats(metadata: list) -> dict[str, Any]:
    """
    Generates statistics based on processing metadata.

    :param metadata: List of tuples containing processing metadata
    :return: Dictionary containing processing statistics
    """
    success = 0
    sucess_details = []
    failures = 0
    failure_details = []
    for m in metadata:
        if m[0] == True:
            success += 1
            sucess_details.append(m[1])
        else:
            failures += 1
            failure_details.append(m[1])

    # Create DataFrame from success details to calculate total bytes in memory
    success_df = pd.DataFrame(
        sucess_details, columns=["path", "bytes_in_memory", "row_count"]
    )
    total_bytes_in_memory = success_df["bytes_in_memory"].sum()
    total_row_count = success_df["row_count"].sum()

    return {
        "total_files_given": len(metadata),
        "total_files_processed": success,
        "total_files_failed_to_processed": failures,
        "total_no_of_rows": int(total_row_count),
        "total_bytes_in_memory": int(total_bytes_in_memory),
        "failure_details": failure_details,
    }


def run():
    parser = argparse.ArgumentParser(description="raw-data-to-parquet")

    data_access_factory = DataAccessFactory()
    data_access_factory.add_input_params(parser)

    args = parser.parse_args()
    data_access_factory.apply_input_params(args)

    # Creates a DataAccess object for accessing data.
    data_access = data_access_factory.create_data_access()

    # Retrieves file paths of files from the input folder.
    file_paths = data_access.get_folder_files(data_access.input_folder, ["zip"], False)

    if len(file_paths) != 0:
        print(f"Number of files is {len(file_paths)} ")
        metadata = []
        with Pool() as p:
            # Processes each file concurrently
            results = p.starmap_async(
                raw_to_parquet,
                [
                    (
                        data_access_factory,
                        file_path,
                    )
                    for file_path in file_paths.keys()
                ],
            )
            metadata = results.get()
        # Generates statistics based on the processing metadata
        stats = generate_stats(metadata)
        print("processing stats generated", stats)

        # Saves the processing statistics
        print("Metadata file stored - response:", data_access.save_job_metadata(stats))
