package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Base64;
import org.apache.commons.pool3.PooledObjectState;
import org.apache.commons.pool3.impl.EvictionConfig;

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
                    String result = execute(fields[0], value);
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine(); output.flush();
            }
        }
    }

    private static String execute(String operation, String value) {
        String[] parts = value.split("\\u0000", -1);
        return switch (operation) {
        case "enum" -> enumNames();
        case "positive" -> config(parts[0], parts[1], Integer.parseInt(parts[2]));
        case "disabled" -> config(parts[0], parts[1], Integer.parseInt(parts[2]));
        case "minidle" -> Integer.toString(new EvictionConfig(Duration.ofMillis(1), Duration.ofMillis(2), Integer.parseInt(parts[0])).getMinIdle());
        case "thread-false" -> Boolean.toString(EvictionConfig.isEvictionThread());
        case "thread-true" -> {
            String old = Thread.currentThread().getName();
            Thread.currentThread().setName("commons-pool-evictor");
            try { yield Boolean.toString(EvictionConfig.isEvictionThread()); }
            finally { Thread.currentThread().setName(old); }
        }
        case "text" -> new EvictionConfig(Duration.ofMillis(Long.parseLong(parts[0])), Duration.ofMillis(Long.parseLong(parts[1])), Integer.parseInt(parts[2])).toString();
        default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String enumNames() {
        StringBuilder result = new StringBuilder();
        for (PooledObjectState state : PooledObjectState.values()) {
            if (result.length() > 0) result.append('|');
            result.append(state.name()).append(':').append(state.ordinal());
        }
        return result.toString();
    }

    private static String config(String hard, String soft, int minIdle) {
        Duration hardDuration = "null".equals(hard) ? null : Duration.ofMillis(Long.parseLong(hard));
        Duration softDuration = "null".equals(soft) ? null : Duration.ofMillis(Long.parseLong(soft));
        EvictionConfig config = new EvictionConfig(hardDuration, softDuration, minIdle);
        return config.getIdleEvictDuration().toMillis() + "|" + config.getIdleSoftEvictDuration().toMillis() + "|" + config.getMinIdle();
    }
}
