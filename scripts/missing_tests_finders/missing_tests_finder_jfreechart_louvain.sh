mainClass="com.kuleuven.missing_test_finder.MissingTestFinder"
clustersPath="thesis_code/data/jfreechart/clusters/louvain/clusters.json"
testInput="systems/jfreechart/src/test"
jarPath="target/libs/jfreechart-1.5.4.jar"
srcDir="systems/jfreechart/src"
missingTests="thesis_code/data/jfreechart/missing_tests/louvain/missing_tests.json"
mvn exec:java -Dexec.mainClass=$mainClass -Dexec.args="$clustersPath $testInput $jarPath $srcDir $missingTests"
