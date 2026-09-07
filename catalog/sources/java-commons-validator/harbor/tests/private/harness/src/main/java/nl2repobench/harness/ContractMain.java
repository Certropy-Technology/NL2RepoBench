package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class ContractMain {
    private static final String[] IDS = {"valid-full", "invalid-full", "match-groups", "validate-groups", "validate-empty-group", "case-insensitive", "patterns-copy", "to-string", "invalid-pattern", "null-input"};
    private static final String[] OPS = {"valid", "invalid", "match", "validate", "validate-empty", "case-insensitive", "patterns-copy", "to-string", "invalid-pattern", "null-input"};
    private static final String[][] ARGS = {{"^item-([0-9]+)$", "item-42"}, {"^item-([0-9]+)$", "prefix-item-42"}, {"(item)-(\\d+)", "item-42"}, {"(item)-(\\d+)", "item-42"}, {"(a)?b", "b"}, {"hello", "HeLLo"}, {"unused", "unused"}, {"cat", "dog"}, {"", "unused"}, {"^x$", "x"}};
    private static final String[] EXPECTED = {"true", "false", "item|42", "item42", "", "true", "true", "RegexValidator{cat,dog}", "IllegalArgumentException", "false"};

    public static void main(String[] args) throws Exception {
        Process process = new ProcessBuilder("/usr/local/bin/python3", "-I", "-m", "nl2repobench.verification.candidate_process_cli", "--cwd", "/tmp/java-harness", "--uid", "10001", "--timeout-sec", "300", "--", "/opt/java/openjdk/bin/java", "-Xmx256m", "-cp", System.getProperty("nl2repobench.candidate.classpath", "/tmp/java-harness/candidate-classes"), "nl2repobench.harness.CandidateMain").redirectError(ProcessBuilder.Redirect.INHERIT).start();
        var input = new BufferedWriter(new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8));
        var output = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));
        boolean[] passed = new boolean[IDS.length];
        for (int index = 0; index < IDS.length; index++) passed[index] = check(input, output, OPS[index], String.join("\u0000", ARGS[index]), EXPECTED[index]);
        input.close(); output.close(); process.waitFor();
        StringBuilder xml = new StringBuilder("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        xml.append("<e:started id=\"c\" name=\"RegexValidator\" time=\"2026-01-01T00:00:00Z\" uniqueId=\"[engine:nl2repobench]\" type=\"CONTAINER\"/>");
        boolean all = true;
        for (int index = 0; index < IDS.length; index++) { all &= passed[index]; xml.append("<e:started id=\"t").append(index).append("\" name=\"").append(IDS[index]).append("\" time=\"2026-01-01T00:00:00Z\" uniqueId=\"[test:").append(IDS[index]).append("]\" type=\"TEST\" parentId=\"c\"/><e:finished id=\"t").append(index).append("\" time=\"2026-01-01T00:00:00Z\"><j:result status=\"").append(passed[index] ? "SUCCESSFUL" : "FAILED").append("\"/></e:finished>"); }
        System.out.println(xml + "<e:finished id=\"c\" time=\"2026-01-01T00:00:00Z\"><j:result status=\"SUCCESSFUL\"/></e:finished></e:events>");
        if (!all) System.exit(1);
    }

    private static boolean check(BufferedWriter input, BufferedReader output, String operation, String value, String expected) throws IOException {
        input.write(operation + "\t" + Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8))); input.newLine(); input.flush();
        String line = output.readLine(); if (line == null) return false; String[] fields = line.split("\t", -1);
        return fields.length == 2 && fields[0].equals("OK") && new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8).equals(expected);
    }
}
