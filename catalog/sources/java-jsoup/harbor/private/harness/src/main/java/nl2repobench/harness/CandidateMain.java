package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.jsoup.nodes.Attribute;

public final class CandidateMain {
    private CandidateMain() {}
    public static void main(String[] args) throws IOException {
        try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    String[] f = line.split("\t", -1);
                    if (f.length != 2) throw new IllegalArgumentException("protocol");
                    String[] p = new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8).split("\u0000", -1);
                    String result = switch (f[0]) {
                        case "construct" -> new Attribute(p[0], nullable(p[1])).getKey();
                        case "get-value" -> new Attribute(p[0], nullable(p[1])).getValue();
                        case "declared" -> Boolean.toString(new Attribute(p[0], nullable(p[1])).hasDeclaredValue());
                        case "set-key" -> { Attribute a = new Attribute(p[0], nullable(p[1])); a.setKey(p[2]); yield a.getKey(); }
                        case "set-value" -> { Attribute a = new Attribute(p[0], nullable(p[1])); yield a.setValue(nullable(p[2])); }
                        case "prefix" -> new Attribute(p[0], nullable(p[1])).prefix();
                        case "local" -> new Attribute(p[0], nullable(p[1])).localName();
                        default -> throw new IllegalArgumentException("unknown operation");
                    };
                    out.write("OK\t" + enc(result));
                } catch (Exception e) { out.write("ERR\t" + enc(e.getClass().getSimpleName())); }
                out.newLine(); out.flush();
            }
        }
    }
    private static String nullable(String s) { return "<NULL>".equals(s) ? null : s; }
    private static String enc(String s) { return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8)); }
}
