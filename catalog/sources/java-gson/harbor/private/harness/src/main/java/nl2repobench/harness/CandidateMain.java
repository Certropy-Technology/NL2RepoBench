package nl2repobench.harness;

import com.google.gson.FieldNamingPolicy;
import java.io.*;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class CandidateMain {
  private static final class Sample {
    String someFieldName;
    String aURL;
    String _someFieldName;
    String _123value;
    String éField;
  }
  private CandidateMain() {}
  public static void main(String[] args) throws IOException {
    try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
         var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
      String line;
      while ((line = in.readLine()) != null) {
        try {
          String[] fields = line.split("\t", -1);
          if (fields.length != 2) throw new IllegalArgumentException("protocol");
          String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
          String result = execute(fields[0], value);
          out.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
          out.write("ERR\t" + Base64.getEncoder().encodeToString(e.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
        }
        out.newLine(); out.flush();
      }
    }
  }
  private static String execute(String operation, String value) throws Exception {
    if (operation.equals("policy")) {
      int colon = value.indexOf(':');
      if (colon < 0) throw new IllegalArgumentException("policy:field");
      Field field = Sample.class.getDeclaredField(value.substring(colon + 1));
      return FieldNamingPolicy.valueOf(valuePolicy(value)).translateName(field);
    }
    if (operation.equals("all")) {
      Field field = Sample.class.getDeclaredField(value);
      StringBuilder b = new StringBuilder();
      for (FieldNamingPolicy p : FieldNamingPolicy.values()) { if (b.length() > 0) b.append('|'); b.append(p.translateName(field)); }
      return b.toString();
    }
    if (operation.equals("enum")) return Integer.toString(FieldNamingPolicy.values().length);
    throw new IllegalArgumentException("unknown operation");
  }
  private static String valuePolicy(String value) {
    int colon = value.indexOf(':');
    if (colon < 0) throw new IllegalArgumentException("policy:field");
    return value.substring(0, colon);
  }
}
