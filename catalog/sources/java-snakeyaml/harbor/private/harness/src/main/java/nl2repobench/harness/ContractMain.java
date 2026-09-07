package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

/** Trusted verifier that owns the fixed leaf collection and Open Test report. */
public final class ContractMain {
    private static final String[] IDS = {
        "single-values", "single-empty", "single-backed", "single-unmodifiable", "single-oob",
        "composite-values", "composite-first-backed", "composite-second-backed",
        "composite-unmodifiable", "composite-empty-left", "composite-empty-right", "null-input"
    };
    private static final String[] EXPECTED = {
        "2:red|blue", "0:", "green", "UnsupportedOperationException", "IndexOutOfBoundsException",
        "3:a|b|c", "x", "y", "UnsupportedOperationException", "1:z", "1:z", "NullPointerException"
    };
    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        String candidateTimeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", candidateTimeout, "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m",
            "-XX:CompressedClassSpaceSize=64m", "-cp", System.getProperty(
                "nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain")
            .redirectError(ProcessBuilder.Redirect.INHERIT).start();
        boolean[] passed = new boolean[IDS.length];
        try (BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
             BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8))) {
            for (int index = 0; index < IDS.length; index++) passed[index] = check(input, output, IDS[index], EXPECTED[index]);
        }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "SnakeYAML ArrayUtils contract", "[engine:nl2repobench]", "CONTAINER", null));
        boolean allPassed = true;
        for (int index = 0; index < IDS.length; index++) {
            report.append(start("t" + index, IDS[index], "[engine:nl2repobench]/[test:" + IDS[index] + "]", "TEST", "c"));
            report.append(finish("t" + index, passed[index] ? "SUCCESSFUL" : "FAILED"));
            allPassed &= passed[index];
        }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report);
        if (!allPassed) System.exit(1);
    }

    private static boolean check(BufferedWriter input, BufferedReader output, String operation, String expected) throws IOException {
        input.write("{\"op\":\"" + operation + "\"}");
        input.newLine();
        input.flush();
        return ("{\"ok\":true,\"value\":\"" + expected + "\"}").equals(output.readLine());
    }

    private static String start(String id, String name, String uniqueId, String type, String parent) {
        String parentAttribute = parent == null ? "" : " parentId=\"" + parent + "\"";
        return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + parentAttribute
            + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\"" + type + "\"/>";
    }

    private static String finish(String id, String status) {
        return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>";
    }
}
