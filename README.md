# Graph Theory Based Test Case Selection for Integration Testing

## Project Overview

Welcome to the repository for my master thesis project for the academic year 2023-2024. 

This thesis explores the topic of 'Graph theory based test case selection for integration testing', where we specifically focus on optimising the integration test case selection process using graph theory. The aim is to represent the system under test (SUT) as a graph and apply clustering algorithms to identify critical integration points. Those are utilised to facilitate the selection of integration tests in an existing test suite, facilitating a more efficient testing process.

## Systems Used

Java's statically typed nature facilitates a smoother process for UML class diagram generation, making Java based open-source frameworks ideal candidates for analysis. The integration points and clusters identified within each studied system are used to validate the effectiveness of the proposed methodology.
Only system with existing test suite were studied in this thesis.

### Joda-Time

Joda-Time is the primary library selected for detailed study. It is a comprehensive framework for dealing with dates and times in Java. 

**Joda-Time GitHub Repository**: [Joda-Time GitHub Repository](https://github.com/JodaOrg/joda-time)

### JFreeChart

JFreeChart is another framework evaluated in this study. It is a popular Java library used for creating a wide variety of charts. 

**JFreeChart GitHub Repository**: [JFreeChart GitHub Repository](https://github.com/jfree/jfreechart)

### Apache Commons Math

Apache Commons Math is a library of lightweight, self-contained mathematics and statistics components addressing the most common problems not available in the Java programming language.

**Apache Commons Math GitHub Repository**: [Apache Commons Math GitHub Repository](https://github.com/apache/commons-math)

## Methodology

The proposed methodology consists of three main steps:

1. **Graph Representation**: The SUT is represented as a graph where classes are nodes and their interactions are edges. This involves parsing the systems's UML class diagrams information to identify the dependencies and interactions between different classes.

2. **Cluster Analysis**: Clustering algorithms such as Louvain, Girvan-Newman, and Leiden are applied to the graph representation of the SUT. These algorithms help in detecting significant clusters within the system, which are treated as integrated units.

3. **Integration Test Case Selection**: The identified inter-cluster edges (representing integration points) are used to select relevant test cases from the existing test suite. This step ensures that the most critical interactions within the system are tested, thereby optimising the test suite for integration testing.

## Running the Implementation

### Prerequisites

- Java Development Kit (JDK)
- Python 3.x
- Necessary libraries and dependencies

### Step 1: Setup

1. Clone this repository:
    ```sh
    git clone https://github.com/syscharles/master_thesis_implementation.git
    ```

2. Clone the repository of the SUT on which you want to apply the methodology:
    ```sh
    git clone the_link_to_the_SUT_repo
    ```

### Step 2: Graph Representation

1. Parse the UML class diagrams and generate the graph representation:

    Ensure that the Java source files and the necessary JAR files are available.

    Run the following command to execute the `GraphExtractor`:

    ```sh
    mvn exec:java -Dexec.mainClass=com.kuleuven.graph_extractor.GraphExtractor -Dexec.args="<output_graph_path> <source_directory> <jar_file_path>"
    ```

    - Replace `<output_graph_path>` with the path where you want the output JSON graph to be saved (`data/<system_name>/graph/graph.json`).
    - Replace `<source_directory>` with the path to the source directory of the system under test (e.g., `systems/<system_name>/src`).
    - Replace `<jar_file_path>` with the path to the JAR file required for type resolution (e.g., `target/libs/<system_jar>.jar`).

    This will generate a JSON file containing the graph representation of the system. The JSON will include:
    
    - **Nodes**: Representing the classes in the system.
    - **Edges**: Representing method calls between classes.

    After running the command, the graph representation will be stored in the `data/<system_name>/graph/graph.json` file, ready for the next steps in the process.

### Step 3: Cluster Analysis

1. Execute the clustering algorithms:

    Ensure that the required Python environment is set up with the necessary dependencies. You can use `pip` to install any required packages.

    Run the following Python script to perform the cluster analysis:

    - The script will use the `AnalysisManager` class to process the graph representation and identify clusters.
    - You can specify the data path and the clustering algorithm to be used. In the example provided, the `LOUVAIN` algorithm is used, but you can also choose `GIRVAN_NEWMAN` or `LEIDEN`.

    The output will be:

    - **Graph Report**: A detailed JSON file of the graph representation saved at `data/<system_name>/graph/graph.json`.
    - **Clusters Report**: A detailed JSON file of the identified clusters saved at `data/<system_name>/clusters/<clustering_algorithm>/clusters.json`.
    - **Logs**: A log file containing detailed logs of the analysis process saved at `data/<system_name>/clusters/<clustering_algorithm>/analysis.log`.
    - **Graph Visualization**: Jupyter Notebooks for plotting the graph visualization saved in the same directory as the clusters report.

    Example command to run the analysis on the Joda-Time framework:

    Make sure to update the `data_path` and `clustering_algorithm` in the `main` function of the `analysis_manager.py` script as needed. For example:

    ```python
    def main():
        '''
        This runs the analysis on the real-world framework Joda-time.
        '''
        data_path = './data/joda_time'
        clustering_algorithm = ClusteringAlgorithm.LOUVAIN
        analysis_manager = AnalysisManager(data_path, clustering_algorithm)
        analysis_manager.run_analysis()
    
    if __name__ == '__main__':
        main()
    ```

    After running the command, the results will be stored in the specified directories, ready for further inspection and use in the next steps.


### Step 4: Integration Test Case Selection

1. Analyse the existing test suite and reduce the tests to only those relevant for integration points:

    Ensure that the required Java source files and JAR files are available.

    Run the following command to execute the `TestReducer`:

    ```sh
    mvn exec:java -Dexec.mainClass=com.kuleuven.test_reducer.TestReducer -Dexec.args="<cluster_file_path> <test_directory_path> <output_directory> <jar_file_path> <src_dir>"
    ```

    - Replace `<cluster_file_path>` with the path to the JSON file containing the graph representation with clusters and inter-cluster edges (e.g., `data/<system_name>/clusters/<clustering_algorithm>/clusters.json`).
    - Replace `<test_directory_path>` with the path to the directory containing the test files of the SUT (e.g., `systems/<system_name>/src/test`).
    - Replace `<output_directory>` with the path to the directory where the reduced test suite should be saved (e.g., `systems/<system_name>/src/reduced_test_<clustering_algorithm>`).
    - Replace `<jar_file_path>` with the path to the JAR file required for type resolution (e.g., `target/libs/<system_jar>.jar`).
    - Replace `<src_dir>` with the path to the source directory of the system under test (e.g., `systems/<system_name>/src`).

    The `TestReducer` will:
    
    - Clean the output directory if it already exists.
    - Copy the test files from the test directory to the output directory.
    - Parse the JSON file to retrieve the relevant methods representing integration points.
    - Analyse each test file to determine if it calls any of the relevant methods and remove tests that do not.
    - Save the reduced test suite in the specified output directory.

    The output will be:
    
    - A reduced set of test files in the specified `<output_directory>`, containing only the tests relevant to the identified integration points.
    - A summary printed to the console with the total number of test methods, the number of removed test methods, and the percentage of kept test methods.

### Step 5: Identifying Missing Integration Tests

This step was an additional work and not specifically intended as part of the thesis but demonstrates an additional use case of the work.

1. Identify missing integration tests by analysing the existing test suite:

    Ensure that the required Java source files and JAR files are available.

    Run the following command to execute the `MissingTestFinder`:

    ```sh
    mvn exec:java -Dexec.mainClass=com.kuleuven.missing_test_finder.MissingTestFinder -Dexec.args="<clusters_json_file_path> <test_directory_path> <jar_file_path> <src_dir> <output_missing_tests_path>"
    ```

    - Replace `<clusters_json_file_path>` with the path to the JSON file containing the graph representation with clusters and inter-cluster edges (e.g., `data/<system_name>/clusters/<clustering_algorithm>/clusters.json`).
    - Replace `<test_directory_path>` with the path to the directory containing the test files of the SUT (e.g., `systems/<system_name>/src/test`).
    - Replace `<jar_file_path>` with the path to the JAR file required for type resolution (e.g., `target/libs/<system_jar>.jar`).
    - Replace `<src_dir>` with the path to the source directory of the system under test (e.g., `systems/<system_name>/src`).
    - Replace `<output_missing_tests_path>` with the path where the report of missing tests should be saved (e.g., `data/<system_name>/missing_tests/<clustering_algorithm>/missing_tests.json`).

    The `MissingTestFinder` will:

    - Parse the JSON file to retrieve the relevant methods representing integration points.
    - Analyse each test file to determine if it calls any of the relevant methods.
    - Identify methods from the graph representation that are not tested by the existing test suite.
    - Save the report of missing tests in the specified output path.

    The output will be:

    - A JSON file in the specified `<output_missing_tests_path>`, containing details of the source methods that are not covered by the existing test suite.
    - A summary printed to the console with the total number of source methods, the number of untested source methods, and the percentage of untested source methods.

## Evaluation

For the evaluation of the test reduction and selection process, we use PiTest, a mutation testing tool for Java. Mutation testing is a technique to evaluate the quality of a test suite by introducing small changes (mutations) to the code and checking if the test suite detects them.

### Pre-Evaluation Steps

1. **Manual Review of Reduced Tests**:
    - Before proceeding with PiTest, it is recommended to manually review the reduced test suite to ensure that it correctly covers the intended functionality. Possible problems were discussed in the thesis text.

2. **Ensure a Green Test Suite**:
    - Make sure that the reduced test suite passes all tests successfully. PiTest requires a green (passing) test suite to perform its mutation testing experiments.

### Using PiTest

PiTest can be integrated into the build process using Maven. Below are the steps to set up and run PiTest:

1. **Add PiTest to the Maven Project of the SUT**:
    - Add the following dependency and plugin to the `pom.xml` file of the SUT:

    ```xml
    </dependency>
        <dependency>
        <groupId>org.pitest</groupId>
        <artifactId>pitest-junit5-plugin</artifactId>
        <version>LATEST</version>
        <scope>test</scope>
    </dependency>
    
    <build>
        <plugins>
            <plugin>
            <groupId>org.pitest</groupId>
            <artifactId>pitest-maven</artifactId>
            <version>1.15.8</version>
            <dependencies>
                <dependency>
                    <groupId>org.pitest</groupId>
                    <artifactId>pitest-junit5-plugin</artifactId>
                    <version>LATEST</version>
                </dependency>
            </dependencies>
            <configuration>
                <targetTests>
                    <!-- This is how it was filled for Joda-Time for instance. -->
                    <param>org.joda.time.*</param> 
                </targetTests>
                <timeoutConstant>20000</timeoutConstant>
            </configuration>
        </plugin>
        </plugins>
    </build>
    ```

2. **Run PiTest**:
    - Execute the following Maven command in the repository of the SUT to run PiTest:

    ```sh
    mvn org.pitest:pitest-maven:mutationCoverage
    ```

    Note: you will probably have to rename the reduced test set directory `test` (and just store the original tests under another name like e.g. `original_test`).

3. **Review the Results**:
    - PiTest will generate a detailed report in the `target/pit-reports` directory in the SUT's main directory. Review the report to evaluate the effectiveness of your test suite in detecting mutations like it was done in the Evaluation chapter of the thesis.

## Conclusion

This repository implements a novel approach to optimise integration testing using graph theory. By representing the system as a graph and applying clustering algorithms, the methodology identifies critical integration points, enhancing the efficiency and effectiveness of the integration test case selection process.
