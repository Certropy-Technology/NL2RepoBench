package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.kohsuke.github.GHCommitState;

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
                    String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = switch (fields[0]) {
                        case "name" -> GHCommitState.valueOf(value).name();
                        case "ordinal" -> Integer.toString(GHCommitState.valueOf(value).ordinal());
                        case "values" -> String.join(",", java.util.Arrays.stream(GHCommitState.values()).map(Enum::name).toList());
                        case "isolation" -> { GHCommitState[] first = GHCommitState.values(); first[0] = GHCommitState.SUCCESS; yield GHCommitState.values()[0].name(); }
                        default -> throw new IllegalArgumentException("operation");
                    };
                    out.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    out.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                out.newLine(); out.flush();
            }
        }
    }
}
