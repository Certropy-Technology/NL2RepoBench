package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"read-int", "read-long", "read-short", "read-uint", "read-ushort", "swap-int", "swap-long", "swap-short", "write-int", "write-long"};

    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        Process candidate = new ProcessBuilder(
            "/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
            "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", "300", "--",
            "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m",
            "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter input = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader output = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(input, output, "read-int", "7856341200\u00000", "305419896");
            passed[1] = check(input, output, "read-long", "0807060504030201\u00000", "72623859790382856");
            passed[2] = check(input, output, "read-short", "feff00\u00000", "-2");
            passed[3] = check(input, output, "read-uint", "ffffffff00\u00000", "4294967295");
            passed[4] = check(input, output, "read-ushort", "ffff00\u00000", "65535");
            passed[5] = check(input, output, "swap-int", "305419896", "2018915346");
            passed[6] = check(input, output, "swap-long", "72623859790382856", "578437695752307201");
            passed[7] = check(input, output, "swap-short", "4660", "13330");
            passed[8] = check(input, output, "write-int", "aa00000000bb\u00001\u0000305419896", "aa78563412bb");
            passed[9] = check(input, output, "write-long", "aa0000000000000000bb\u00001\u000072623859790382856", "aa0807060504030201bb");
        } finally { input.close(); output.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Commons IO EndianUtils contract", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; report.append(start(id, IDS[i], "TEST", "c")); report.append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report);
        if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter in, BufferedReader out, String operation, String value, String expected) throws IOException {
        in.write(operation + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush();
        String line = out.readLine();
        return line != null && line.startsWith("OK\t") && expected.equals(new String(Base64.getDecoder().decode(line.substring(3)), StandardCharsets.UTF_8));
    }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
