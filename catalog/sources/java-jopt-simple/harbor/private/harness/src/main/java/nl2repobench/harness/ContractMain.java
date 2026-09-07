package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"empty", "no-equals", "trailing-equals", "leading-equals", "simple-pair", "later-equals", "whitespace", "string-form", "record-equality", "null-input"};

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        String timeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", timeout, "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m",
            "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(input, output, "pair", "", nul() + soh());
            passed[1] = check(input, output, "pair", "debug", "debug" + nul() + soh());
            passed[2] = check(input, output, "pair", "key=", "key" + nul());
            passed[3] = check(input, output, "pair", "=value", nul() + "value");
            passed[4] = check(input, output, "pair", "key=value", "key" + nul() + "value");
            passed[5] = check(input, output, "pair", "key=one=two", "key" + nul() + "one=two");
            passed[6] = check(input, output, "pair", " key = value ", " key " + nul() + " value ");
            passed[7] = check(input, output, "text", "debug", "debug=null");
            passed[8] = check(input, output, "equal", "x=y" + nul() + "x=y", "true");
            passed[9] = expectError(input, output, "null", "NullPointerException");
        } finally { input.close(); output.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "jopt-simple KeyValuePair contract", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; report.append(start(id, IDS[i], "TEST", "c")); report.append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report);
        if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter in, BufferedReader out, String operation, String value, String expected) throws IOException {
        in.write(operation + tab() + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush();
        String line = out.readLine();
        return line != null && line.startsWith("OK" + tab()) && expected.equals(new String(Base64.getDecoder().decode(line.substring(3)), StandardCharsets.UTF_8));
    }

    private static boolean expectError(BufferedWriter in, BufferedReader out, String operation, String expected) throws IOException {
        in.write(operation + tab()); in.newLine(); in.flush();
        String line = out.readLine();
        return line != null && line.startsWith("ERR" + tab()) && expected.equals(new String(Base64.getDecoder().decode(line.substring(4)), StandardCharsets.UTF_8));
    }

    private static String tab() { return String.valueOf((char) 9); }
    private static String nul() { return String.valueOf((char) 0); }
    private static String soh() { return String.valueOf((char) 1); }

    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
