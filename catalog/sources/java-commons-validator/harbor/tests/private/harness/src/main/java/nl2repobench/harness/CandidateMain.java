package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.regex.Pattern;
import org.apache.commons.validator.routines.RegexValidator;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (var input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                try {
                    String[] fields = line.split("\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String[] parts = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8).split("\u0000", -1);
                    String result = run(fields[0], parts);
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String run(String operation, String[] parts) {
        return switch (operation) {
            case "valid" -> Boolean.toString(new RegexValidator(parts[0]).isValid(parts[1]));
            case "invalid" -> Boolean.toString(new RegexValidator(parts[0]).isValid(parts[1]));
            case "match" -> encodeGroups(new RegexValidator(parts[0]).match(parts[1]));
            case "validate" -> value(new RegexValidator(parts[0]).validate(parts[1]));
            case "validate-empty" -> value(new RegexValidator(parts[0]).validate(parts[1]));
            case "case-insensitive" -> Boolean.toString(new RegexValidator(parts[0], false).isValid(parts[1]));
            case "patterns-copy" -> {
                RegexValidator validator = new RegexValidator(new String[] {"cat", "dog"});
                Pattern[] patterns = validator.getPatterns();
                patterns[0] = Pattern.compile("never");
                yield Boolean.toString(validator.isValid("dog"));
            }
            case "to-string" -> new RegexValidator(parts).toString();
            case "invalid-pattern" -> {
                try { new RegexValidator(parts[0]); yield "NO_EXCEPTION"; }
                catch (IllegalArgumentException failure) { yield failure.getClass().getSimpleName(); }
            }
            case "null-input" -> Boolean.toString(new RegexValidator(parts[0]).isValid(null));
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String encodeGroups(String[] groups) {
        if (groups == null) return "<null>";
        StringBuilder result = new StringBuilder();
        for (int index = 0; index < groups.length; index++) {
            if (index > 0) result.append('|');
            result.append(groups[index] == null ? "<null>" : groups[index]);
        }
        return result.toString();
    }

    private static String value(String value) { return value == null ? "<null>" : value; }
}
