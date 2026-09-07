package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"basic-segment", "escape-decoding", "invalid-prefix", "property-match", "element-match", "navigation", "append-property", "append-index", "negative-index", "empty-pointer"};

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        String candidateTimeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", candidateTimeout, "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m",
            "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(input, output, "basic", "/alpha", "/alpha|6|false|alpha|-1|true|false");
            passed[1] = check(input, output, "escape", "/a~1b/~0c/~x", "/a~1b/~0c/~x|12|false|a/b|-1|true|false");
            passed[2] = error(input, output, "invalid", "not-a-pointer", "IllegalArgumentException");
            passed[3] = check(input, output, "property", "/a~1b/tail\u0000a/b", "true|/tail");
            passed[4] = check(input, output, "element", "/0/tail\u00000", "true|/tail");
            passed[5] = check(input, output, "navigation", "/a/b/c", "/b/c|/a/b");
            passed[6] = check(input, output, "append-property", "/a\u0000x/y~z", "/a/x~1y~0z");
            passed[7] = check(input, output, "append-index", "/a\u000012", "/a/12");
            passed[8] = error(input, output, "append-negative", "/a", "IllegalArgumentException");
            passed[9] = check(input, output, "empty", "", "|0|true|<null>|-1|false|false");
        } finally { input.close(); output.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Jackson Core JsonPointer contract", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; report.append(start(id, IDS[i], "TEST", "c")); report.append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report);
        if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter in, BufferedReader out, String op, String args, String expected) throws Exception {
        String line = request(in, out, op, args);
        String prefix = "{\"ok\":true,\"value\":\"";
        return line != null && line.startsWith(prefix) && line.endsWith("\"}") && expected.equals(decode(line.substring(prefix.length(), line.length() - 2)));
    }
    private static boolean error(BufferedWriter in, BufferedReader out, String op, String args, String expected) throws Exception { return ("{\"ok\":false,\"error\":\"" + expected + "\"}").equals(request(in, out, op, args)); }
    private static String request(BufferedWriter in, BufferedReader out, String op, String args) throws Exception { in.write("{\"op\":\"" + op + "\",\"args\":\"" + encode(args) + "\"}"); in.newLine(); in.flush(); return out.readLine(); }
    private static String encode(String value) { return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)); }
    private static String decode(String value) { return new String(Base64.getDecoder().decode(value), StandardCharsets.UTF_8); }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
