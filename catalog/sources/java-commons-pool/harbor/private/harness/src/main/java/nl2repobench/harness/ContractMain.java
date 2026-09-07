package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"enum-order", "positive-durations", "disabled-null-zero", "min-idle", "thread-false", "thread-true", "text-format", "independent-normalization"};
    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", "300", "--", "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(input, output, "enum", "", "IDLE:0|ALLOCATED:1|EVICTION:2|EVICTION_RETURN_TO_HEAD:3|VALIDATION:4|VALIDATION_PREALLOCATED:5|VALIDATION_RETURN_TO_HEAD:6|INVALID:7|ABANDONED:8|RETURNING:9");
            passed[1] = check(input, output, "positive", "10\u000020\u00003", "10|20|3");
            passed[2] = check(input, output, "disabled", "0\u0000null\u0000-1", Long.MAX_VALUE + "|" + Long.MAX_VALUE + "|-1");
            passed[3] = check(input, output, "minidle", "-7", "-7");
            passed[4] = check(input, output, "thread-false", "", "false");
            passed[5] = check(input, output, "thread-true", "", "true");
            passed[6] = check(input, output, "text", "10\u000020\u00003", "EvictionConfig [idleEvictDuration=PT0.01S, idleSoftEvictDuration=PT0.02S, minIdle=3]");
            passed[7] = check(input, output, "disabled", "-1\u00005\u00000", Long.MAX_VALUE + "|5|0");
        } finally { input.close(); output.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Commons Pool contract", "CONTAINER", null)); boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; report.append(start(id, IDS[i], "TEST", "c")).append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n"); System.out.print(report); if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException {
        in.write(op + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush(); String line = out.readLine();
        return line != null && line.startsWith("OK\t") && expected.equals(new String(Base64.getDecoder().decode(line.substring(3)), StandardCharsets.UTF_8));
    }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
