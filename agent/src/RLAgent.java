import java.lang.instrument.Instrumentation;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/**
 * Research agent for option B. Compiled without any game classes: everything goes through reflection.
 * Registers Lua globals on the game's main Lua environment so server Lua mods (which run on the main
 * server thread) can call into Java-only APIs:
 *   rlLoadArea(x, y, z)  -> ServerMap.instance.characterIn(x, y, z) and importantAreaIn(x, y)
 */
public class RLAgent {
    private static void log(String s) { System.out.println("RLAGENT " + s); }

    public static void premain(String args, Instrumentation inst) {
        Thread t = new Thread(RLAgent::installWhenReady, "rl-agent-install");
        t.setDaemon(true);
        t.start();
    }


    /** Evaluate "pkg.Class.staticField.method(1,2).field" style paths by reflection. */
    static Object eval(String expr) throws Exception {
        String[] parts = expr.split("\\.(?![^(]*\\))");
        // find the longest prefix that is a class name
        Class<?> cls = null; int idx = 0; StringBuilder name = new StringBuilder();
        for (; idx < parts.length; idx++) {
            if (name.length() > 0) name.append('.');
            name.append(parts[idx]);
            try { cls = Class.forName(name.toString()); idx++; break; } catch (ClassNotFoundException ignored) { }
        }
        if (cls == null) throw new IllegalArgumentException("no class in " + expr);
        Object cur = null; boolean isStatic = true; Class<?> curCls = cls;
        for (; idx < parts.length; idx++) {
            String tok = parts[idx];
            int p = tok.indexOf('(');
            if (p < 0) {
                java.lang.reflect.Field f = findField(curCls, tok);
                f.setAccessible(true);
                cur = f.get(cur);
            } else {
                String mname = tok.substring(0, p);
                String argStr = tok.substring(p + 1, tok.length() - 1).trim();
                String[] as = argStr.isEmpty() ? new String[0] : argStr.split(",");
                Object[] args = new Object[as.length];
                for (int i = 0; i < as.length; i++) args[i] = Integer.valueOf(as[i].trim());
                Method m = null;
                for (Method c : curCls.getMethods()) {
                    if (!c.getName().equals(mname) || c.getParameterCount() != args.length) continue;
                    m = c; break;
                }
                if (m == null) for (Method c : curCls.getDeclaredMethods()) {
                    if (c.getName().equals(mname) && c.getParameterCount() == args.length) { m = c; break; }
                }
                if (m == null) throw new NoSuchMethodException(tok + " on " + curCls.getName());
                m.setAccessible(true);
                cur = m.invoke(cur, args);
            }
            if (cur == null) return null;
            curCls = cur.getClass();
        }
        return cur;
    }

    static java.lang.reflect.Field findField(Class<?> c, String n) throws NoSuchFieldException {
        for (Class<?> k = c; k != null; k = k.getSuperclass()) {
            try { return k.getDeclaredField(n); } catch (NoSuchFieldException ignored) { }
        }
        throw new NoSuchFieldException(n + " on " + c.getName());
    }

    private static void installWhenReady() {
        try {
            Class<?> lm = null;
            Object env = null;
            for (int i = 0; i < 600 && env == null; i++) {
                Thread.sleep(500);
                try {
                    lm = Class.forName("zombie.Lua.LuaManager");
                    env = lm.getField("env").get(null);
                } catch (Throwable ignored) { }
            }
            if (env == null) { log("LuaManager.env never became available"); return; }
            Class<?> jf = Class.forName("se.krka.kahlua.vm.JavaFunction");
            Class<?> frame = Class.forName("se.krka.kahlua.vm.LuaCallFrame");
            Method frameGet = frame.getMethod("get", int.class);
            Method framePush = frame.getMethod("push", Object.class);
            Method rawset = Class.forName("se.krka.kahlua.vm.KahluaTable").getMethod("rawset", Object.class, Object.class);

            InvocationHandler h = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                Object cf = a[0];
                try {
                    int x = ((Number) frameGet.invoke(cf, 0)).intValue();
                    int y = ((Number) frameGet.invoke(cf, 1)).intValue();
                    int z = ((Number) frameGet.invoke(cf, 2)).intValue();
                    Class<?> sm = Class.forName("zombie.network.ServerMap");
                    Object inst = sm.getField("instance").get(null);
                    if (inst == null) { framePush.invoke(cf, Boolean.FALSE); return 1; }
                    sm.getMethod("characterIn", int.class, int.class, int.class).invoke(inst, x, y, z);
                    sm.getMethod("importantAreaIn", int.class, int.class).invoke(inst, x, y);
                    framePush.invoke(cf, Boolean.TRUE);
                } catch (Throwable e) {
                    log("rlLoadArea failed: " + e + " / " + e.getCause());
                    framePush.invoke(cf, Boolean.FALSE);
                }
                return 1;
            };
            Object fn = Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, h);
            rawset.invoke(env, "rlLoadArea", fn);
            InvocationHandler h2 = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                Object cf = a[0];
                String r;
                try { r = String.valueOf(eval((String) frameGet.invoke(cf, 0))); }
                catch (Throwable e) { Throwable c = e; while (c.getCause() != null) c = c.getCause(); r = "ERR " + c; }
                framePush.invoke(cf, r);
                return 1;
            };
            rawset.invoke(env, "rlGet", Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, h2));

            log("installed rlLoadArea");
        } catch (Throwable e) {
            log("install failed: " + e);
        }
    }
}
