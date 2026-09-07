package nl2repobench.harness;
import com.jayway.jsonpath.JsonPath;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
public final class CandidateMain {
  private CandidateMain() {}
  public static void main(String[] args) throws IOException {
    try (var in=new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8)); var out=new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
      String line; while ((line=in.readLine())!=null) { try { String[] f=line.split("\\t",-1); if(f.length!=2) throw new IllegalArgumentException("protocol"); String v=new String(Base64.getDecoder().decode(f[1]),StandardCharsets.UTF_8); String r=run(f[0],v); out.write("OK\t"+Base64.getEncoder().encodeToString(r.getBytes(StandardCharsets.UTF_8))); } catch(Exception e) { out.write("ERR\t"+Base64.getEncoder().encodeToString(e.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8))); } out.newLine(); out.flush(); }
    }
  }
  private static String run(String op,String v) { return switch(op) { case "inspect" -> { JsonPath p=JsonPath.compile(v); yield p.getPath()+"|"+p.isDefinite(); } case "static" -> Boolean.toString(JsonPath.isPathDefinite(v)); default -> throw new IllegalArgumentException("unknown operation"); }; }
}
