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
                } else {
                    try {
                        String value = fields[1].equals("-") ? null
                                : new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                        String result = execute(fields[0], value);
                        String encoded = result == null ? "-"
                                : Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8));
                        output.write("OK\t" + encoded);
                    } catch (RuntimeException | IOException failure) {
                        writeError(output, failure.getClass().getSimpleName());
                    }
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
        case "parse-exec":
            return CommandLine.parse(value).getExecutable();
        case "parse-args":
            return join(CommandLine.parse(value).toStrings());
        case "add-arg": {
            String[] parts = parts(value, 2);
            CommandLine command = new CommandLine(parts[0]);
            command.addArgument(parts[1]);
            return command.toString();
        }
        case "to-string": {
            String[] parts = parts(value, 2);
            CommandLine command = new CommandLine(parts[0]);
            command.addArgument(parts[1]);
            return command.toString();
        }
        case "quote-space":
        case "quote-double":
            return StringUtils.quoteArgument(value);
        case "is-quoted":
            return Boolean.toString(StringUtils.isQuoted(value));
        case "split": {
            String[] parts = parts(value, 2);
            return join(StringUtils.split(parts[0], parts[1]));
        }
        case "join": {
            String[] parts = parts(value, 2);
            return StringUtils.toString(parts[0].split("\\u001f", -1), parts[1]);
        }
        case "subst": {
            String[] parts = parts(value, 3);
            Map<String, String> variables = new HashMap<>();
            if (!parts[1].isEmpty()) {
                for (String pair : parts[1].split(";", -1)) {
                    String[] entry = pair.split("=", 2);
                    if (entry.length != 2) throw new IllegalArgumentException("bad variable");
                    variables.put(entry[0], entry[1]);
                }
            }
            return StringUtils.stringSubstitution(parts[0], variables, "lenient".equals(parts[2])).toString();
        }
        default:
            throw new IllegalArgumentException("unknown operation");
        }
    }

    private static String[] parts(String value, int expected) {
        String[] parts = value.split("\\u0000", -1);
        if (parts.length != expected) throw new IllegalArgumentException("structured input required");
        return parts;
    }

    private static String join(String[] values) {
        return String.join("\u001f", values);
    }

    private static void writeError(BufferedWriter output, String message) throws IOException {
        output.write("ERR\t" + Base64.getEncoder().encodeToString(message.getBytes(StandardCharsets.UTF_8)));
    }

    private static String readBoundedLine(BufferedReader input) throws IOException {
        StringBuilder line = new StringBuilder();
        int character;
        while ((character = input.read()) != -1) {
            if (character == '\n') return line.toString();
            if (line.length() >= MAX_REQUEST_CHARS) throw new IOException("request exceeds size limit");
            line.append((char) character);
        }
        return line.length() == 0 ? null : line.toString();
    }
}
