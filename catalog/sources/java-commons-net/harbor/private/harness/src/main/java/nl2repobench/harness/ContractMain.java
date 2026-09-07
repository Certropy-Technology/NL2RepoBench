package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class ContractMain {
    private static final String[] IDS = {"cidr-summary", "default-range", "inclusive-range", "mask-constructor",
            "large-count", "invalid-input", "address-array", "address-stream", "navigation", "packed-integer"};

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        boolean[] passed = new boolean[IDS.length];
        Process candidate = new ProcessBuilder(System.getProperty("nl2repobench.python", "/usr/local/bin/python3"), "-I", "-m",
                "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001",
                "--timeout-sec", System.getProperty("nl2repobench.candidate.timeout", "300"), "--",
                System.getProperty("nl2repobench.java", "/opt/java/openjdk/bin/java"), "-Xmx256m", "-XX:MaxMetaspaceSize=128m",
                "-XX:MaxDirectMemorySize=64m", "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
                "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        try {
            passed[0] = check(input, output, "cidr-summary", "192.168.0.1/29", "192.168.0.1|255.255.255.248|192.168.0.0|192.168.0.7|192.168.0.1/29|6");
            passed[1] = check(input, output, "default-range", "192.168.0.1/29", "192.168.0.1|192.168.0.6|6|true|false");
            passed[2] = check(input, output, "inclusive-range", "192.168.0.1/29", "192.168.0.0|192.168.0.7|8|true|true");
            passed[3] = check(input, output, "mask-constructor", "192.168.0.1|255.255.255.248", "192.168.0.1|255.255.255.248|192.168.0.0|192.168.0.7|192.168.0.1/29|6");
            passed[4] = check(input, output, "large-count", "0.0.0.0/0", "4294967296");
            passed[5] = check(input, output, "invalid-input", "192.168.0.1/33", "IllegalArgumentException");
            passed[6] = check(input, output, "address-array", "192.168.0.1/30", "192.168.0.1,192.168.0.2");
            passed[7] = check(input, output, "address-stream", "192.168.0.1/30", "192.168.0.1,192.168.0.2");
            passed[8] = check(input, output, "navigation", "192.168.0.7/29", "192.168.0.8|192.168.0.0");
            passed[9] = check(input, output, "packed-integer", "192.168.0.1", "-1062731775");
        } finally { try { input.close(); } catch (IOException ignored) {} }
        output.close();
        if (candidate.waitFor() != 0) Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder();
        report.append("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Java commons-net contract", "[engine:nl2repobench]", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) { report.append(start("t" + i, IDS[i], "[engine:nl2repobench]/[test:" + IDS[i] + "]", "TEST", "c")); report.append(finish("t" + i, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report); if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter input, BufferedReader output, String operation, String value, String expected) {
        try { input.write(operation + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); input.newLine(); input.flush(); String line = output.readLine(); if (line == null) return false; String[] fields = line.split("\t", -1); return fields.length == 2 && fields[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8)); } catch (Exception failure) { return false; }
    }
    private static String start(String id, String name, String uniqueId, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
