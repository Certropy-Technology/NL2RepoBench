package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.apache.commons.text.similarity.HammingDistance;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                String[] fields = line.split("\t", -1);
                try {
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = execute(fields[0], value);
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String execute(String operation, String value) {
        if (!"apply".equals(operation)) throw new IllegalArgumentException("unknown operation");
        String[] parts = value.split("\\|", -1);
        if (parts.length != 2) throw new IllegalArgumentException("pair input required");
        CharSequence left = "NULL".equals(parts[0]) ? null : parts[0];
        CharSequence right = "NULL".equals(parts[1]) ? null : parts[1];
        try {
            return Integer.toString(new HammingDistance().apply(left, right));
        } catch (IllegalArgumentException expected) {
            return "EX:" + expected.getClass().getSimpleName();
        }
    }
}
