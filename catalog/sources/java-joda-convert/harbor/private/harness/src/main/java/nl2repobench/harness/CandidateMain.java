package nl2repobench.harness;

import java.io.*;
import java.lang.annotation.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.Base64;
import org.joda.convert.FromString;
import org.joda.convert.ToString;

public final class CandidateMain {
  private CandidateMain() {}
  public static final class Fixture {
    @FromString public Fixture(String value) {}
    @FromString public static Fixture parse(String value) { return new Fixture(value); }
    @ToString public String text() { return "fixture"; }
    public String plain() { return "plain"; }
  }
  public static void main(String[] args) throws IOException {
    try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
         var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
      String line;
      while ((line = in.readLine()) != null) {
        try {
          String[] f = line.split("\\t", -1);
          if (f.length != 2) throw new IllegalArgumentException("protocol");
          String value = new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8);
          String result = execute(f[0], value);
          out.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception ex) {
          out.write("ERR\t" + Base64.getEncoder().encodeToString(ex.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
        }
        out.newLine(); out.flush();
      }
    }
  }
  private static String execute(String operation, String ignored) {
    try {
      Class<FromString> from = FromString.class;
      Class<ToString> to = ToString.class;
      return switch (operation) {
        case "from-target" -> targets(from).toString();
        case "to-target" -> targets(to).toString();
        case "from-retention" -> retention(from);
        case "to-retention" -> retention(to);
        case "from-method" -> Boolean.toString(Fixture.class.getDeclaredMethod("parse", String.class).isAnnotationPresent(from));
        case "from-constructor" -> Boolean.toString(Fixture.class.getDeclaredConstructor(String.class).isAnnotationPresent(from));
        case "to-method" -> Boolean.toString(Fixture.class.getDeclaredMethod("text").isAnnotationPresent(to));
        case "plain-method" -> Boolean.toString(!Fixture.class.getDeclaredMethod("plain").isAnnotationPresent(to));
        case "no-elements" -> Integer.toString(from.getDeclaredMethods().length + to.getDeclaredMethods().length);
        case "distinct" -> Boolean.toString(!from.equals(to) && !from.getName().equals(to.getName()));
        default -> throw new IllegalArgumentException("unknown operation");
      };
    } catch (ReflectiveOperationException ex) { throw new IllegalStateException(ex); }
  }
  private static String targets(Class<? extends Annotation> type) {
    return Arrays.stream(type.getAnnotation(Target.class).value()).map(Enum::name).sorted().reduce((a,b) -> a + "," + b).orElse("");
  }
  private static String retention(Class<? extends Annotation> type) { return type.getAnnotation(Retention.class).value().name(); }
}
