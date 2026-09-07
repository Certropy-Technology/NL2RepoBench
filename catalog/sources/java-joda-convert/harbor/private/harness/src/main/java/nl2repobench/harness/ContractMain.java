package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class ContractMain {
  private static final String[] IDS = {"from-target","to-target","from-retention","to-retention","from-method","from-constructor","to-method","plain-method","no-elements","distinct"};
  private ContractMain() {}
  public static void main(String[] args) throws Exception {
    boolean[] passed = new boolean[IDS.length];
    Process p = new ProcessBuilder(
        System.getProperty("nl2repobench.python", "/usr/local/bin/python3"),
        "-I", "-m", "nl2repobench.verification.candidate_process_cli",
        "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec",
        System.getProperty("nl2repobench.candidate.timeout", "300"), "--",
        System.getProperty("nl2repobench.java", "/opt/java/openjdk/bin/java"),
        "-Xmx256m", "-XX:MaxMetaspaceSize=128m", "-Djava.awt.headless=true",
        "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"),
        "nl2repobench.harness.CandidateMain"
    ).redirectError(ProcessBuilder.Redirect.INHERIT).start();
    try (var input = new BufferedWriter(new OutputStreamWriter(p.getOutputStream(), StandardCharsets.UTF_8)); var output = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8))) {
      passed[0] = check(input, output, IDS[0], "CONSTRUCTOR,METHOD"); passed[1] = check(input, output, IDS[1], "METHOD");
      passed[2] = check(input, output, IDS[2], "RUNTIME"); passed[3] = check(input, output, IDS[3], "RUNTIME");
      passed[4] = check(input, output, IDS[4], "true"); passed[5] = check(input, output, IDS[5], "true");
      passed[6] = check(input, output, IDS[6], "true"); passed[7] = check(input, output, IDS[7], "true");
      passed[8] = check(input, output, IDS[8], "0"); passed[9] = check(input, output, IDS[9], "true");
    }
    int exit = p.waitFor();
    StringBuilder xml = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
    xml.append(start("c", "Joda-Convert annotation contract", "[engine:nl2repobench]", "CONTAINER", null));
    boolean all = exit == 0;
    for (int i=0;i<IDS.length;i++) { all &= passed[i]; xml.append(start("t"+i, IDS[i], "[engine:nl2repobench]/[test:"+IDS[i]+"]", "TEST", "c")); xml.append(finish("t"+i, passed[i] ? "SUCCESSFUL" : "FAILED")); }
    xml.append(finish("c", "SUCCESSFUL")).append("</e:events>\n"); System.out.print(xml); if (!all) System.exit(1);
  }
  private static boolean check(BufferedWriter in, BufferedReader out, String op, String expected) { try { in.write(op+"\t"+Base64.getEncoder().encodeToString(new byte[0])); in.newLine(); in.flush(); String[] f=out.readLine().split("\\t",-1); return f.length==2 && f[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8)); } catch(Exception e) { return false; } }
  private static String start(String id,String name,String uid,String type,String parent) { return "<e:started id=\""+id+"\" name=\""+name+"\""+(parent==null?"":" parentId=\""+parent+"\"")+" time=\"2026-01-01T00:00:00Z\" uniqueId=\""+uid+"\" type=\""+type+"\"/>"; }
  private static String finish(String id,String status) { return "<e:finished id=\""+id+"\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""+status+"\"/></e:finished>"; }
}
