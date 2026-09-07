package nl2repobench.harness;

import com.cedarsoftware.util.ByteUtilities;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    String[] fields = line.split("\\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = run(fields[0], value);
                    out.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    out.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                out.newLine(); out.flush();
            }
        }
    }

    private static String run(String op, String value) {
        return switch (op) {
            case "encode" -> nullable(ByteUtilities.encode(parseHex(value)));
            case "decode-string" -> nullable(ByteUtilities.encode(ByteUtilities.decode(value)));
            case "decode-charsequence" -> nullable(ByteUtilities.encode(ByteUtilities.decode((CharSequence) value)));
            case "hex-char" -> Character.toString(ByteUtilities.toHexChar(Integer.parseInt(value)));
            case "gzip-default" -> Boolean.toString(ByteUtilities.isGzipped(parseHex(value)));
            case "gzip-offset" -> { String[] p = value.split("\\u0000", -1); yield Boolean.toString(ByteUtilities.isGzipped(parseHex(p[0]), Integer.parseInt(p[1]))); }
            case "index-first" -> { String[] p = value.split("\\u0000", -1); yield Integer.toString(ByteUtilities.indexOf(parseHex(p[0]), parseHex(p[1]), Integer.parseInt(p[2]))); }
            case "index-last" -> { String[] p = value.split("\\u0000", -1); yield Integer.toString(ByteUtilities.lastIndexOf(parseHex(p[0]), parseHex(p[1]), Integer.parseInt(p[2]))); }
            case "index-last-default" -> { String[] p = value.split("\\u0000", -1); yield Integer.toString(ByteUtilities.lastIndexOf(parseHex(p[0]), parseHex(p[1]))); }
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static byte[] parseHex(String text) {
        if ("<null>".equals(text)) return null;
        if ((text.length() & 1) != 0) throw new IllegalArgumentException("hex");
        byte[] result = new byte[text.length() / 2];
        for (int i = 0; i < result.length; i++) result[i] = (byte) Integer.parseInt(text.substring(i * 2, i * 2 + 2), 16);
        return result;
    }

    private static String nullable(Object value) { return value == null ? "<null>" : value.toString(); }
}
