mainClass="com.kuleuven.graph_extractor.GraphExtractor"
graphPath="thesis_code/data/joda_time/graph/graph.json"
srcDir="systems/joda-time/src/main/java/org/joda/time"
jarPath="target/libs/joda-time-2.12.6.jar"
mvn exec:java -Dexec.mainClass=$mainClass -Dexec.args="$graphPath $srcDir $jarPath"