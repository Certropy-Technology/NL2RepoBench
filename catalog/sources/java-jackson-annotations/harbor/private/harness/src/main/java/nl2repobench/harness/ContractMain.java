package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {
        "mode-order", "mode-lookup", "mode-unknown", "mode-default",
        "mode-return-type", "creator-targets", "runtime-retention", "marker-and-explicit-mode"
    };

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
            passed[0] = success(input, output, "values", "", "DEFAULT,DELEGATING,PROPERTIES,DISABLED");
            passed[1] = success(input, output, "value-of", "DELEGATING", "DELEGATING");
            passed[2] = error(input, output, "value-of", "UNKNOWN", "IllegalArgumentException");
            passed[3] = success(input, output, "default", "", "DEFAULT");
            passed[4] = success(input, output, "return-type", "", "com.fasterxml.jackson.annotation.JsonCreator$Mode");
            passed[5] = success(input, output, "targets", "", "ANNOTATION_TYPE,METHOD,CONSTRUCTOR");
            passed[6] = success(input, output, "retention", "", "RUNTIME");
            passed[7] = success(input, output, "marker", "", "true") && success(input, output, "explicit", "", "PROPERTIES");
        } finally {
            input.close();
            output.close();
        }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Jackson JsonCreator contract", "CONTAINER", null));
        boolean all = true;
        for (int index = 0; index < IDS.length; index++) {
            String id = "t" + index;
            report.append(start(id, IDS[index], "TEST", "c"));
            report.append(finish(id, passed[index] ? "SUCCESSFUL" : "FAILED"));
            all &= passed[index];
        }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report);
        if (!all) System.exit(1);
    }

    private static boolean success(BufferedWriter input, BufferedReader output, String operation, String value, String expected) throws Exception {
        String response = request(input, output, operation, value);
        return response != null && response.startsWith("OK\t") && expected.equals(decode(response.substring(3)));
    }

    private static boolean error(BufferedWriter input, BufferedReader output, String operation, String value, String expected) throws Exception {
        String response = request(input, output, operation, value);
        return response != null && response.startsWith("ERR\t") && expected.equals(decode(response.substring(4)));
    }

    private static String request(BufferedWriter input, BufferedReader output, String operation, String value) throws Exception {
        input.write(operation + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)));
        input.newLine();
        input.flush();
        return output.readLine();
    }

    private static String decode(String value) { return new String(Base64.getDecoder().decode(value), StandardCharsets.UTF_8); }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
