package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class ContractMain {
  private static final String[] IDS = {"identity", "upper-camel", "spaces", "upper-underscore", "lower-underscore", "dashes", "dots", "acronym", "leading-underscore", "nonletter"};
  private ContractMain() {}
  public static void main(String[] args) throws Exception {
    boolean[] pass = new boolean[IDS.length];
    Process p = new ProcessBuilder(System.getProperty("nl2repobench.python", "/usr/local/bin/python3"), "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", System.getProperty("nl2repobench.candidate.timeout", "300"), "--", System.getProperty("nl2repobench.java", "/opt/java/openjdk/bin/java"), "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
    var in = new BufferedWriter(new OutputStreamWriter(p.getOutputStream(), StandardCharsets.UTF_8));
    var out = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8));
    pass[0] = check(in, out, "policy", "IDENTITY:someFieldName", "someFieldName");
    pass[1] = check(in, out, "policy", "UPPER_CAMEL_CASE:someFieldName", "SomeFieldName");
    pass[2] = check(in, out, "policy", "UPPER_CAMEL_CASE_WITH_SPACES:someFieldName", "Some Field Name");
    pass[3] = check(in, out, "policy", "UPPER_CASE_WITH_UNDERSCORES:someFieldName", "SOME_FIELD_NAME");
    pass[4] = check(in, out, "policy", "LOWER_CASE_WITH_UNDERSCORES:someFieldName", "some_field_name");
    pass[5] = check(in, out, "policy", "LOWER_CASE_WITH_DASHES:someFieldName", "some-field-name");
    pass[6] = check(in, out, "policy", "LOWER_CASE_WITH_DOTS:someFieldName", "some.field.name");
    pass[7] = check(in, out, "policy", "UPPER_CASE_WITH_UNDERSCORES:aURL", "A_U_R_L");
    pass[8] = check(in, out, "policy", "UPPER_CAMEL_CASE:_someFieldName", "_SomeFieldName");
    pass[9] = check(in, out, "policy", "UPPER_CAMEL_CASE:_123value", "_123value");
    try { in.close(); } catch (IOException ignored) {}
    out.close();
    if (p.waitFor() != 0) Arrays.fill(pass, false);
    StringBuilder xml = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
    xml.append("<e:started id=\"c\" name=\"Gson naming contract\" time=\"2026-01-01T00:00:00Z\" uniqueId=\"[engine:nl2repobench]\" type=\"CONTAINER\"/>");
    boolean all = true;
    for (int i=0;i<IDS.length;i++) { xml.append("<e:started id=\"t"+i+"\" name=\""+IDS[i]+"\" parentId=\"c\" time=\"2026-01-01T00:00:00Z\" uniqueId=\"[test:"+IDS[i]+"]\" type=\"TEST\"/>"); xml.append("<e:finished id=\"t"+i+"\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""+(pass[i]?"SUCCESSFUL":"FAILED")+"\"/></e:finished>"); all &= pass[i]; }
    xml.append("<e:finished id=\"c\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\"SUCCESSFUL\"/></e:finished></e:events>\n");
    System.out.print(xml); if (!all) System.exit(1);
  }
  private static boolean check(BufferedWriter in, BufferedReader out, String op, String value, String expected) {
    try { in.write(op+"\t"+Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); in.newLine(); in.flush(); String line=out.readLine(); if(line==null)return false; String[] f=line.split("\t",-1); return f.length==2 && f[0].equals("OK") && expected.equals(new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8)); } catch(Exception e){return false;}
  }
}
