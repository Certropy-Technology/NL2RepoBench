package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.impl.NoOpLog;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (var input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
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
        NoOpLog logger = operation.equals("construct-default") ? new NoOpLog() : new NoOpLog(value);
        return switch (operation) {
            case "construct-default", "construct-name" -> "NoOpLog";
            case "levels" -> Boolean.toString(!logger.isDebugEnabled()) + "," + !logger.isErrorEnabled()
                + "," + !logger.isFatalEnabled() + "," + !logger.isInfoEnabled()
                + "," + !logger.isTraceEnabled() + "," + !logger.isWarnEnabled();
            case "debug-call" -> { logger.debug(value); logger.debug(value, null); yield "ok"; }
            case "error-call" -> { logger.error(value); logger.error(value, null); yield "ok"; }
            case "fatal-call" -> { logger.fatal(value); logger.fatal(value, null); yield "ok"; }
            case "info-call" -> { logger.info(value); logger.info(value, null); yield "ok"; }
            case "trace-call" -> { logger.trace(value); logger.trace(value, null); yield "ok"; }
            case "warn-call" -> { logger.warn(value); logger.warn(value, null); yield "ok"; }
            case "type" -> Boolean.toString(logger instanceof Log && logger instanceof java.io.Serializable);
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }
}
