package nl2repobench.harness;
import de.svenkubiak.http.Result;
import de.svenkubiak.utils.Utils;
import java.io.*; import java.net.URI; import java.nio.charset.StandardCharsets; import java.util.*; import java.util.Base64;
public final class CandidateMain {
 private CandidateMain() {}
 public static void main(String[] args) throws IOException {
  try (var in=new BufferedReader(new InputStreamReader(System.in,StandardCharsets.UTF_8)); var out=new BufferedWriter(new OutputStreamWriter(System.out,StandardCharsets.UTF_8))) { String line; while((line=in.readLine())!=null) { try { String[] f=line.split("\t",-1); if(f.length!=2) throw new IllegalArgumentException("protocol"); String v=new String(Base64.getDecoder().decode(f[1]),StandardCharsets.UTF_8); String r=execute(f[0],v); out.write("OK\t"+enc(r)); } catch(Exception e) { out.write("ERR\t"+enc(e.getClass().getSimpleName())); } out.newLine(); out.flush(); } }
 }
 private static String execute(String op,String v) throws Exception {
  return switch(op) {
   case "create" -> { Result r=Result.create(); yield r.body()+"|"+r.status()+"|"+r.isValid(); }
   case "body" -> Result.create().withBody("<NULL>".equals(v)?null:v).body();
   case "header" -> { String[] p=v.split("\\|",-1); yield Result.create().withHeader(p[0],p[1]).header(p[0]); }
   case "binary" -> { Result r=Result.create().withBinaryBody(v.getBytes(StandardCharsets.UTF_8)); byte[] b=r.binaryBody(); b[0]='X'; yield new String(r.binaryBody(),StandardCharsets.UTF_8); }
   case "status" -> Integer.toString(Result.create().withStatus(Integer.parseInt(v)).status());
   case "valid" -> Boolean.toString(Result.create().withStatus(Integer.parseInt(v)).isValid());
   case "expected" -> { String[] p=v.split("\\|",-1); int s=Integer.parseInt(p[0]); int[] e=new int[p.length-1]; for(int i=1;i<p.length;i++) e[i-1]=Integer.parseInt(p[i]); yield Boolean.toString(Result.create().withStatus(s).isValid(e)); }
   case "success" -> Boolean.toString(Utils.isSuccessCode(Integer.parseInt(v)));
   case "form" -> { Map<String,String> m=new LinkedHashMap<>(); for(String item:v.split(";",-1)){String[] p=item.split("=",2);m.put(p[0],p.length==1?"":p[1]);} yield Utils.getFormDataAsString(m); }
   case "clean" -> Utils.clean(v);
   case "uri" -> { URI u=Utils.toAllowedUri(v); yield u.getScheme().toLowerCase(Locale.ROOT)+"|"+u.getHost(); }
   case "error" -> Result.create().withBody(v).error();
   default -> throw new IllegalArgumentException("unknown operation");
  };
 }
 private static String enc(String s){return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8));}
}
