package nl2repobench.harness;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import org.apache.commons.dbutils.BasicRowProcessor;
import org.apache.commons.dbutils.handlers.ArrayHandler;
import org.apache.commons.dbutils.handlers.ColumnListHandler;
import org.apache.commons.dbutils.handlers.MapHandler;
import org.apache.commons.dbutils.handlers.ScalarHandler;

public final class CandidateMain {
    private CandidateMain() {}

    public static void main(String[] args) throws IOException {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
             BufferedWriter output = new BufferedWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                try {
                    String[] fields = line.split("\\t", -1);
                    if (fields.length != 2) throw new IllegalArgumentException("protocol");
                    String value = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
                    String result = execute(fields[0], value);
                    output.write("OK\t" + Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception failure) {
                    output.write("ERR\t" + Base64.getEncoder().encodeToString(
                        failure.getClass().getSimpleName().getBytes(StandardCharsets.UTF_8)));
                }
                output.newLine();
                output.flush();
            }
        }
    }

    private static String execute(String operation, String value) throws Exception {
        String[] parts = value.split("\\u0000", -1);
        return switch (operation) {
        case "array" -> join(new BasicRowProcessor().toArray(Fixture.current(parts[0], parts[1])));
        case "map" -> map(new BasicRowProcessor().toMap(Fixture.current(parts[0], parts[1])));
        case "map-get" -> mapGet(new BasicRowProcessor().toMap(Fixture.current(parts[0], parts[1])), parts[2]);
        case "array-handler" -> join(new ArrayHandler().handle(Fixture.result(parts[0], parts[1])));
        case "map-handler" -> mapOrNull(new MapHandler().handle(Fixture.result(parts[0], parts[1])));
        case "scalar-index" -> valueOf(new ScalarHandler<>(Integer.parseInt(parts[2])).handle(
            Fixture.result(parts[0], parts[1])));
        case "scalar-name" -> valueOf(new ScalarHandler<>(parts[2]).handle(Fixture.result(parts[0], parts[1])));
        case "column-index" -> join(new ColumnListHandler<>(Integer.parseInt(parts[2])).handle(
            Fixture.result(parts[0], parts[1])));
        case "column-name" -> join(new ColumnListHandler<>(parts[2]).handle(Fixture.result(parts[0], parts[1])));
        default -> throw new IllegalArgumentException("unknown operation");
        };
    }

    private static String join(Object[] values) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < values.length; i++) {
            if (i > 0) result.append('|');
            result.append(valueOf(values[i]));
        }
        return result.toString();
    }

    private static String join(List<?> values) {
        return join(values.toArray());
    }

    private static String map(Map<String, Object> values) {
        StringBuilder result = new StringBuilder();
        for (Map.Entry<String, Object> entry : values.entrySet()) {
            if (result.length() > 0) result.append(';');
            result.append(entry.getKey()).append('=').append(valueOf(entry.getValue()));
        }
        return result.toString();
    }

    private static String mapOrNull(Map<String, Object> values) {
        return values == null ? "<null>" : map(values);
    }

    private static String mapGet(Map<String, Object> values, String key) {
        return valueOf(values.get(key));
    }

    private static String valueOf(Object value) {
        return value == null ? "<null>" : String.valueOf(value);
    }

    private static final class Fixture {
        private Fixture() {}

        static ResultSet result(String labels, String rows) {
            String[] names = labels.split(",", -1);
            String[][] values = rows.isEmpty() ? new String[0][] : parseRows(rows, names.length);
            return ResultSetProxy.create(names, values);
        }

        static ResultSet current(String labels, String rows) throws Exception {
            ResultSet result = result(labels, rows);
            if (!result.next()) throw new IllegalArgumentException("empty result");
            return result;
        }

        private static String[][] parseRows(String data, int columns) {
            String[] encodedRows = data.split(";", -1);
            String[][] rows = new String[encodedRows.length][columns];
            for (int row = 0; row < encodedRows.length; row++) {
                String[] fields = encodedRows[row].split(",", -1);
                if (fields.length != columns) throw new IllegalArgumentException("column count");
                System.arraycopy(fields, 0, rows[row], 0, columns);
            }
            return rows;
        }
    }

    private static final class ResultSetProxy implements InvocationHandler {
        private final String[] labels;
        private final String[][] rows;
        private int cursor = -1;

        private ResultSetProxy(String[] labels, String[][] rows) {
            this.labels = labels.clone();
            this.rows = rows.clone();
        }

        static ResultSet create(String[] labels, String[][] rows) {
            return (ResultSet) Proxy.newProxyInstance(
                ResultSetProxy.class.getClassLoader(),
                new Class<?>[] {ResultSet.class},
                new ResultSetProxy(labels, rows)
            );
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            return switch (method.getName()) {
                case "next" -> next();
                case "getMetaData" -> metadata();
                case "getObject" -> getObject(args);
                case "wasNull", "isWrapperFor" -> false;
                case "toString" -> "ResultSetProxy";
                case "hashCode" -> System.identityHashCode(proxy);
                case "equals" -> proxy == args[0];
                default -> defaultValue(method.getReturnType());
            };
        }

        private boolean next() {
            if (cursor + 1 < rows.length) {
                cursor++;
                return true;
            }
            cursor = rows.length;
            return false;
        }

        private Object getObject(Object[] args) throws SQLException {
            if (cursor < 0 || cursor >= rows.length) throw new SQLException("cursor is not on a row");
            int column = args[0] instanceof Integer value ? value : columnIndex((String) args[0]);
            if (column < 1 || column > labels.length) throw new SQLException("invalid column");
            String value = rows[cursor][column - 1];
            return "~".equals(value) ? null : value;
        }

        private int columnIndex(String name) throws SQLException {
            for (int index = 0; index < labels.length; index++) {
                if (labels[index].equalsIgnoreCase(name)) return index + 1;
            }
            throw new SQLException("unknown column: " + name);
        }

        private ResultSetMetaData metadata() {
            InvocationHandler handler = (proxy, method, args) -> switch (method.getName()) {
                case "getColumnCount" -> labels.length;
                case "getColumnLabel", "getColumnName" -> {
                    int index = (Integer) args[0];
                    if (index < 1 || index > labels.length) throw new SQLException("invalid column");
                    yield labels[index - 1];
                }
                case "isWrapperFor" -> false;
                case "unwrap" -> throw new SQLException("not a wrapper");
                default -> defaultValue(method.getReturnType());
            };
            return (ResultSetMetaData) Proxy.newProxyInstance(
                ResultSetProxy.class.getClassLoader(),
                new Class<?>[] {ResultSetMetaData.class},
                handler
            );
        }

        private static Object defaultValue(Class<?> type) {
            if (!type.isPrimitive()) return null;
            if (type == boolean.class) return false;
            if (type == char.class) return '\0';
            if (type == byte.class) return (byte) 0;
            if (type == short.class) return (short) 0;
            if (type == int.class) return 0;
            if (type == long.class) return 0L;
            if (type == float.class) return 0.0f;
            if (type == double.class) return 0.0d;
            return null;
        }
    }
}
