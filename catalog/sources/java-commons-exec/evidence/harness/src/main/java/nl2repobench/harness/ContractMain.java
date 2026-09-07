package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final int MAX_RESPONSE_CHARS = 4 * 1024 * 1024;
    private static final String[] IDS = {
        "parse-executable", "parse-quoted-arguments", "add-argument", "to-string",
        "quote-space", "quote-double", "is-quoted", "split", "join", "substitution"
    };

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        boolean[] passed = new boolean[IDS.length];
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec",
            System.getProperty("nl2repobench.candidate.timeout", "300"), "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m",
            "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp",
            System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain"
        ).redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        try {
            passed[0] = check(input, output, "parse-exec", "tool --flag value", "tool");
            passed[1] = check(input, output, "parse-args", "tool 'hello world' \"fast mode\"", "tool\u001f\"hello world\"\u001f\"fast mode\"");
            passed[2] = check(input, output, "add-arg", "tool\u0000hello world", "[tool, \"hello world\"]");
            passed[3] = check(input, output, "to-string", "tool\u0000value", "[tool, value]");
            passed[4] = check(input, output, "quote-space", "hello world", "\"hello world\"");
            passed[5] = check(input, output, "quote-double", "hello\"world", "'hello\"world'");
            passed[6] = check(input, output, "is-quoted", "'hello'", "true");
            passed[7] = check(input, output, "split", "a,b,c\u0000,", "a\u001fb\u001fc");
            passed[8] = check(input, output, "join", "a\u001fb\u001fc\u0000:", "a:b:c");
            passed[9] = check(input, output, "subst", "run ${name}\u0000name=demo\u0000strict", "run demo");
        } finally {
            try { input.close(); } catch (IOException ignored) { }
        }
        output.close();
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder();
        report.append("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Commons Exec contract", "[engine:nl2repobench]", "CONTAINER", null));
        boolean allPassed = true;
        for (int i = 0; i < IDS.length; i++) {
            String eventId = "t" + i;
            report.append(start(eventId, IDS[i], "[engine:nl2repobench]/[test:" + IDS[i] + "]", "TEST", "c"));
            report.append(finish(eventId, passed[i] ? "SUCCESSFUL" : "FAILED"));
            allPassed &= passed[i];
        }
        report.append(finish("c", "SUCCESSFUL"));
        report.append("</e:events>\n");
        System.out.print(report);
        if (!allPassed) System.exit(1);
    }

    private static boolean check(BufferedWriter input, BufferedReader output, String operation, String value, String expected) {
        try {
            input.write(operation + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)));
            input.newLine(); input.flush();
            String[] fields = readBoundedLine(output).split("\\t", -1);
            if (fields.length != 2 || !fields[0].equals("OK")) return false;
            String actual = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
            return expected.equals(actual);
        } catch (RuntimeException | IOException failure) { return false; }
    }

    private static String readBoundedLine(BufferedReader output) throws IOException {
        StringBuilder line = new StringBuilder(); int character;
        while ((character = output.read()) != -1) {
            if (character == '\n') return line.toString();
            if (line.length() >= MAX_RESPONSE_CHARS) throw new IOException("response exceeds size limit");
            line.append((char) character);
        }
        throw new IOException("candidate exited before responding");
    }

    private static String start(String id, String name, String uniqueId, String type, String parent) {
        String parentAttribute = parent == null ? "" : " parentId=\"" + parent + "\"";
        return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + parentAttribute + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\"" + type + "\"/>";
    }

    private static String finish(String id, String status) {
        return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>";
    }
}
