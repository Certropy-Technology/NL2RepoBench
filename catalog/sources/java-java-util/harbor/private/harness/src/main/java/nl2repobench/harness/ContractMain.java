package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class ContractMain {
    private static final String[] IDS = {"hex-encode", "hex-decode", "hex-decode-charsequence", "hex-invalid", "hex-odd", "hex-digit", "gzip-default", "gzip-offset", "index-first", "index-last"};
    private ContractMain() {}

    public static void main(String[] args) throws Exception {
        String timeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli",
                "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", timeout, "--",
                "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m",
                "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
                "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        var in = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        var out = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(in, out, "encode", "00ff102a", "00FF102A");
            passed[1] = check(in, out, "decode-string", "00fF10", "00FF10");
            passed[2] = check(in, out, "decode-charsequence", "aBcD", "ABCD");
            passed[3] = check(in, out, "decode-string", "0g", "<null>");
            passed[4] = check(in, out, "decode-string", "abc", "<null>");
            passed[5] = check(in, out, "hex-char", "-1", "F");
            passed[6] = check(in, out, "gzip-default", "1f8b00", "true");
            passed[7] = check(in, out, "gzip-offset", "001f8b00\u00001", "true");
            passed[8] = check(in, out, "index-first", "0011221122\u00001122\u00000", "1");
            passed[9] = check(in, out, "index-last", "0011221122\u00001122\u00004", "3");
        } finally { in.close(); out.close(); }
        if (candidate.waitFor() != 0) Arrays.fill(passed, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Java Util ByteUtilities contract", "CONTAINER", null));
        boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; report.append(start(id, IDS[i], "TEST", "c")); report.append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n");
        System.out.print(report); if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws Exception {
        in.write(op + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush();
        String line = out.readLine(); if (line == null) return false; String[] f = line.split("\\t", -1);
        return f.length == 2 && f[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8));
    }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
