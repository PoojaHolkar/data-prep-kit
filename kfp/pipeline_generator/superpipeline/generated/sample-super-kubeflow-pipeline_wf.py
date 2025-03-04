# NOTE: This file is auto generated by Pipeline Generator.
import os

import kfp.compiler as compiler
import kfp.components as comp
import kfp.dsl as dsl
from workflow_support.compile_utils import (
    DEFAULT_KFP_COMPONENT_SPEC_PATH,
    ONE_HOUR_SEC,
    ONE_WEEK_SEC,
    ComponentUtils,
)


# path to kfp component specifications files
component_spec_path = os.getenv("KFP_COMPONENT_SPEC_PATH", DEFAULT_KFP_COMPONENT_SPEC_PATH)
# For every sub workflow we need a separate components, that knows about this subworkflow.
run_doc_id_op = comp.load_component_from_file(component_spec_path + "executeSubWorkflowComponent.yaml")
run_ededup_op = comp.load_component_from_file(component_spec_path + "executeSubWorkflowComponent.yaml")
doc_id_image = "quay.io/dataprep1/data-prep-kit/doc_id-ray:latest`"
ededup_image = "quay.io/dataprep1/data-prep-kit/ededup-ray:latest"

# Pipeline to invoke execution on remote resource
@dsl.pipeline(
    name="sample-super-kubeflow-pipeline",
    description="Pipeline to show how to run combine several transformer pipelines",
)
def super_pipeline(
    p1_orch_doc_id_name: str = "doc_id_wf",
    p1_orch_ededup_name: str = "ededup_wf",
    p2_pipeline_runtime_pipeline_id: str = "pipeline_id",
    p2_pipeline_ray_head_options: str = '{"cpu": 1, "memory": 4, "image_pull_secret": ""}',
    p2_pipeline_ray_worker_options: str = '{"replicas": 2, "max_replicas": 2, "min_replicas": 2, "cpu": 2, "memory": 4, "image_pull_secret": ""}',
    p2_pipeline_server_url: str = "http://kuberay-apiserver-service.kuberay.svc.cluster.local:8888",
    p2_pipeline_additional_params: str = '{"wait_interval": 2, "wait_cluster_ready_tmout": 400, "wait_cluster_up_tmout": 300, "wait_job_ready_tmout": 400, "wait_print_tmout": 30, "http_retries": 5, "delete_cluster_delay_minutes": 0}',
    p2_pipeline_runtime_code_location: str = '{"github": "github", "commit_hash": "12345", "path": "path"}',
    p2_pipeline_input_parent_path: str = "test/doc_id/input/",
    p2_pipeline_output_parent_path: str = "test/super/output/",
    p2_pipeline_parent_path_suffix: str = "",
    p2_pipeline_data_s3_access_secret: str = "s3-secret",
    # doc_id step parameters
    p3_name: str = "doc_id",
    p3_skip: bool = False,
    p3_doc_id_doc_column: str = "contents",
    p3_doc_id_hash_column: str = "hash_column",
    p3_doc_id_int_column: str = "int_id_column",
    p3_doc_id_start_id: int = 0,
    p3_overriding_params: str = '{"ray_worker_options": {"image": "'
    + doc_id_image
    + '"}, "ray_head_options": {"image": "'
    + doc_id_image
    + '"}}',
    # ededup step parameters
    p4_name: str = "ededup",
    p4_skip: bool = False,
    p4_ededup_doc_column: str = "contents",
    p4_ededup_hash_cpu: float = 0.5,
    p4_ededup_use_snapshot: bool = False,
    p4_ededup_snapshot_directory: str = None,
    p4_ededup_n_samples: int = 10,
    p4_overriding_params: str = '{"ray_worker_options": {"image": "'
    + ededup_image
    + '"}, "ray_head_options": {"image": "'
    + ededup_image
    + '"}}',
):

    # get all arguments
    args = locals()
    orch_host = "http://ml-pipeline:8888"

    def _set_component(op: dsl.BaseOp, displaied_name: str, prev_op: dsl.BaseOp = None):
        # set the sub component UI name
        op.set_display_name(displaied_name)

        # Add pod labels
        op.add_pod_label("app", "ml-pipeline").add_pod_label("component", "data-science-pipelines")
        # No cashing
        op.execution_options.caching_strategy.max_cache_staleness = "P0D"
        # image pull policy
        op.set_image_pull_policy("Always")
        # Set the timeout for each task to one week (in seconds)
        op.set_timeout(ONE_WEEK_SEC)
        if prev_op is not None:
            op.after(prev_op)

    doc_id = run_doc_id_op(
        name=p1_orch_doc_id_name, prefix="p3_", params=args, host=orch_host, input_folder=p2_pipeline_input_parent_path
    )
    _set_component(doc_id, "doc_id")
    ededup = run_ededup_op(
        name=p1_orch_ededup_name, prefix="p4_", params=args, host=orch_host, input_folder=doc_id.output
    )
    _set_component(ededup, "ededup", doc_id)

    # Configure the pipeline level to one week (in seconds)
    dsl.get_pipeline_conf().set_timeout(ONE_WEEK_SEC)


if __name__ == "__main__":
    # Compiling the pipeline
    compiler.Compiler().compile(super_pipeline, __file__.replace(".py", ".yaml"))
