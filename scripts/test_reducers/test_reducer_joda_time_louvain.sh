mainClass="com.kuleuven.test_reducer.TestReducer"
clustersPath="thesis_code/data/joda_time/clusters/louvain/clusters.json"
testInput="systems/joda-time/src/test"
testOutput="systems/joda-time/src/reduced_test_louvain"
jarPath="target/libs/joda-time-2.12.6.jar"
srcDir="systems/joda-time/src"
mvn exec:java -Dexec.mainClass=$mainClass -Dexec.args="$clustersPath $testInput $testOutput $jarPath $srcDir"
