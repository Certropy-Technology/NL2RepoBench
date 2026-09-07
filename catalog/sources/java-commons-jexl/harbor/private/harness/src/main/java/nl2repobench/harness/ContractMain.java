package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"bool-null", "bool-zero", "bool-text", "double-empty", "double-bool",
        "int-fraction-error", "long-decimal", "string-nan", "identifier-zero", "identifier-leading-zero",
        "size-string", "size-array", "size-default", "empty-list", "starts-both-null", "starts-prefix"};
    private ContractMain() {}
    public static void main(String[] args) throws Exception {
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m",
            "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001",
            "--timeout-sec", "300", "--", "/opt/java/openjdk/bin/java", "-Xmx256m",
            "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp",
            System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
            "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter in = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader out = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] pass = new boolean[IDS.length];
        try {
            pass[0] = check(in, out, "bool", "null", "false");
            pass[1] = check(in, out, "bool", "i:0", "false");
            pass[2] = check(in, out, "bool", "ready", "true");
            pass[3] = check(in, out, "double", "", "NaN");
            pass[4] = check(in, out, "double", "true", "1.0");
            pass[5] = checkError(in, out, "int", "1.5", "ArithmeticException");
            pass[6] = check(in, out, "long", "3.0", "3");
            pass[7] = check(in, out, "string", "NaN", "");
            pass[8] = check(in, out, "identifier", "0", "0");
            pass[9] = check(in, out, "identifier", "01", "<null>");
            pass[10] = check(in, out, "size", "string:abcd", "4");
            pass[11] = check(in, out, "size", "array:3", "3");
            pass[12] = check(in, out, "size-default", "object:x", "9");
            pass[13] = check(in, out, "empty", "list:0", "true");
            pass[14] = check(in, out, "starts", "null\u0000null", "true");
            pass[15] = check(in, out, "starts", "commons\u0000com", "true");
        } finally { in.close(); out.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(pass, false);
        StringBuilder report = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Commons JEXL contract", "CONTAINER", null)); boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; report.append(start(id, IDS[i], "TEST", "c")); report.append(finish(id, pass[i] ? "SUCCESSFUL" : "FAILED")); all &= pass[i]; }
        report.append(finish("c", "SUCCESSFUL")).append("</e:events>\n"); System.out.print(report); if (!all) System.exit(1);
    }
    private static String enc(String s) { return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8)); }
    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException {
        in.write(op + "\t" + enc(value)); in.newLine(); in.flush(); String line = out.readLine();
        return line != null && line.startsWith("OK\t") && expected.equals(new String(Base64.getDecoder().decode(line.substring(3)), StandardCharsets.UTF_8));
    }
    private static boolean checkError(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException {
        in.write(op + "\t" + enc(value)); in.newLine(); in.flush(); String line = out.readLine();
        return line != null && line.startsWith("ERR\t") && expected.equals(new String(Base64.getDecoder().decode(line.substring(4)), StandardCharsets.UTF_8));
    }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + (parent == null ? "" : " parentId=\"" + parent + "\"") + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + id + "\" type=\"" + type + "\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"" + status + "\"/></e:finished>"; }
}
