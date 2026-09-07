package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"error-name", "failure-name", "pending-name", "success-name", "values-order", "ordinal", "valueof-error", "values-isolated"};
    private ContractMain() {}
    public static void main(String[] args) throws Exception {
        String timeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", timeout, "--", "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        var input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        var output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(input, output, "name", "ERROR", "ERROR"); passed[1] = check(input, output, "name", "FAILURE", "FAILURE");
            passed[2] = check(input, output, "name", "PENDING", "PENDING"); passed[3] = check(input, output, "name", "SUCCESS", "SUCCESS");
            passed[4] = check(input, output, "values", "", "ERROR,FAILURE,PENDING,SUCCESS"); passed[5] = check(input, output, "ordinal", "PENDING", "2");
            passed[6] = error(input, output, "name", "success", "IllegalArgumentException"); passed[7] = check(input, output, "isolation", "", "ERROR");
        } finally { input.close(); output.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder xml = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        xml.append(start("c", "GHCommitState contract", "CONTAINER", null)); boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; xml.append(start(id, IDS[i], "TEST", "c")).append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        xml.append(finish("c", "SUCCESSFUL")).append("</e:events>\n"); System.out.print(xml); if (!all) System.exit(1);
    }
    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException { String actual = call(in, out, op, value); return ("OK\t" + expected).equals(actual); }
    private static boolean error(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException { return ("ERR\t" + expected).equals(call(in, out, op, value)); }
    private static String call(BufferedWriter in, BufferedReader out, String op, String value) throws IOException { in.write(op + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush(); String line = out.readLine(); if (line == null) return ""; String[] p = line.split("\t", 2); return p.length == 2 ? p[0] + "\t" + new String(Base64.getDecoder().decode(p[1]), StandardCharsets.UTF_8) : ""; }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
