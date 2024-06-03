package com.kuleuven.test_reducer;

import org.json.JSONArray;
import org.json.JSONObject;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
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
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class TestReducer {

    private static JavaParser javaParser;
    private static CombinedTypeSolver combinedSolver;

    private static class AnalysisResult {
        int totalTestMethods = 0;
        int removedTestMethods = 0;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: java TestReducer <json_file_path> <test_directory_path> <output_directory> <jar_path> <src_dir>");
            return;
        }

        String jsonFilePath = args[0];
        Path testDirectoryPath = Paths.get(args[1]);
        Path outputDirectoryPath = Paths.get(args[2]);
        Path jarPath = Paths.get(args[3]);
        File srcDir = new File(args[4]);

        cleanReducedTest(outputDirectoryPath);
        Files.createDirectories(outputDirectoryPath);
        copyDirectory(testDirectoryPath, outputDirectoryPath);

        setupParser(jarPath, srcDir);

        Set<JSONObject> relevantMethods = parseJsonFile(jsonFilePath);

        processJavaFiles(outputDirectoryPath, relevantMethods);
    }

    private static void cleanReducedTest(Path outputDirectoryPath) throws IOException {
        if (Files.exists(outputDirectoryPath)) {
            Files.walkFileTree(outputDirectoryPath, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                    Files.delete(file);
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
                    Files.delete(dir);
                    return FileVisitResult.CONTINUE;
                }
            });
        }
    }

    private static void copyDirectory(Path source, Path target) throws IOException {
        Files.walk(source)
            .forEach(sourcePath -> {
                Path targetPath = target.resolve(source.relativize(sourcePath));
                try {
                    Files.copy(sourcePath, targetPath, StandardCopyOption.REPLACE_EXISTING);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
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

    private static Set<JSONObject> parseJsonFile(String filePath) throws Exception {
        String content = new String(Files.readAllBytes(Paths.get(filePath)));
        JSONObject jsonObject = new JSONObject(content);
        JSONArray edges = jsonObject.getJSONArray("inter_cluster_edges");
        Set<JSONObject> methods = new HashSet<>();
    
        for (int i = 0; i < edges.length(); i++) {
            JSONObject edge = edges.getJSONObject(i);
            JSONObject sourceMethod = edge.getJSONObject("source_method");
            methods.add(sourceMethod);
        }
    
        return methods;
    }

    private static void processJavaFiles(Path directory, Set<JSONObject> relevantMethods) throws IOException {
        int totalTests = 0;
        int removedTests = 0;

        List<Path> javaFiles = Files.walk(directory)
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".java"))
            .collect(Collectors.toList());

        for (Path path : javaFiles) {
            AnalysisResult result = analyzeAndModifyJavaFile(path, relevantMethods);
            totalTests += result.totalTestMethods;
            removedTests += result.removedTestMethods;
        }

        if (totalTests > 0) {
            int keptTests = totalTests - removedTests;
            double keptPercentage = ((double) keptTests / totalTests) * 100;
            System.out.printf("Total test methods: %d, Removed test methods: %d, Kept test methods: %d (%.2f%%)\n",
                    totalTests, removedTests, keptTests, keptPercentage);
        } else {
            System.out.println("No test methods found.");
        }
    }


    private static AnalysisResult analyzeAndModifyJavaFile(Path path, Set<JSONObject> relevantMethods) throws IOException {
        try {
            AnalysisResult result = new AnalysisResult();
            CompilationUnit cu = javaParser.parse(path).getResult().orElseThrow(IllegalStateException::new);
    
            List<MethodDeclaration> methodsToRemove = new ArrayList<>();
    
            VoidVisitorAdapter<Void> methodVisitor = new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration n, Void arg) {
                    super.visit(n, arg);
    
                    if (n.getNameAsString().startsWith("test")) {
                        result.totalTestMethods++;
                        boolean containsSourceMethodCall = n.findAll(com.github.javaparser.ast.expr.MethodCallExpr.class).stream()
                            .anyMatch(call -> {
                                try {
                                    ResolvedMethodDeclaration resolvedMethod = call.resolve();
                                    String methodCallName = call.getNameAsString();
                                    ResolvedReferenceTypeDeclaration currentClass = resolvedMethod.declaringType().asReferenceType();
    
                                    return relevantMethods.stream().anyMatch(json -> {
                                        String jsonDeclaringClass = json.getString("declaring_class");
                                        try {
                                            if (methodCallName.equals(json.getString("method_name"))) {
                                                ResolvedReferenceTypeDeclaration jsonClass = combinedSolver.tryToSolveType(jsonDeclaringClass).getCorrespondingDeclaration().asReferenceType();
                                                return (currentClass.isAssignableBy(jsonClass) || jsonClass.isAssignableBy(currentClass));
                                            }
                                        } catch (UnsolvedSymbolException | UnsupportedOperationException e) {
                                            logException(e);
                                            return false;
                                        }
                                        return false;
                                    });
                                } catch (Throwable e) {
                                    logException(e);
                                    return false;
                                }
                            });
                        if (containsSourceMethodCall) {
                            methodsToRemove.add(n);
                            result.removedTestMethods++;
                        }
                    }
                }
            };
    
            methodVisitor.visit(cu, null);
            methodsToRemove.forEach(MethodDeclaration::remove);
    
            // Write the modified compilation unit back to the file
            Files.write(path, cu.toString().getBytes());
    
            return result;
        } catch (IOException e) {
            throw new IOException("Failed to analyze and modify Java file: " + path, e);
        }
    }

    private static void logException(Throwable e) {
        System.out.println(e.getClass().getSimpleName() + ": " + e.getMessage());
    }
}
