package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"empty", "include", "exclude", "package", "chain", "parse", "alias", "invalid", "package-dollar", "exclude-first"};
    public static void main(String[] args) throws Exception {
        String timeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", timeout, "--", "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        var in = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        var out = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        try {
            passed[0] = check(in, out, "empty", "anything", "true");
            passed[1] = check(in, out, "include", "foo\\..*\u0000foo.Bar", "true");
            passed[2] = check(in, out, "exclude", "foo\\..*\u0000foo.Bar", "false");
            passed[3] = check(in, out, "package", "org.example\u0000org.example.Service", "true");
            passed[4] = check(in, out, "chain", "org\\..*\u0000org\\.internal\\..*\u0000org.internal.Secret", "false");
            passed[5] = check(in, out, "parse", "+java, -java.lang\u0000java.util.List", "true");
            passed[6] = check(in, out, "alias", "foo\\..*\u0000foo\\.internal\\..*\u0000foo.internal.X", "false");
            passed[7] = check(in, out, "invalid", "*bad", "ReflectionsException");
            passed[8] = check(in, out, "package-dollar", "a$b\u0000a$b.Inner", "true");
            passed[9] = check(in, out, "exclude-first", "foo\\..*\u0000bar", "true");
        } finally { in.close(); out.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(passed, false);
        StringBuilder xml = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        xml.append(start("c", "Reflections FilterBuilder contract", "CONTAINER", null)); boolean all = true;
        for (int i = 0; i < IDS.length; i++) { String id = "t" + i; xml.append(start(id, IDS[i], "TEST", "c")); xml.append(finish(id, passed[i] ? "SUCCESSFUL" : "FAILED")); all &= passed[i]; }
        xml.append(finish("c", "SUCCESSFUL")).append("</e:events>"); System.out.println(xml); if (!all) System.exit(1);
    }
    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) throws IOException { in.write(op + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush(); String line = out.readLine(); return line != null && line.startsWith("OK\t") && expected.equals(new String(Base64.getDecoder().decode(line.substring(3)), StandardCharsets.UTF_8)); }
    private static String start(String id, String name, String type, String parent) { return "<e:started id=\""+id+"\" name=\""+name+"\""+(parent==null?"":" parentId=\""+parent+"\"")+" time=\"2026-01-01T00:00:00Z\" uniqueId=\""+id+"\" type=\""+type+"\"/>"; }
    private static String finish(String id, String status) { return "<e:finished id=\""+id+"\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""+status+"\"/></e:finished>"; }
}
