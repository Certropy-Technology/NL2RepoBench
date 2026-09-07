package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"is-empty", "is-blank", "contains", "count-char", "count-sub", "default", "default-custom", "capitalize", "uncapitalize", "reverse", "split-whitespace", "split-char", "substring-negative", "substring-range", "left", "right"};
    private static final String[] EXPECTED = {"true:true:false", "true:true:false", "true:false:false", "3", "1", "|x", "fallback|x", "Cat||<null>", "cAT|cat", "desserts|B😀A", "red|green|blue", "a|b|c", "def", "cde", "ab|", "ef|"};
    private ContractMain() {}
    public static void main(String[] args) throws Exception {
        boolean[] passed = new boolean[IDS.length];
        Process candidate = new ProcessBuilder(System.getProperty("nl2repobench.python", "/usr/local/bin/python3"), "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", System.getProperty("nl2repobench.candidate.timeout", "300"), "--", System.getProperty("nl2repobench.java", "/opt/java/openjdk/bin/java"), "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        try (var input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8)); var output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8))) {
            for (int i = 0; i < IDS.length; i++) passed[i] = check(input, output, IDS[i], EXPECTED[i]);
            input.close();
            if (candidate.waitFor() != 0) Arrays.fill(passed, false);
            StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
            report.append(start("c", "Java commons-lang contract", "[engine:nl2repobench]", "CONTAINER", null));
            boolean all = true;
            for (int i = 0; i < IDS.length; i++) { report.append(start("t" + i, IDS[i], "[engine:nl2repobench]/[test:" + IDS[i] + "]", "TEST", "c")); report.append(finish("t" + i, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
            report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
            System.out.print(report);
            if (!all) System.exit(1);
        }
    }
    private static boolean check(BufferedWriter input, BufferedReader output, String op, String expected) {
        try { input.write(op + "\t" + Base64.getEncoder().encodeToString("x".getBytes(StandardCharsets.UTF_8))); input.newLine(); input.flush(); String line = output.readLine(); if (line == null) return false; String[] fields = line.split("\t", -1); return fields.length == 2 && fields[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8)); } catch (Exception error) { return false; }
    }
    private static String start(String id, String name, String uniqueId, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
