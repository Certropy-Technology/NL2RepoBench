package nl2repobench.harness;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.stream.Collectors;
import org.apache.commons.net.util.SubnetUtils;

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
                output.newLine(); output.flush();
            }
        }
    }

    private static String execute(String operation, String value) {
        return switch (operation) {
            case "cidr-summary" -> summary(new SubnetUtils(value).getInfo());
            case "default-range" -> range(new SubnetUtils(value).getInfo());
            case "inclusive-range" -> { SubnetUtils subnet = new SubnetUtils(value); subnet.setInclusiveHostCount(true); yield range(subnet.getInfo()); }
            case "mask-constructor" -> summary(new SubnetUtils(value.split("\\|", -1)[0], value.split("\\|", -1)[1]).getInfo());
            case "large-count" -> { SubnetUtils subnet = new SubnetUtils(value); subnet.setInclusiveHostCount(true); yield Long.toString(subnet.getInfo().getAddressCountLong()); }
            case "invalid-input" -> { try { new SubnetUtils(value); yield "accepted"; } catch (RuntimeException failure) { yield failure.getClass().getSimpleName(); } }
            case "address-array" -> String.join(",", new SubnetUtils(value).getInfo().getAllAddresses());
            case "address-stream" -> new SubnetUtils(value).getInfo().streamAddressStrings().collect(Collectors.joining(","));
            case "navigation" -> { SubnetUtils subnet = new SubnetUtils(value); yield subnet.getNext().getInfo().getNetworkAddress() + "|" + subnet.getPrevious().getInfo().getNetworkAddress(); }
            case "packed-integer" -> Integer.toString(new SubnetUtils(value + "/32").getInfo().asInteger(value));
            default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String summary(SubnetUtils.SubnetInfo info) {
        return info.getAddress() + "|" + info.getNetmask() + "|" + info.getNetworkAddress() + "|"
                + info.getBroadcastAddress() + "|" + info.getCidrSignature() + "|" + info.getAddressCountLong();
    }

    private static String range(SubnetUtils.SubnetInfo info) {
        return info.getLowAddress() + "|" + info.getHighAddress() + "|" + info.getAddressCountLong()
                + "|" + info.isInRange(info.getLowAddress()) + "|" + info.isInRange(info.getBroadcastAddress());
    }
}
