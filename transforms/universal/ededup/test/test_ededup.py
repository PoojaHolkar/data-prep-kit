# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os
from typing import Tuple

from data_processing.test_support import get_tables_in_folder
from data_processing.test_support.transform import AbstractTableTransformTest
from dpk_ededup.transform_base import (
    HashFilter,
    doc_column_name_key,
    int_column_name_key,
)
from dpk_ededup.transform_python import EdedupTransform


class TestEdedupTransform(AbstractTableTransformTest):
    """
    Extends the super-class to define the test data for the tests defined there.
    The name of this class MUST begin with the word Test so that pytest recognizes it as a test class.
    """

    def get_test_transform_fixtures(self) -> list[Tuple]:
        basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test-data"))
        input_dir = os.path.join(basedir, "input")
        input_tables = get_tables_in_folder(input_dir)
        expected_metadata_list = [{"result_documents": 3, "source_documents": 5}, {}]
        config = {doc_column_name_key: "contents", int_column_name_key: "document_id", "filter": HashFilter({})}
        expected_tables = get_tables_in_folder(os.path.join(basedir, "expected"))
        return [
            (EdedupTransform(config), input_tables, expected_tables, expected_metadata_list),
        ]
