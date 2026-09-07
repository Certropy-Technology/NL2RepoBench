package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.apache.commons.lang3.StringUtils;

public final class CandidateMain {
    private CandidateMain() {}
    public static void main(String[] args) throws IOException {
        try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    String[] fields = line.split("\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String result = execute(fields[0]);
                    out.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception error) {
                    out.write("ERR\t" + Base64.getEncoder().encodeToString(error.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                out.newLine(); out.flush();
            }
        }
    }
    private static String execute(String operation) {
        return switch (operation) {
            case "is-empty" -> Boolean.toString(StringUtils.isEmpty(null)) + ":" + StringUtils.isEmpty("") + ":" + StringUtils.isEmpty(" ");
            case "is-blank" -> Boolean.toString(StringUtils.isBlank(null)) + ":" + StringUtils.isBlank(" \t") + ":" + StringUtils.isBlank("a");
            case "contains" -> StringUtils.contains("alpha", 'p') + ":" + StringUtils.contains("alpha", 'z') + ":" + StringUtils.contains(null, 'a');
            case "count-char" -> Integer.toString(StringUtils.countMatches("banana", 'a'));
            case "count-sub" -> Integer.toString(StringUtils.countMatches("ababa", "aba"));
            case "default" -> StringUtils.defaultString(null) + "|" + StringUtils.defaultString("x");
            case "default-custom" -> StringUtils.defaultString(null, "fallback") + "|" + StringUtils.defaultString("x", "fallback");
            case "capitalize" -> StringUtils.capitalize("cat") + "|" + StringUtils.capitalize("") + "|" + display(StringUtils.capitalize(null));
            case "uncapitalize" -> StringUtils.uncapitalize("CAT") + "|" + StringUtils.uncapitalize("cat");
            case "reverse" -> StringUtils.reverse("stressed") + "|" + StringUtils.reverse("A\uD83D\uDE00B");
            case "split-whitespace" -> join(StringUtils.split("  red  green\tblue "));
            case "split-char" -> join(StringUtils.split("a::b:c", ':'));
            case "substring-negative" -> StringUtils.substring("abcdef", -3);
            case "substring-range" -> StringUtils.substring("abcdef", -4, -1);
            case "left" -> StringUtils.left("abcdef", 2) + "|" + StringUtils.left("abcdef", -1);
            case "right" -> StringUtils.right("abcdef", 2) + "|" + StringUtils.right("abcdef", -1);
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }
    private static String join(String[] values) {
        if (values == null) return "<null>";
        return String.join("|", values);
    }
    private static String display(String value) { return value == null ? "<null>" : value; }
}
