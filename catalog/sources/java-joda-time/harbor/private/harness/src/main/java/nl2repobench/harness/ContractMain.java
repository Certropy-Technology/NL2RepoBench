package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class ContractMain {
    private static final String[] IDS = {"pad-int", "pad-long", "pad-appendable", "pad-writer", "unpad-int", "unpad-long", "unpad-writer", "unpad-appendable", "digit-count", "minimum-int"};
    private ContractMain() {}
    public static void main(String[] args) throws Exception {
        boolean[] p = new boolean[IDS.length];
        Process child = new ProcessBuilder(System.getProperty("nl2repobench.python", "/usr/local/bin/python3"), "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", System.getProperty("nl2repobench.candidate.timeout", "300"), "--", System.getProperty("nl2repobench.java", "/opt/java/openjdk/bin/java"), "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        BufferedWriter in = new BufferedWriter(new OutputStreamWriter(child.getOutputStream(), StandardCharsets.UTF_8));
        BufferedReader out = new BufferedReader(new InputStreamReader(child.getInputStream(), StandardCharsets.UTF_8));
        try {
            p[0] = check(in, out, "pad-int-buffer", "-7|4", "-0007");
            p[1] = check(in, out, "pad-long-buffer", "1234567890123|15", "001234567890123");
            p[2] = check(in, out, "pad-int-appendable", "42|5", "00042");
            p[3] = check(in, out, "pad-long-writer", "-9|3", "-009");
            p[4] = check(in, out, "unpad-int", "-42", "-42");
            p[5] = check(in, out, "unpad-long", "9223372036854775807", "9223372036854775807");
            p[6] = check(in, out, "unpad-int-writer", "0", "0");
            p[7] = check(in, out, "unpad-long-appendable", "-9000000000", "-9000000000");
            p[8] = check(in, out, "digits", "-9223372036854775808", "19");
            p[9] = check(in, out, "pad-min", "12", "-002147483648");
        } finally { try { in.close(); } catch (IOException ignored) {} }
        out.close();
        if (child.waitFor() != 0) Arrays.fill(p, false);
        StringBuilder r = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        r.append(start("c", "Java Joda-Time FormatUtils contract", "[engine:nl2repobench]", "CONTAINER", null)); boolean all = true;
        for (int i=0;i<IDS.length;i++) { r.append(start("t"+i, IDS[i], "[engine:nl2repobench]/[test:"+IDS[i]+"]", "TEST", "c")); r.append(finish("t"+i, p[i] ? "SUCCESSFUL" : "FAILED")); all &= p[i]; }
        r.append(finish("c", "SUCCESSFUL")).append("</e:events>\n"); System.out.print(r); if (!all) System.exit(1);
    }
    private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) { try { in.write(op+"\t"+Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush(); String line=out.readLine(); if(line==null)return false; String[] f=line.split("\t",-1); return f.length==2 && f[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8)); } catch(Exception e){return false;} }
    private static String start(String id,String name,String uid,String type,String parent){return "<e:started id=\""+id+"\" name=\""+name+"\""+(parent==null?"":" parentId=\""+parent+"\"")+" time=\"2026-01-01T00:00:00Z\" uniqueId=\""+uid+"\" type=\""+type+"\"/>";}
    private static String finish(String id,String status){return "<e:finished id=\""+id+"\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""+status+"\"/></e:finished>";}
}
