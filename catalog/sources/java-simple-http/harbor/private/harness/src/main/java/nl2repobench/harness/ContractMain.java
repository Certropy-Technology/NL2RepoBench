package nl2repobench.harness;
import java.io.*; import java.nio.charset.StandardCharsets; import java.util.*;
public final class ContractMain {
 private static final String[] IDS={"create","body-null","header","binary","status","valid-success","valid-failure","expected","success-edge","form-order","clean","uri"};
 private ContractMain() {}
 public static void main(String[] args) throws Exception {
  String timeout=System.getProperty("nl2repobench.candidate.timeout","300");
  Process p=new ProcessBuilder("/usr/local/bin/python3","-I","-m","nl2repobench.verification.candidate_process_cli","--cwd","/tmp/java-harness","--uid","10001","--timeout-sec",timeout,"--","/opt/java/openjdk/bin/java","-Xmx256m","-XX:MaxMetaspaceSize=128m","-XX:MaxDirectMemorySize=64m","-Djava.awt.headless=true","-cp",System.getProperty("nl2repobench.candidate.classpath","/tmp/java-harness/candidate-classes"),"nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
  var in=new BufferedWriter(new OutputStreamWriter(p.getOutputStream(),StandardCharsets.UTF_8)); var out=new BufferedReader(new InputStreamReader(p.getInputStream(),StandardCharsets.UTF_8)); boolean[] ok=new boolean[IDS.length];
  try { ok[0]=check(in,out,"create","","|-1|false"); ok[1]=check(in,out,"body","<NULL>",""); ok[2]=check(in,out,"header","X-Test|value","value"); ok[3]=check(in,out,"binary","bytes","bytes"); ok[4]=check(in,out,"status","204","204"); ok[5]=check(in,out,"valid-success","201","true"); ok[6]=check(in,out,"valid-failure","299","false"); ok[7]=check(in,out,"expected","404|200|404","true"); ok[8]=check(in,out,"success-edge","226","true"); ok[9]=check(in,out,"form-order","b=two words;a=x+y","b=two+words&a=x%2By"); ok[10]=check(in,out,"clean","A! b-9_\u00e9","A b9"); ok[11]=check(in,out,"uri","HTTPS://example.test/path","https|example.test"); } finally { in.close(); out.close(); }
  if(p.waitFor()!=0) Arrays.fill(ok,false); StringBuilder r=new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">"); r.append(start("c","simple-http contract","CONTAINER",null)); boolean all=true; for(int i=0;i<ok.length;i++){String id="t"+i; r.append(start(id,IDS[i],"TEST","c")).append(finish(id,ok[i]?"SUCCESSFUL":"FAILED")); all&=ok[i];} r.append(finish("c","SUCCESSFUL")); System.out.print(r); if(!all) System.exit(1);
 }
 private static boolean check(BufferedWriter i,BufferedReader o,String op,String val,String expected)throws IOException{i.write(op+"\t"+enc(val));i.newLine();i.flush();String l=o.readLine();return l!=null&&l.startsWith("OK\t")&&expected.equals(new String(Base64.getDecoder().decode(l.substring(3)),StandardCharsets.UTF_8));}
 private static String enc(String s){return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8));}
 private static String start(String id,String n,String type,String parent){return "<e:started id=\""+id+"\" name=\""+n+"\""+(parent==null?"":" parentId=\""+parent+"\"")+" time=\"2026-01-01T00:00:00Z\" uniqueId=\""+id+"\" type=\""+type+"\"/>";}
 private static String finish(String id,String s){return "<e:finished id=\""+id+"\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""+s+"\"/></e:finished>";}
}
