package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import org.apache.commons.collections4.CollectionUtils;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                String[] fields = line.split("\\t", -1);
                if (fields.length != 2) {
                    writeError(output, "protocol");
                } else {
                    try {
                        String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                        String result = execute(fields[0], value);
                        output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                    } catch (RuntimeException failure) {
                        writeError(output, failure.getClass().getSimpleName());
                    }
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String execute(String operation, String value) {
        switch (operation) {
            case "empty":
                return Boolean.toString(CollectionUtils.isEmpty(nullableList(value)));
            case "not-empty":
                return Boolean.toString(CollectionUtils.isNotEmpty(nullableList(value)));
            case "cardinality": {
                String[] parts = pair(value);
                return Integer.toString(CollectionUtils.cardinality(parts[0], values(parts[1])));
            }
            case "contains-any": {
                String[] parts = pair(value);
                return Boolean.toString(CollectionUtils.containsAny(values(parts[0]), values(parts[1])));
            }
            case "equal": {
                String[] parts = pair(value);
                return Boolean.toString(CollectionUtils.isEqualCollection(values(parts[0]), values(parts[1])));
            }
            case "add-ignore-null": {
                String[] parts = pair(value);
                List<String> target = values(parts[0]);
                String item = "NULL".equals(parts[1]) ? null : parts[1];
                boolean changed = CollectionUtils.addIgnoreNull(target, item);
                return Boolean.toString(changed) + ":" + join(target);
            }
            case "size":
                return Integer.toString(CollectionUtils.size(values(value)));
            case "size-empty":
                return Boolean.toString(CollectionUtils.sizeIsEmpty(values(value)));
            default:
                throw new IllegalArgumentException("unknown operation");
        }
    }

    private static List<String> nullableList(String value) {
        return "NULL".equals(value) ? null : values(value);
    }

    private static List<String> values(String value) {
        if (value.isEmpty()) {
            return new ArrayList<>();
        }
        return new ArrayList<>(Arrays.asList(value.split(",", -1)));
    }

    private static String[] pair(String value) {
        String[] parts = value.split("\\|", -1);
        if (parts.length != 2) {
            throw new IllegalArgumentException("pair input required");
        }
        return parts;
    }

    private static String join(List<String> values) {
        return String.join(",", values);
    }

    private static void writeError(BufferedWriter output, String message) throws IOException {
        output.write("ERR\t" + Base64.getEncoder().encodeToString(message.getBytes(StandardCharsets.UTF_8)));
    }
}
