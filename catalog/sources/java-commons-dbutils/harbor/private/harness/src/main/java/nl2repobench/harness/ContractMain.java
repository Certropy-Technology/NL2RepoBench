package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {
        "array-order", "map-order", "map-case-insensitive", "array-first-row",
        "map-first-row", "scalar-index", "scalar-name", "column-index-order",
        "column-name-null", "empty-first-row"
    };

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", "300", "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m",
            "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp",
            System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain"
        ).redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(input, output, "array", "name,age\u0000Ada,37", "Ada|37");
            passed[1] = check(input, output, "map", "Name,Age\u0000Ada,37", "Name=Ada;Age=37");
            passed[2] = check(input, output, "map-get", "Name,Age\u0000Ada,37\u0000age", "37");
            passed[3] = check(input, output, "array-handler", "name,age\u0000Ada,37;Bob,41", "Ada|37");
            passed[4] = check(input, output, "map-handler", "name,age\u0000Ada,37;Bob,41", "name=Ada;age=37");
            passed[5] = check(input, output, "scalar-index", "name,age\u0000Ada,37\u00002", "37");
            passed[6] = check(input, output, "scalar-name", "name,age\u0000Ada,37\u0000NAME", "Ada");
            passed[7] = check(input, output, "column-index", "name,age\u0000Ada,37;Bob,41\u00002", "37|41");
            passed[8] = check(input, output, "column-name", "name,age\u0000Ada,~;Bob,41\u0000age", "<null>|41");
            passed[9] = check(input, output, "map-handler", "name,age\u0000\u0000", "<null>");
        } finally {
            input.close();
            output.close();
        }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Commons DbUtils contract", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) {
            String id = "t" + i;
            report.append(start(id, IDS[i], "TEST", "c"));
            report.append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED"));
            all &= passed[i];
        }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report);
        if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException {
        in.write(op + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)));
        in.newLine(); in.flush();
        String line = out.readLine();
        if (line == null || !line.startsWith("OK\t")) return false;
        return expected.equals(new String(Base64.getDecoder().decode(line.substring(3)), StandardCharsets.UTF_8));
    }

    private static String start(String id, String name, String type, String parent) {
        String parentAttr = parent == null ? "" : " parentId=\"" + parent + "\"";
        return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + parentAttr + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>";
    }

    private static String finish(String id, String status) {
        return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>";
    }
}
