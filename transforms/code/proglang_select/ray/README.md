# Programming Language Select 

Please see the set of
[transform project conventions](../../../README.md)
for details on general project conventions, transform configuration,
testing and IDE set up.

## Summary
This project enables the [python malware transform](../python) to be run in a Ray runtime.
Please see the [python project](../python) for details on the transform implementation and use.

## Configuration and Command Line Options

Transform configuration options are the same as the base python transform.

## Running

### Launched Command Line Options
In addition to those available to the transform as defined in [here](../python/README.md),
the set of
[launcher options](../../../../data-processing-lib/doc/launcher-options.md) are available.


### Running the samples
To run the samples, use the following `make` targets

* `run-cli-sample` - runs src/proglang_select_transform_ray.py using command line args
* `run-local-ray-sample` - runs src/proglang_select_local_ray.py

These targets will activate the virtual environment and set up any configuration needed.
Use the `-n` option of `make` to see the detail of what is done to run the sample.

For example, 
```shell
make run-cli-sample
...
```
Then 
```shell
ls output
```
To see results of the transform.

### Transforming data using the transform image

To use the transform image to transform your data, please refer to the 
[running images quickstart](../../../../doc/quick-start/run-transform-image.md),
substituting the name of this transform image and runtime as appropriate.
