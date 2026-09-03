package nl2repobench.harness;

import example.text.TextUtil;

public final class ContractMain {
    private ContractMain() {}

    public static void main(String[] args) {
        String[] ids = {"ascii-trim", "empty-input", "null-input"};
        boolean[] passed = {
            check(() -> "hello".equals(TextUtil.normalize("  hello  "))),
            check(() -> "".equals(TextUtil.normalize("\t\n"))),
            check(() -> {
                if (TextUtil.normalize(null) != null) {
                    throw new AssertionError("null input was changed");
                }
            }),
        };
        StringBuilder report = new StringBuilder();
        report.append("<e:events xmlns:e=\"https://schemas.opentest4j.org/reporting/events/0.1.0\" ");
        report.append("xmlns:j=\"https://schemas.junit.org/open-test-reporting\">");
        report.append(start("c", "Java contract", "[engine:nl2repobench]", "CONTAINER", null));
        boolean allPassed = true;
        for (int i = 0; i < ids.length; i++) {
            String eventId = "t" + i;
            String uniqueId = "[engine:nl2repobench]/[test:" + ids[i] + "]";
            report.append(start(eventId, ids[i], uniqueId, "TEST", "c"));
            String status = passed[i] ? "SUCCESSFUL" : "FAILED";
            report.append(finish(eventId, status));
            allPassed &= passed[i];
        }
        report.append(finish("c", allPassed ? "SUCCESSFUL" : "FAILED"));
        report.append("</e:events>\n");
        System.out.print(report);
        if (!allPassed) {
            System.exit(1);
        }
    }

    private static boolean check(Check check) {
        try {
            check.run();
            return true;
        } catch (RuntimeException | AssertionError failure) {
            return false;
        }
    }

    private static String start(String id, String name, String uniqueId, String type, String parent) {
        String parentAttribute = parent == null ? "" : " parentId=\"" + parent + "\"";
        return "<e:started id=\"" + id + "\" name=\"" + name + "\"" + parentAttribute
            + " time=\"2026-01-01T00:00:00Z\" uniqueId=\"" + uniqueId + "\" type=\""
            + type + "\"/>";
    }

    private static String finish(String id, String status) {
        return "<e:finished id=\"" + id + "\" time=\"2026-01-01T00:00:00.010Z\"><j:result status=\""
            + status + "\"/></e:finished>";
    }

    @FunctionalInterface
    private interface Check {
        void run();
    }
}
