package nl2repobench.harness;

import java.io.*;
import java.lang.reflect.Array;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.Base64;
import org.apache.commons.jexl3.JexlArithmetic;

public final class CandidateMain {
    private CandidateMain() {}
    public static void main(String[] args) throws IOException {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    String[] fields = line.split("\\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = execute(fields[0], value);
                    out.write("OK\t" + encode(result));
                } catch (Exception failure) {
                    out.write("ERR\t" + encode(failure.getClass().getSimpleName()));
                }
                out.newLine(); out.flush();
            }
        }
    }
    private static String execute(String operation, String value) {
        JexlArithmetic a = new JexlArithmetic(false);
        return switch (operation) {
            case "bool" -> Boolean.toString(a.toBoolean(parse(value)));
            case "double" -> Double.toString(a.toDouble(parse(value)));
            case "int" -> Integer.toString(a.toInteger(parse(value)));
            case "long" -> Long.toString(a.toLong(parse(value)));
            case "string" -> a.toString(parse(value));
            case "identifier" -> printable(JexlArithmetic.parseIdentifier(parse(value)));
            case "size" -> Integer.toString(a.size(container(value)));
            case "size-default" -> Integer.toString(a.size(container(value), 9));
            case "empty" -> Boolean.toString(a.empty(container(value)));
            case "starts" -> {
                String[] p = value.split("\\u0000", -1);
                yield printable(a.startsWith(parse(p[0]), parse(p[1])));
            }
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }
    private static Object parse(String value) {
        if ("null".equals(value)) return null;
        if (value.startsWith("i:")) return Integer.valueOf(value.substring(2));
        if (value.startsWith("d:")) return Double.valueOf(value.substring(2));
        if ("NaN".equals(value)) return Double.NaN;
        if ("true".equals(value)) return Boolean.TRUE;
        if ("false".equals(value)) return Boolean.FALSE;
        return value;
    }
    private static Object container(String value) {
        String[] p = value.split(":", 2);
        return switch (p[0]) {
            case "null" -> null;
            case "string" -> p.length == 1 ? "" : p[1];
            case "list" -> new ArrayList<>(Collections.nCopies(Integer.parseInt(p[1]), "x"));
            case "map" -> {
                LinkedHashMap<String, Object> result = new LinkedHashMap<>();
                for (int index = 0; index < Integer.parseInt(p[1]); index++) result.put("k" + index, "x");
                yield result;
            }
            case "array" -> new Object[Integer.parseInt(p[1])];
            case "object" -> new Object();
            default -> throw new IllegalArgumentException("container");
        };
    }
    private static String printable(Object value) { return value == null ? "<null>" : String.valueOf(value); }
    private static String encode(String value) { return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)); }
}
