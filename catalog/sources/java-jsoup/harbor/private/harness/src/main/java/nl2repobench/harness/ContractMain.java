package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"trim-key", "empty-value", "null-value", "set-key", "set-value", "prefix", "local", "multi-colon", "key-error", "null-transition"};
    private ContractMain() {}
    public static void main(String[] args) throws Exception {
        String timeout = System.getProperty("nl2repobench.candidate.timeout", "300");
        Process candidate = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", timeout, "--", "/opt/java/openjdk/bin/java", "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-XX:CompressedClassSpaceSize=64m", "-Djava.awt.headless=true", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        var in = new BufferedWriter(new OutputStreamWriter(candidate.getOutputStream(), StandardCharsets.UTF_8));
        var out = new BufferedReader(new InputStreamReader(candidate.getInputStream(), StandardCharsets.UTF_8));
        boolean[] ok = new boolean[IDS.length];
        try {
            ok[0] = check(in, out, "construct", "  href  \u0000url", "href");
            ok[1] = check(in, out, "get-value", "x\u0000", "");
            ok[2] = check(in, out, "declared", "x\u0000<NULL>", "false");
            ok[3] = check(in, out, "set-key", "x\u0000v\u0000 data ", "data");
            ok[4] = check(in, out, "set-value", "x\u0000old\u0000new", "old");
            ok[5] = check(in, out, "prefix", "og:title\u0000v", "og");
            ok[6] = check(in, out, "local", ":name\u0000v", "name");
            ok[7] = check(in, out, "local", "a:b:c\u0000v", "b:c");
            ok[8] = error(in, out, "construct", "   \u0000v", "IllegalArgumentException");
            ok[9] = check(in, out, "set-value", "x\u0000old\u0000<NULL>", "old");
        } finally { in.close(); out.close(); }
        if (candidate.waitFor() != 0) java.util.Arrays.fill(ok, false);
        StringBuilder r = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        r.append(start("c", "jsoup Attribute contract", "CONTAINER", null)); boolean all = true;
        for (int i=0;i<IDS.length;i++) { String id="t"+i; r.append(start(id, IDS[i], "TEST", "c")).append(finish(id, ok[i] ? "SUCCESSFUL" : "FAILED")); all &= ok[i]; }
        r.append(finish("c", "SUCCESSFUL")).append("</e:events>\n"); System.out.print(r); if (!all) System.exit(1);
    }
    private static boolean check(BufferedWriter i, BufferedReader o, String op, String val, String expected) throws IOException { i.write(op+"\t"+enc(val)); i.newLine(); i.flush(); String l=o.readLine(); return l != null && l.startsWith("OK\t") && expected.equals(new String(Base64.getDecoder().decode(l.substring(3)), StandardCharsets.UTF_8)); }
    private static boolean error(BufferedWriter i, BufferedReader o, String op, String val, String expected) throws IOException { i.write(op+"\t"+enc(val)); i.newLine(); i.flush(); String l=o.readLine(); return l != null && l.startsWith("ERR\t") && expected.equals(new String(Base64.getDecoder().decode(l.substring(4)), StandardCharsets.UTF_8)); }
    private static String enc(String s) { return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8)); }
    private static String start(String id,String n,String type,String p){return "<e:started id=\""+id+"\" name=\""+n+"\""+(p==null?"":" parentId=\""+p+"\"")+" time=\"2026-01-01T00:00:00Z\" uniqueId=\""+id+"\" type=\""+type+"\"/>";}
    private static String finish(String id,String s){return "<e:finished id=\""+id+"\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""+s+"\"/></e:finished>";}
}
