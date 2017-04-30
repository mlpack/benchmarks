# Machine Learning Benchmark Scripts

Develop branch build status:

[![Build Status](http://masterblaster.mlpack.org/job/benchmark%20-%20checkout%20-%20all%20nodes//badge/icon)](http://masterblaster.mlpack.org/job/benchmark%20-%20checkout%20-%20all%20nodes//)

Visit http://www.mlpack.org/benchmark.html to see our latest results.

This repository contains a collection of benchmark scripts for various machine learning libraries. The scripts serves as an infrastructure for measuring and comparing the performance, of different algorithms and libraries on various datasets using visual tools and different metrics. It aims to give the machine learning community a streamlined tool to get information on those changesets that may have caused speedups or slowdowns.

The system has several key attributes that lead to its highly and easily customizable nature. It makes extensive use of the Python standard library and the YAML file format to provide a very easy way to efficiently run the performance measurements on custom setups with different operating systems. The tools and metrics used for the visualization are highly flexible, e.g. with one line you can measure the size of your program’s stack, get the variance or standard deviation of the measurements. The architecture is easily maintainable since each part is a single module. with the results that the framework can be easily integrated in the main workflow.


Quick links to this file:
* [Prerequisites](#prerequisites)
* [Running](#running)
* [Directory Structure](#directory-structure)
* [Getting the datasets](#getting-the-datasets)
* [Configuration](#configuration)
* [Competing libraries](#competing-libraries)
* [Citation details](#citation-details)

## Prerequisites

* **[Python 3.3+](http://www.python.org "Python Website")**: The main benchmark script is written with the programming language python: The benchmark script by default uses the version of Python on your path.
* **[Python-yaml](http://pyyaml.org "Python-yaml Website")**: PyYAML is a YAML parser and emitter for Python. We've picked YAML as the configuration file format for specifying the structure for the project.
* **[SQLite](http://www.sqlite.org "SQLite Website")** (**Optional**): SQLite is a lightweight disk-based database that doesn't require a separate server process. We use the python built-in SQLite database to save the benchmark results.
* **[Valgrind](http://valgrind.org "Valgrind Website")** (**Optional**): Valgrind is a suite of tools for debugging and profiling. This package is only needed if you want to run the memory benchmarks.
* **[python-xmlrunner](https://github.com/lamby/pkg-python-xmlrunner "python-xmlrunner github")** (**Optional**): The xmlrunner module is a unittest test runner that can save test results to XML files. This package is only needed if you want to run the tests.

## Running

Benchmarks are run with the `make` command.

* `make run`        -- Perform the benchmark.
* `make memory`     -- Get memory profiling information.
* `make test`       -- Test the configuration file. Check for correct syntax and then try to open files referred in the configuration file.
* `make scripts`    -- Make additional scripts.


Running `make` with no additional arguments except the task option will use the default parameters specified in the `Makefile` (e.g. config file). You can set an alternate config file with the `CONFIG` flag. You can also run a single benchmark script with the `BLOCK` and `METHODBLOCK` flag. Use `make help` to see a full list of options.


## Running the scripts

#### Benchmarking and save the Output
By default running the benchmarks will produce some logging to standard out. To save the results in the databse, set the `LOG` flag. If you wanted to run all scripts and save the output in the database located in the reports directory use the following command line:

    $ make run LOG=True

#### Benchmarking a Single Method

If you are making changes to any of the scripts, or if you simply want to benchmark a single method, you can benchmark the method with the `METHODBLOCK` flag. For example, if you only wanted to benchmark all K-Means scripts use the following command line:

    $ make run METHODBLOCK=KMEANS

You can also run a list of methods with the following command line:

    $ make run METHODBLOCK=KMEANS,ALLKNN

#### Benchmarking a Single Library

If you are making changes to any of the scripts for a specified library, or if you simply want to benchmark a single library, you can benchmark the library with the `BLOCK` flag. For example, if you only wanted to benchmark all MLPACK scripts use the following command line:

    $ make run BLOCK=mlpack

You can also benchmark a list of libraries with the following command line:

    $ make run BLOCK=mlpack,shogun

#### Benchmarking a Single Libary and a Single Method

You can also combine the `BLOCK` and `METHODBLOCK` flag to benchmark single methods for a specific libraries. For example, if you only wanted to benchmark the MLPACK and Shogun, K-Means scripts use the following command line:

    $ make run BLOCK=mlpack,shogun METHODBLOCK=KMEANS

#### Update Benchmark Results

In case of an failure you can update the last benchmark results stored in the database. You can combine the other flag to specifie the libary or method you like to update. For example, if you only wanted to update the MLPACK, HMM script use the following command line:

    $ make run UPDATE=True BLOCK=mlpack METHODBLOCK=HMM

## Directory Structure

Source directories

    ./                      -- config file and the Makefile to start the benchmarks
    ./datasets              -- several datasets which are used for the benchmarks
    ./util                  -- common files used by several scripts
    ./tests                 -- source code for tests
    ./benchmark             -- executables for the different benchmarks tasks
    ./methods/<library>     -- source code for scripts

Working directories

    ./
    ./reports               -- output from the memory_benchmark executable
    ./reports/benchmark.db  -- database for benchmark runs

## Getting the datasets

The datasets are kept in a separate repository as a git submodule. You can get the datasets by updating the submodule from within your working directory.

    $ git submodule update --init

This will checkout the datasets from the benchmark-datasets repository and place them in your working directory.

## Configuration
The benchmark script requires several parameters that specify the benchmark runs, the parameters of the graph to be generated, etc.

For complete details, refer the wiki page : https://github.com/zoq/benchmarks/wiki/Google-Summer-of-Code-2014-:-Improvement-of-Automatic-Benchmarking-System

The benchmark script comes with a default configuration. The default configuration will run all available benchmarks. This configuration can take quite a while to run (more than two weeks), so it would be best to adjust the configuration to to suite your time constraints. You can also command line options to selectively run benchmarks the options are described below.


### General Block

The general block contains some settings that control the benchmark itself, and the output of the reports page.

```yaml
library: general
settings:
    timeout: 9000
    database: 'reports/benchmark.db'
    keepReports: 20
    topChartColor: '#F3F3F3'
    chartColor: '#FFFFFF'
    textColor: '#6E6E6E'
```
* `timeout`: Limit the execution time for the benchmarks. This can be an easy way to keep a benchmark from eating up all the execution time.
* `database`: The location of the databse. If there is no database at the specified location, the script creates a new database.
* `keepReports`: Limit the report pages. This can be an easy way to keep a benchmark from eating up all your space.
* `topChartColor`: The background color of the top chart.
* `chartColor`: The background color of the charts.
* `textColor`: The font color of the charts.


### Library Block

The libary block contains some settings that control the specified benchmark scripts.

```yaml
library: mlpack
methods:
    PCA:
        run: ['timing', 'metric', 'bootstrap']
        script: methods/mlpack/pca.py
        format: [csv, txt]
        datasets:
            - files: [['datasets/iris_train.csv', 'datasets/iris_test.csv', 'datasets/iris_labels.csv']]

            - files: [['datasets/wine_train.csv', 'datasets/wine_test.csv', 'datasets/wine_labels.csv']]
              options: '-d 2'
    NMF:
        run: []
        script: methods/mlpack/nmf.py
        format: [csv, txt]
        datasets:
            - files: [['datasets/iris_train.csv', 'datasets/iris_test.csv', 'datasets/iris_labels.csv']]
              options: '-r 6 -s 42 -u multdist'
```

| **library**  |  |
| :------------ | :----------- |
| Description     | A name to identify the library. The name is also used for the output, for this reason it should be avoided to choose a name with more than 23 characters. |
| Syntax | `library: name` |
| Required | Yes |
| **script** | |
| Description | Path to the current method which should be tested. You can use the relative path from the benchmark root folder, a absolute path or a symlink. |
| Syntax | `script: name` |
| Required | Yes |
| **files** | |
| Description | List of datasets for this method. You can use the relative path from the benchmark root folder, a absolute path or a symlink. Requires a method more than one data set, you should add the data sets in an extra list. |
| Syntax | `files: [...] or [ [...] ]` |
| Required | Yes |
| **run** | |
| Description | List of benchmark tasks for this method. |
| Syntax | `run: ['timing', 'metrics']` |
| Default | `[]` |
| Required | No |
| **iterations** | |
| Description | The number of executions for this method. It is recommended to set the value higher than one in order to obtain meaningful results. |
| Syntax | `iterations: number` |
| Default | `3` |
| Required | No |
| **format** | |
| Description | A array of supported file formats for this method. If this data set isn't available in this format, the benchmark script tries to convert the data set. |
| Syntax | `format: [...]` |
| Required | No |
| **options** | |
| Description | description  The string contains options for this method. The string is passed when the script is started. |
| Syntax | `options: String` |
| Default   | `None` |
| Required | No |

#### Minimal Configuration

The configuration described here is the smallest possible configuration. The configuration combines all required options to benchmark a method.

```yaml
# MLPACK:
# A Scalable C++  Machine Learning Library
library: mlpack
methods:
    PCA:
        script: methods/mlpack/pca.py
        format: [csv, txt, hdf5, bin]
        datasets:
            - files: ['isolet.csv']
```

In this case we benchmark the pca method located in methods/mlpack/pca.py and use the isolet dataset. The pca method supports the following formats txt, csv, hdf5 and bin. The benchmark script use the default values for the non-specified values.

#### Full Configuration

Combining all the elements discussed above results in the following configuration, which should be placed typically in the config.yaml.

```yaml
# MLPACK:
# A Scalable C++  Machine Learning Library
library: mlpack
methods:
    PCA:
        script: methods/mlpack/pca.py
        format: [csv, txt, hdf5, bin]
        run: ['timing', 'metric', 'bootstrap']
        iterations: 2
        datasets:
            - files: [['datasets/iris_train.csv', 'datasets/iris_test.csv', 'datasets/iris_labels.csv']]
              options: '-s'
```

In this case we benchmark the pca method located in methods/mlpack/pca.py with the isolet and the cities dataset. The pca method scales the data before running the pca method. The benchmark performs twice for each dataset. Additionally the pca.py script supports the following file formats txt, csv, hdf5 and bin. If the data isn't available in this particular case the format will be generated.

## Competing libraries

* http://mlpack.org
* http://mathworks.com
* http://shogun-toolbox.org
* http://cs.waikato.ac.nz/ml/weka/
* http://scikit-learn.org
* http://mlpy.sourceforge.net
* http://www.cs.umd.edu/~mount/ANN/
* http://www.cs.ubc.ca/research/flann/

## Citation details

If you use the benchmarks in your work, we'd really appreciate it if you could cite the following paper (given in BiBTeX format):

    @inproceedings{edel2014automatic,
      title={An automatic benchmarking system},
      author={Edel, Marcus and Soni, Anand and Curtin, Ryan R},
      booktitle={NIPS 2014 Workshop on Software Engineering for Machine Learning (SE4ML’2014)},
      volume={1},
      year={2014}
    }
