package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.joda.time.format.FormatUtils;

public final class CandidateMain {
    private CandidateMain() {}
    public static void main(String[] args) throws IOException {
        try (var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             var out = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    String[] f = line.split("\t", -1);
                    if (f.length != 2) throw new IllegalArgumentException("protocol");
                    String value = new String(Base64.getDecoder().decode(f[1]), StandardCharsets.UTF_8);
                    String result = execute(f[0], value);
                    out.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception e) {
                    out.write("ERR\t" + Base64.getEncoder().encodeToString(e.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                out.newLine(); out.flush();
            }
        }
    }
    private static String execute(String op, String value) throws IOException {
        String[] p = value.split("\\|", -1);
        StringBuffer b = new StringBuffer();
        switch (op) {
            case "pad-int-buffer" -> FormatUtils.appendPaddedInteger(b, Integer.parseInt(p[0]), Integer.parseInt(p[1]));
            case "pad-long-buffer" -> FormatUtils.appendPaddedInteger(b, Long.parseLong(p[0]), Integer.parseInt(p[1]));
            case "pad-int-appendable" -> FormatUtils.appendPaddedInteger((Appendable)b, Integer.parseInt(p[0]), Integer.parseInt(p[1]));
            case "pad-long-writer" -> FormatUtils.writePaddedInteger(new StringWriterAdapter(b), Long.parseLong(p[0]), Integer.parseInt(p[1]));
            case "unpad-int" -> FormatUtils.appendUnpaddedInteger(b, Integer.parseInt(p[0]));
            case "unpad-long" -> FormatUtils.appendUnpaddedInteger(b, Long.parseLong(p[0]));
            case "unpad-int-writer" -> FormatUtils.writeUnpaddedInteger(new StringWriterAdapter(b), Integer.parseInt(p[0]));
            case "unpad-long-appendable" -> FormatUtils.appendUnpaddedInteger((Appendable)b, Long.parseLong(p[0]));
            case "digits" -> { return Integer.toString(FormatUtils.calculateDigitCount(Long.parseLong(p[0]))); }
            case "pad-min" -> FormatUtils.appendPaddedInteger(b, Integer.MIN_VALUE, Integer.parseInt(p[0]));
            default -> throw new IllegalArgumentException("unknown operation");
        }
        return b.toString();
    }
    private static final class StringWriterAdapter extends Writer {
        private final StringBuffer target;
        StringWriterAdapter(StringBuffer target) { this.target = target; }
        public void write(char[] c, int o, int l) { target.append(c, o, l); }
        public void flush() {}
        public void close() {}
    }
}
