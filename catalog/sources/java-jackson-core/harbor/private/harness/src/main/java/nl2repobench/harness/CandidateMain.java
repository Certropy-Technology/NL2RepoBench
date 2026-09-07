package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import tools.jackson.core.JsonPointer;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws Exception {
        try (var input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                try {
                    String[] request = request(line);
                    String value = run(request[0], request[1]);
                    output.write("{\"ok\":true,\"value\":\"" + encode(value) + "\"}");
                } catch (Exception failure) {
                    output.write("{\"ok\":false,\"error\":\"" + failure.getClass().getSimpleName() + "\"}");
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String[] request(String line) {
        String prefix = "{\"op\":\"";
        String marker = "\",\"args\":\"";
        if (!line.startsWith(prefix) || !line.endsWith("\"}")) throw new IllegalArgumentException("protocol");
        int split = line.indexOf(marker, prefix.length());
        if (split < 0) throw new IllegalArgumentException("protocol");
        return new String[] {line.substring(prefix.length(), split), decode(line.substring(split + marker.length(), line.length() - 2))};
    }

    private static String run(String operation, String args) {
        String[] values = args.split("\u0000", -1);
        return switch (operation) {
            case "basic" -> basic(pointer(values[0]));
            case "escape" -> basic(pointer(values[0]));
            case "invalid" -> { pointer(values[0]); yield "unexpected"; }
            case "property" -> property(pointer(values[0]), values[1]);
            case "element" -> element(pointer(values[0]), Integer.parseInt(values[1]));
            case "navigation" -> navigation(pointer(values[0]));
            case "append-property" -> pointer(values[0]).appendProperty(values[1]).toString();
            case "append-index" -> pointer(values[0]).appendIndex(Integer.parseInt(values[1])).toString();
            case "append-negative" -> { pointer(values[0]).appendIndex(-1); yield "unexpected"; }
            case "empty" -> basic(JsonPointer.empty());
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static JsonPointer pointer(String expression) { return "<null>".equals(expression) ? JsonPointer.compile(null) : JsonPointer.compile(expression); }
    private static String basic(JsonPointer p) { return p + "|" + p.length() + "|" + p.matches() + "|" + nullable(p.getMatchingProperty()) + "|" + p.getMatchingIndex() + "|" + p.mayMatchProperty() + "|" + p.mayMatchElement(); }
    private static String property(JsonPointer p, String name) { JsonPointer tail = p.matchProperty(name); return p.matchesProperty(name) + "|" + nullable(tail); }
    private static String element(JsonPointer p, int index) { JsonPointer tail = p.matchElement(index); return p.matchesElement(index) + "|" + nullable(tail); }
    private static String navigation(JsonPointer p) { return nullable(p.tail()) + "|" + nullable(p.head()); }
    private static String nullable(Object value) { return value == null ? "<null>" : value.toString(); }
    private static String encode(String value) { return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8)); }
    private static String decode(String value) { return new String(Base64.getDecoder().decode(value), StandardCharsets.UTF_8); }
}
