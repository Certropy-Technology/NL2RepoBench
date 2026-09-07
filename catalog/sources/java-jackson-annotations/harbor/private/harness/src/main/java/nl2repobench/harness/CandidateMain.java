package nl2repobench.harness;

import com.fasterxml.jackson.annotation.JacksonAnnotation;
import com.fasterxml.jackson.annotation.JsonCreator;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class CandidateMain {
    private CandidateMain() {}

    @JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
    private static void propertiesFactory() {}

    public static void main(String[] args) throws Exception {
        try (var input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                try {
                    String[] fields = line.split("\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String argument = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = run(fields[0], argument);
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String run(String operation, String argument) throws Exception {
        return switch (operation) {
            case "values" -> String.join(",", java.util.Arrays.stream(JsonCreator.Mode.values()).map(Enum::name).toList());
            case "value-of" -> JsonCreator.Mode.valueOf(argument).name();
            case "default" -> JsonCreator.class.getMethod("mode").getDefaultValue().toString();
            case "return-type" -> JsonCreator.class.getMethod("mode").getReturnType().getName();
            case "targets" -> String.join(",", java.util.Arrays.stream(JsonCreator.class.getAnnotation(Target.class).value()).map(Enum::name).toList());
            case "retention" -> JsonCreator.class.getAnnotation(Retention.class).value().name();
            case "marker" -> Boolean.toString(JsonCreator.class.isAnnotationPresent(JacksonAnnotation.class));
            case "explicit" -> propertiesFactoryMode();
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String propertiesFactoryMode() throws NoSuchMethodException {
        return CandidateMain.class.getDeclaredMethod("propertiesFactory").getAnnotation(JsonCreator.class).mode().name();
    }
}
