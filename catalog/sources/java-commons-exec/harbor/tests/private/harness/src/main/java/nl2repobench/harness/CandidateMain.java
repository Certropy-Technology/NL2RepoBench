package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.util.StringUtils;

public final class CandidateMain {
    private static final int MAX_REQUEST_CHARS = 4 * 1024 * 1024;

    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = readBoundedLine(input)) != null) {
                String[] fields = line.split("\\t", -1);
                if (fields.length != 2) {
                    writeError(output, "protocol");
                    continue;
                }
                try {
                    String value = fields[1].equals("-")
                        ? null : new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = execute(fields[0], value);
                    String encoded = result == null ? "-" : Base64.getEncoder().encodeToString(
                        result.getBytes(StandardCharsets.UTF_8));
                    output.write("OK\t" + encoded);
                } catch (RuntimeException | IOException failure) {
                    writeError(output, failure.getClass().getSimpleName());
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String execute(String operation, String value) {
        if (value == null) {
            throw new IllegalArgumentException("null input");
        }
        switch (operation) {
            case "parse-executable":
                return CommandLine.parse(value).getExecutable();
            case "parse-argument":
                return CommandLine.parse(value).getArguments()[0];
            case "construct":
                return new CommandLine("tool").addArgument(value).toStrings()[1];
            case "quote":
                return StringUtils.quoteArgument(value);
            case "is-quoted":
                return Boolean.toString(StringUtils.isQuoted(value));
            case "split":
                return String.join("|", StringUtils.split(value, ","));
            case "join":
                return StringUtils.toString(value.split("\\|", -1), ",");
            case "substitute-strict":
            case "substitute-lenient": {
                Map<String, String> vars = new HashMap<>();
                vars.put("name", "demo");
                vars.put("root", "/opt");
                return StringUtils.stringSubstitution(value, vars, operation.endsWith("lenient")).toString();
            }
            case "separator":
                return StringUtils.fixFileSeparatorChar(value);
            default:
                throw new IllegalArgumentException("unknown operation");
        }
    }

    private static void writeError(BufferedWriter output, String message) throws IOException {
        output.write("ERR\t" + Base64.getEncoder().encodeToString(message.getBytes(StandardCharsets.UTF_8)));
    }

    private static String readBoundedLine(BufferedReader input) throws IOException {
        StringBuilder line = new StringBuilder();
        int character;
        while ((character = input.read()) != -1) {
            if (character == '\n') {
                return line.toString();
            }
            if (line.length() >= MAX_REQUEST_CHARS) {
                throw new IOException("request exceeds the size limit");
            }
            line.append((char) character);
        }
        return line.length() == 0 ? null : line.toString();
    }
}
