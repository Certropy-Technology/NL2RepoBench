package nl2repobench.harness;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Arrays;

final class ResultSetProxy implements InvocationHandler {
    private final String[] labels;
    private final String[][] rows;
    private int cursor = -1;

    private ResultSetProxy(String[] labels, String[][] rows) {
        this.labels = labels.clone();
        this.rows = rows.clone();
    }

    static ResultSet create(String[] labels, String[][] rows) {
        return (ResultSet) Proxy.newProxyInstance(
            ResultSetProxy.class.getClassLoader(), new Class<?>[] {ResultSet.class},
            new ResultSetProxy(labels, rows));
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        return switch (method.getName()) {
        case "next" -> next();
        case "getMetaData" -> metadata();
        case "getObject" -> getObject(args);
        case "wasNull" -> false;
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
        int column = args[0] instanceof Integer integer ? integer : columnIndex((String) args[0]);
        if (column < 1 || column > labels.length) throw new SQLException("invalid column");
        String value = rows[cursor][column - 1];
        return "~".equals(value) ? null : value;
    }

    private int columnIndex(String name) throws SQLException {
        for (int i = 0; i < labels.length; i++) {
            if (labels[i].equalsIgnoreCase(name)) return i + 1;
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
            ResultSetProxy.class.getClassLoader(), new Class<?>[] {ResultSetMetaData.class}, handler);
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
