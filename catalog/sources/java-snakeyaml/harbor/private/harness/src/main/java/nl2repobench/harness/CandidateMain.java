package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.yaml.snakeyaml.util.ArrayUtils;

/** Candidate-side JSON-lines adapter. It cannot create verifier reports. */
public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                try {
                    String operation = parseOperation(line);
                    output.write("{\"ok\":true,\"value\":\"" + escape(run(operation)) + "\"}");
                } catch (Throwable failure) {
                    output.write("{\"ok\":false,\"error\":\"" + failure.getClass().getSimpleName() + "\"}");
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String parseOperation(String line) {
        String prefix = "{\"op\":\"";
        if (!line.startsWith(prefix) || !line.endsWith("\"}")) throw new IllegalArgumentException("protocol");
        return line.substring(prefix.length(), line.length() - 2);
    }

    private static String run(String operation) {
        return switch (operation) {
            case "single-values" -> values(ArrayUtils.toUnmodifiableList(new String[] {"red", "blue"}));
            case "single-empty" -> values(ArrayUtils.toUnmodifiableList(new String[0]));
            case "single-backed" -> singleBacked();
            case "single-unmodifiable" -> singleUnmodifiable();
            case "single-oob" -> exception(() -> ArrayUtils.toUnmodifiableList(new String[] {"x"}).get(1));
            case "composite-values" -> values(ArrayUtils.toUnmodifiableCompositeList(new String[] {"a", "b"}, new String[] {"c"}));
            case "composite-first-backed" -> firstBacked();
            case "composite-second-backed" -> secondBacked();
            case "composite-unmodifiable" -> compositeUnmodifiable();
            case "composite-empty-left" -> values(ArrayUtils.toUnmodifiableCompositeList(new String[0], new String[] {"z"}));
            case "composite-empty-right" -> values(ArrayUtils.toUnmodifiableCompositeList(new String[] {"z"}, new String[0]));
            case "null-input" -> exception(() -> ArrayUtils.toUnmodifiableList((String[]) null));
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String singleBacked() {
        String[] array = {"red", "blue"};
        List<String> list = ArrayUtils.toUnmodifiableList(array);
        array[1] = "green";
        return list.get(1);
    }

    private static String firstBacked() {
        String[] first = {"a"};
        List<String> list = ArrayUtils.toUnmodifiableCompositeList(first, new String[] {"b"});
        first[0] = "x";
        return list.get(0);
    }

    private static String secondBacked() {
        String[] second = {"b"};
        List<String> list = ArrayUtils.toUnmodifiableCompositeList(new String[] {"a"}, second);
        second[0] = "y";
        return list.get(1);
    }

    private static String singleUnmodifiable() {
        return exception(() -> ArrayUtils.toUnmodifiableList(new String[] {"x"}).set(0, "y"));
    }

    private static String compositeUnmodifiable() {
        return exception(() -> ArrayUtils.toUnmodifiableCompositeList(new String[] {"x"}, new String[] {"y"}).set(0, "z"));
    }

    private static String values(List<String> values) {
        return values.size() + ":" + String.join("|", values);
    }

    private static String exception(Action action) {
        try {
            action.run();
            return "NO_EXCEPTION";
        } catch (Throwable failure) {
            return failure.getClass().getSimpleName();
        }
    }

    private static String escape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private interface Action { void run(); }
}
