package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.apache.commons.io.EndianUtils;

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
                    String[] parts = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8).split("\u0000", -1);
                    String result = run(fields[0], parts);
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String run(String operation, String[] parts) {
        return switch (operation) {
            case "read-int" -> Integer.toString(EndianUtils.readSwappedInteger(bytes(parts[0]), Integer.parseInt(parts[1])));
            case "read-long" -> Long.toString(EndianUtils.readSwappedLong(bytes(parts[0]), Integer.parseInt(parts[1])));
            case "read-short" -> Short.toString(EndianUtils.readSwappedShort(bytes(parts[0]), Integer.parseInt(parts[1])));
            case "read-uint" -> Long.toString(EndianUtils.readSwappedUnsignedInteger(bytes(parts[0]), Integer.parseInt(parts[1])));
            case "read-ushort" -> Integer.toString(EndianUtils.readSwappedUnsignedShort(bytes(parts[0]), Integer.parseInt(parts[1])));
            case "swap-int" -> Integer.toString(EndianUtils.swapInteger(Integer.parseInt(parts[0])));
            case "swap-long" -> Long.toString(EndianUtils.swapLong(Long.parseLong(parts[0])));
            case "swap-short" -> Short.toString(EndianUtils.swapShort(Short.parseShort(parts[0])));
            case "write-int" -> writeInt(parts);
            case "write-long" -> writeLong(parts);
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String writeInt(String[] parts) {
        byte[] data = bytes(parts[0]);
        EndianUtils.writeSwappedInteger(data, Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
        return hex(data);
    }

    private static String writeLong(String[] parts) {
        byte[] data = bytes(parts[0]);
        EndianUtils.writeSwappedLong(data, Integer.parseInt(parts[1]), Long.parseLong(parts[2]));
        return hex(data);
    }

    private static byte[] bytes(String hex) {
        if (hex.length() % 2 != 0) throw new IllegalArgumentException("hex byte string required");
        byte[] result = new byte[hex.length() / 2];
        for (int i = 0; i < result.length; i++) result[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        return result;
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) result.append(String.format("%02x", value & 255));
        return result.toString();
    }
}
