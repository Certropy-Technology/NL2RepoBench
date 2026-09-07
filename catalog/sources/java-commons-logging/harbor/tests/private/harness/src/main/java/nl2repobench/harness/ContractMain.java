package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"construct-default", "construct-name", "levels", "debug-call",
        "error-call", "fatal-call", "info-call", "trace-call", "warn-call", "type"};

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        boolean[] passed = new boolean[IDS.length];
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m",
            "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001",
            "--timeout-sec", System.getProperty("nl2repobench.candidate.timeout", "300"), "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m",
            "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp",
            System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        try {
            passed[0] = check(input, output, IDS[0], "ignored", "NoOpLog");
            passed[1] = check(input, output, IDS[1], "component", "NoOpLog");
            passed[2] = check(input, output, IDS[2], "null", "true,true,true,true,true,true");
            passed[3] = check(input, output, IDS[3], "message", "ok");
            passed[4] = check(input, output, IDS[4], "message", "ok");
            passed[5] = check(input, output, IDS[5], "message", "ok");
            passed[6] = check(input, output, IDS[6], "message", "ok");
            passed[7] = check(input, output, IDS[7], "message", "ok");
            passed[8] = check(input, output, IDS[8], "message", "ok");
            passed[9] = check(input, output, IDS[9], "any", "true");
        } finally { try { input.close(); } catch (IOException ignored) {} }
        output.close();
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder();
        report.append("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Java Commons Logging contract", "[engine:nl2repobench]", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) { report.append(start("t" + i, IDS[i], "[test:" + IDS[i] + "]", "TEST", "c")); report.append(finish("t" + i, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report); if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter input, BufferedReader output, String operation, String value, String expected) {
        try { input.write(operation + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); input.newLine(); input.flush(); String[] fields = output.readLine().split("\t", -1); return fields.length == 2 && fields[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8)); } catch (RuntimeException | IOException failure) { return false; }
    }
    private static String start(String id, String name, String uniqueId, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
