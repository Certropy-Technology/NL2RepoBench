package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.json.JSONObject;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                String[] fields = line.split("\t", -1);
                try {
                    String result;
                    if (fields.length == 1 && "quote-null".equals(fields[0])) {
                        result = JSONObject.quote(null);
                    } else if (fields.length == 2 && "quote".equals(fields[0])) {
                        result = JSONObject.quote(new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8));
                    } else throw new IllegalArgumentException("protocol");
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }
}
