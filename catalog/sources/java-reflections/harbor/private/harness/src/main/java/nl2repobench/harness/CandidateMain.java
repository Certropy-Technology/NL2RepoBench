package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.reflections.util.FilterBuilder;

public final class CandidateMain {
    public static void main(String[] args) throws IOException {
        try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    String[] f = line.split("\t", -1);
                    if (f.length != 2) throw new IllegalArgumentException("protocol");
                    String[] p = new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8).split("\u0000", -1);
                    String result = run(f[0], p);
                    out.write("OK\t" + enc(result));
                } catch (Exception e) { out.write("ERR\t" + enc(e.getClass().getSimpleName())); }
                out.newLine(); out.flush();
            }
        }
    }
    private static String run(String op, String[] p) {
        return switch (op) {
            case "empty" -> Boolean.toString(new FilterBuilder().test(p[0]));
            case "include" -> Boolean.toString(new FilterBuilder().includePattern(p[0]).test(p[1]));
            case "exclude" -> Boolean.toString(new FilterBuilder().excludePattern(p[0]).test(p[1]));
            case "package" -> Boolean.toString(new FilterBuilder().includePackage(p[0]).test(p[1]));
            case "chain" -> Boolean.toString(new FilterBuilder().includePattern(p[0]).excludePattern(p[1]).test(p[2]));
            case "parse" -> Boolean.toString(FilterBuilder.parsePackages(p[0]).test(p[1]));
            case "alias" -> Boolean.toString(new FilterBuilder().include(p[0]).exclude(p[1]).test(p[2]));
            case "invalid" -> { try { FilterBuilder.parsePackages(p[0]); yield "NO_EXCEPTION"; } catch (RuntimeException e) { yield e.getClass().getSimpleName(); } }
            case "package-dollar" -> Boolean.toString(new FilterBuilder().includePackage(p[0]).test(p[1]));
            case "exclude-first" -> Boolean.toString(new FilterBuilder().excludePattern(p[0]).test(p[1]));
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }
    private static String enc(String value) { return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)); }
}
