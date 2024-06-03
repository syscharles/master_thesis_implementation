package com.kuleuven.graph_extractor;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.resolution.declarations.ResolvedMethodDeclaration;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JavaParserTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JarTypeSolver;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Set;

public class GraphExtractor {

    private static JavaParser javaParser;
    private static final JSONObject graph = new JSONObject();
    private static final JSONArray nodes = new JSONArray();
    private static final JSONArray edges = new JSONArray();
    private static final Set<String> declaredClasses = new HashSet<>();
    private static final Set<String> uniqueEdges = new HashSet<>();

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: java CollaborationDiagramExtractor <output_json_file_path> <source_directory> <jar_path>]");
            return;
        }

        String outputFilePath = args[0];
        File mainDirectory = new File(args[1]);
        Path jarPath = Paths.get(args[2]);

        setupParser(jarPath, mainDirectory);

        if (mainDirectory.isDirectory()) {
            Files.walk(mainDirectory.toPath())
                .filter(Files::isRegularFile)
                .filter(path -> path.toString().endsWith(".java"))
                .forEach(path -> collectClassNames(path.toFile()));
        }

        if (mainDirectory.isDirectory()) {
            Files.walk(mainDirectory.toPath())
                .filter(Files::isRegularFile)
                .filter(path -> path.toString().endsWith(".java"))
                .forEach(path -> parseJavaFile(path.toFile()));
        }

        processEdges();

        graph.put("nodes", nodes);
        graph.put("edges", edges);

        writeFile(outputFilePath, graph.toString(4).getBytes());
        System.out.println("Graph has been saved to " + outputFilePath);
    }

    public static void writeFile(String outputFilePath, byte[] content) {
        try {
            Path path = Paths.get(outputFilePath);
            Path parentDir = path.getParent();
            if (parentDir != null) {
                Files.createDirectories(parentDir);
            }
            Files.write(path, content);
            System.out.println("File written successfully.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void setupParser(Path jarPath, File mainDirectory) {
        CombinedTypeSolver combinedSolver = new CombinedTypeSolver(new ReflectionTypeSolver());
        
        if (mainDirectory.exists() && mainDirectory.isDirectory()) {
            combinedSolver.add(new JavaParserTypeSolver(mainDirectory));
        } else {
            System.err.println("Directory does not exist: " + mainDirectory.getPath());
        }

        try {
            combinedSolver.add(new JarTypeSolver(jarPath));
            combinedSolver.add(new JarTypeSolver("target/libs/javax.servlet-api-4.0.1.jar"));
            combinedSolver.add(new JarTypeSolver("target/libs/xercesImpl-2.8.0.jar"));
            combinedSolver.add(new JarTypeSolver("target/libs/xml-apis-1.3.03.jar"));
        } catch (IOException e) {
            System.err.println("Failed to load JAR for type resolution: " + e.getMessage());
        }        

        JavaSymbolSolver symbolSolver = new JavaSymbolSolver(combinedSolver);
        ParserConfiguration parserConfiguration = new ParserConfiguration().setSymbolResolver(symbolSolver);
        javaParser = new JavaParser(parserConfiguration);
        return;
    }


    private static void collectClassNames(File file) {
        try (FileInputStream in = new FileInputStream(file)) {
            ParseResult<CompilationUnit> parseResult = javaParser.parse(in);
            parseResult.ifSuccessful(cu -> {
                cu.findAll(ClassOrInterfaceDeclaration.class).forEach(cid -> {
                    cid.getFullyQualifiedName().ifPresent(declaredClasses::add);
                });
            });
        } catch (Exception e) {
            System.err.println("Error collecting class names from file: " + file.getName());
        }
    }

    private static void parseJavaFile(File file) {
        try (FileInputStream in = new FileInputStream(file)) {
            ParseResult<CompilationUnit> parseResult = javaParser.parse(in);
            parseResult.ifSuccessful(cu -> cu.accept(new ClassVisitor(), null));
        } catch (Exception e) {
            System.err.println("Error processing file: " + file.getName());
        }
    }

    private static class ClassVisitor extends VoidVisitorAdapter<Void> {
        @Override
        public void visit(ClassOrInterfaceDeclaration cid, Void arg) {
            super.visit(cid, arg);
            cid.getFullyQualifiedName().ifPresent(declaredClasses::add);
            JSONObject node = new JSONObject();
            String node_name = cid.getFullyQualifiedName().orElse("Unknown");
            node.put("name", node_name);
            nodes.put(node);
            cid.getMethods().forEach(method -> method.accept(new MethodVisitor(), cid.getFullyQualifiedName().orElse("Unknown")));
        }
    }

    private static class MethodVisitor extends VoidVisitorAdapter<String> {
        @Override
        public void visit(MethodDeclaration md, String className) {
            super.visit(md, className);
            String methodSignature = md.getSignature().asString();
            JSONObject sourceMethod = new JSONObject();
            sourceMethod.put("method_signature", md.getSignature());
            sourceMethod.put("method_name", md.getNameAsString());
            sourceMethod.put("return_type", md.getType().resolve().describe());
            sourceMethod.put("arguments", getArguments(md));
            sourceMethod.put("declaring_class", className);
            md.findAll(MethodCallExpr.class).forEach(mce -> mce.accept(new MethodCallVisitor(className, methodSignature, sourceMethod), null));
        }
    }    

    private static class MethodCallVisitor extends VoidVisitorAdapter<Void> {
        private final String className;
        private final String sourceMethodSignature;
        private final JSONObject sourceMethod;
    
        public MethodCallVisitor(String className, String sourceMethodSignature, JSONObject sourceMethod) {
            this.className = className;
            this.sourceMethodSignature = sourceMethodSignature;
            this.sourceMethod = sourceMethod;
        }
    
        @Override
        public void visit(MethodCallExpr mce, Void arg) {
            super.visit(mce, arg);
            try {
                ResolvedMethodDeclaration resolvedMethod = mce.resolve();
                String declaringClassName = resolvedMethod.declaringType().getQualifiedName();
                String methodCallSignature = resolvedMethod.getSignature();
                String uniqueId = className + "->" + declaringClassName + ":" + methodCallSignature + "@" + sourceMethodSignature;
                if (!uniqueEdges.contains(uniqueId)) {
                    JSONObject edge = new JSONObject();
                    edge.put("source", className);
                    edge.put("destination", declaringClassName);
                    JSONObject link_method = new JSONObject();
                    link_method.put("method_signature", methodCallSignature);
                    link_method.put("method_name", mce.getNameAsString());
                    link_method.put("return_type", resolvedMethod.getReturnType().describe());
                    link_method.put("arguments", getArguments(mce));
                    link_method.put("declaring_class", declaringClassName);
                    edge.put("link_method", link_method);
                    edge.put("source_method", sourceMethod);
                    edges.put(edge);
                    uniqueEdges.add(uniqueId);
                }
            } catch (Exception e) {
                System.out.println("Could not resolve method declaration for: " + mce.getNameAsString());
            }
        }
    }

    private static JSONArray getArguments(MethodDeclaration md) {
        JSONArray arguments = new JSONArray();
        md.getParameters().forEach(param -> {
            JSONObject argument = new JSONObject();
            String typeName = param.getType().resolve().describe();
            argument.put("type", typeName);
            argument.put("value", param.getNameAsString());
            arguments.put(argument);
        });
        return arguments;
    }

    private static JSONArray getArguments(MethodCallExpr mce) {
        JSONArray arguments = new JSONArray();
        mce.getArguments().forEach(arg -> {
            JSONObject argument = new JSONObject();
            String typeName = arg.calculateResolvedType().describe();
            argument.put("type", typeName);
            argument.put("value", arg.toString());
            arguments.put(argument);
        });
        return arguments;
    }

    private static void processEdges() {
        JSONArray filteredEdges = new JSONArray();
        edges.forEach(item -> {
            JSONObject edge = (JSONObject) item;
            String source = edge.getString("source");
            String destination = edge.getString("destination");
            if (!source.equals(destination) &&
                declaredClasses.contains(source) && declaredClasses.contains(destination)) {
                filteredEdges.put(edge);
            }
        });
        edges.clear();
        filteredEdges.forEach(edges::put);
    }
}
