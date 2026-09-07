package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import net.sf.joptsimple.KeyValuePair;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (var input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                try {
                    String[] fields = line.split("\\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = run(fields[0], value);
                    output.write("OK" + tab() + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR" + tab() + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String run(String operation, String input) {
        return switch (operation) {
            case "pair" -> pair(input);
            case "text" -> KeyValuePair.valueOf(input).toString();
            case "equal" -> equal(input);
            case "null" -> KeyValuePair.valueOf((String) null).toString();
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String pair(String input) {
        KeyValuePair pair = KeyValuePair.valueOf(input);
        return pair.key() + nul() + (pair.value() == null ? soh() : pair.value());
    }

    private static String equal(String input) {
        int separator = input.indexOf(nul());
        if (separator < 0) throw new IllegalArgumentException("equal input");
        return Boolean.toString(KeyValuePair.valueOf(input.substring(0, separator)).equals(KeyValuePair.valueOf(input.substring(separator + 1))));
    }

    private static String tab() { return String.valueOf((char) 9); }
    private static String nul() { return String.valueOf((char) 0); }
    private static String soh() { return String.valueOf((char) 1); }
}
