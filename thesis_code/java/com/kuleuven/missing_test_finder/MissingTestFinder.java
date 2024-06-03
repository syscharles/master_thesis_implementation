package com.kuleuven.missing_test_finder;

import org.json.JSONArray;
import org.json.JSONObject;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JarTypeSolver;
import com.github.javaparser.resolution.UnsolvedSymbolException;
import com.github.javaparser.resolution.declarations.ResolvedMethodDeclaration;
import com.github.javaparser.resolution.declarations.ResolvedReferenceTypeDeclaration;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JavaParserTypeSolver;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MissingTestFinder {

    private static JavaParser javaParser;
    private static CombinedTypeSolver combinedSolver;

    private static class AnalysisResult{
        Set<JSONObject> untestedSourceMethods = new HashSet<JSONObject>();
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: java MissingTestFinder <clusters_json_file_path> <test_directory_path> <jar_path> <src_dir> <output_missing_tests_path>");
            return;
        }

        String clustersPath = args[0];
        Path testDirectoryPath = Paths.get(args[1]);
        Path jarPath = Paths.get(args[2]);
        File srcDir = new File(args[3]);
        String missingTestsPath = args[4];

        setupParser(jarPath, srcDir);

        Set<JSONObject> allSourceMethodsJson = parseJsonClusters(clustersPath);
        AnalysisResult analysisResult = analyseTestSuite(testDirectoryPath, allSourceMethodsJson);

        System.out.println("Total number of source_method calls: " + String.valueOf(allSourceMethodsJson.size()));
        System.out.println("Number of source_method calls not tested: " + String.valueOf(analysisResult.untestedSourceMethods.size()));
        double percentageNotTested = (double) analysisResult.untestedSourceMethods.size() / allSourceMethodsJson.size() * 100;
        System.out.printf("Percentage of source methods not tested: %.2f%%\n", percentageNotTested);

        outputMissingTests(analysisResult, missingTestsPath);
        System.out.println("Missing integration tests have been saved to " + missingTestsPath);
    }

    private static AnalysisResult analyseTestSuite(Path directory, Set<JSONObject> allSourceMethodsJson) throws IOException {
        AnalysisResult result = new AnalysisResult();
        result.untestedSourceMethods = new HashSet<>(allSourceMethodsJson);
    
        Files.walk(directory)
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".java"))
            .forEach(path -> {
                try {
                    CompilationUnit cu = javaParser.parse(path).getResult().orElseThrow(IllegalStateException::new);
                    cu.findAll(MethodDeclaration.class).forEach(method -> {
                        Set<JSONObject> methodsTested = new HashSet<>();
                        method.findAll(com.github.javaparser.ast.expr.MethodCallExpr.class).forEach(call -> {
                            try {
                                ResolvedMethodDeclaration resolvedMethod = call.resolve();
                                String methodCallName = call.getNameAsString();
                                ResolvedReferenceTypeDeclaration currentClass = resolvedMethod.declaringType().asReferenceType();
                                
                                result.untestedSourceMethods.forEach(json -> {
                                    String jsonDeclaringClass = json.getString("declaring_class");
                                    try {
                                        if (methodCallName.equals(json.getString("method_name"))) {
                                            ResolvedReferenceTypeDeclaration jsonClass = combinedSolver.tryToSolveType(jsonDeclaringClass).getCorrespondingDeclaration().asReferenceType();
                                            if ((currentClass.isAssignableBy(jsonClass) || jsonClass.isAssignableBy(currentClass))) {
                                                methodsTested.add(json);
                                            }
                                        }
                                    } catch (UnsolvedSymbolException | UnsupportedOperationException e) {
                                        logException(e);
                                    }
                                });
                            } catch (Throwable e) {
                                logException(e);
                            }
                        });
                        result.untestedSourceMethods.removeAll(methodsTested);
                    });
                } catch (IOException e) {
                    logException(e);
                }
            });
    
        return result;
    }    

    private static void logException(Throwable e) {
        System.out.println(e.getClass().getSimpleName() + ": " + e.getMessage());
    }

    private static void outputMissingTests(AnalysisResult analysisResult, String outputPath) throws IOException {
        JSONArray untestedMethodsJson = new JSONArray();
        
        for (JSONObject method : analysisResult.untestedSourceMethods) {
            untestedMethodsJson.put(method);
        }
        
        writeFile(outputPath, untestedMethodsJson.toString(4).getBytes());
    }

    public static void writeFile(String outputFilePath, byte[] content) {
        try {
            Path path = Paths.get(outputFilePath);
            Path parentDir = path.getParent();
            if (parentDir != null && !Files.exists(parentDir)) {
                Files.createDirectories(parentDir);
            }
            if (!Files.exists(path)) {
                Files.createFile(path);
            }
            Files.write(path, content);
            System.out.println("File written successfully to " + path.toAbsolutePath());
        } catch (Exception e) {
            System.err.println("Error writing file to " + outputFilePath);
            e.printStackTrace();
        }
    }
    
    private static void setupParser(Path jarPath, File mainDirectory) {
        combinedSolver = new CombinedTypeSolver(new ReflectionTypeSolver());
        
        List<Path> additionalJars = new ArrayList<Path>();
        additionalJars.add(jarPath);
        Path junit4Jar = Paths.get("target/libs/junit-4.12.jar");
        additionalJars.add(junit4Jar);
        Path junitJupityerEngineJar = Paths.get("target/libs/junit-jupiter-engine-5.2.0.jar");
        additionalJars.add(junitJupityerEngineJar);
        Path junitPlatformRunnerJar = Paths.get("target/libs/junit-platform-runner-1.2.0.jar");
        additionalJars.add(junitPlatformRunnerJar);
        Path junitJupiterApiJar = Paths.get("target/libs/junit-jupiter-api-5.2.0.jar");
        additionalJars.add(junitJupiterApiJar);
        
        if (mainDirectory.exists() && mainDirectory.isDirectory()) {
            combinedSolver.add(new JavaParserTypeSolver(mainDirectory));
        } else {
            System.err.println("Directory does not exist: " + mainDirectory.getPath());
        }

        for (Path jar : additionalJars) {
            try {
                combinedSolver.add(new JarTypeSolver(jar));
            } catch (IOException e) {
                System.err.println("Failed to load JAR for type resolution: " + jar + "; " + e.getMessage());
            }
        }       

        JavaSymbolSolver symbolSolver = new JavaSymbolSolver(combinedSolver);
        ParserConfiguration parserConfiguration = new ParserConfiguration().setSymbolResolver(symbolSolver);
        javaParser = new JavaParser(parserConfiguration);
        return;
    }

    private static Set<JSONObject> parseJsonClusters(String filePath) throws Exception {
        String content = new String(Files.readAllBytes(Paths.get(filePath)));
        JSONObject jsonObject = new JSONObject(content);
        JSONArray edges = jsonObject.getJSONArray("inter_cluster_edges");
        Set<JSONObject> methods = new HashSet<>();
        Set<String> uniqueMethodSignatures = new HashSet<>();
    
        for (int i = 0; i < edges.length(); i++) {
            JSONObject edge = edges.getJSONObject(i);
            JSONObject sourceMethod = edge.getJSONObject("source_method");
    
            String uniqueIdentifier = sourceMethod.getString("declaring_class") + "." + sourceMethod.getString("method_signature");
    
            if (uniqueMethodSignatures.add(uniqueIdentifier)) {
                methods.add(sourceMethod);
            }
        }
        return methods;
    }
        
}
