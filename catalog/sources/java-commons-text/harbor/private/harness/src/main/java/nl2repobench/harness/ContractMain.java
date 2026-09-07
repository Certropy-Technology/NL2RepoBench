package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"equal", "one-mismatch", "all-mismatch", "empty", "unicode-units", "builder", "null-left", "null-right", "unequal-short", "unequal-long"};
    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        boolean[] passed = new boolean[IDS.length];
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec",
            System.getProperty("nl2repobench.candidate.timeout", "300"), "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m",
            "-XX:CompressedClassSpaceSize=64m", "-cp", System.getProperty(
                "nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain")
            .redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        try {
            passed[0] = check(input, output, "apply", "same|same", "0");
            passed[1] = check(input, output, "apply", "abc|axc", "1");
            passed[2] = check(input, output, "apply", "abc|XYZ", "3");
            passed[3] = check(input, output, "apply", "|", "0");
            passed[4] = check(input, output, "apply", "😀|😁", "1");
            passed[5] = check(input, output, "apply", "builder|builder", "0");
            passed[6] = check(input, output, "apply", "NULL|abc", "EX:IllegalArgumentException");
            passed[7] = check(input, output, "apply", "abc|NULL", "EX:IllegalArgumentException");
            passed[8] = check(input, output, "apply", "ab|abc", "EX:IllegalArgumentException");
            passed[9] = check(input, output, "apply", "abcd|abc", "EX:IllegalArgumentException");
        } finally {
            try { input.close(); } catch (IOException ignored) { }
        }
        output.close();
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder();
        report.append("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Java Commons Text contract", "[engine:nl2repobench]", "CONTAINER", null));
        boolean allPassed = true;
        for (int i = 0; i < IDS.length; i++) {
            report.append(start("t" + i, IDS[i], "[engine:nl2repobench]/[test:" + IDS[i] + "]", "TEST", "c"));
            report.append(finish("t" + i, passed[i] ? "SUCCESSFUL" : "FAILED")); allPassed &= passed[i];
        }
        report.append(finish("c", "SUCCESSFUL")); report.append("</e:events>\n");
        System.out.print(report); if (!allPassed) System.exit(1);
    }

    private static boolean check(BufferedWriter input, BufferedReader output, String op, String value, String expected) throws IOException {
        input.write(op + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)));
        input.newLine(); input.flush(); String line = output.readLine(); if (line == null) return false;
        String[] fields = line.split("\t", -1);
        return fields.length == 2 && "OK".equals(fields[0]) && expected.equals(new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8));
    }
    private static String start(String id, String name, String uniqueId, String type, String parent) {
        String parentAttribute = parent == null ? "" : " parentId=\"" + parent + "\"";
        return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + parentAttribute + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\"" + type + "\"/>";
    }
    private static String finish(String id, String status) {
        return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>";
    }
}
