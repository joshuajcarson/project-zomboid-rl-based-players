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
        // agent args, ';' separated: client | classes=<prefix>,<prefix> | control=<port> | channel=<port>
        // (the clock itself reads -Drl.timescale)
        java.util.Map<String, String> a = new java.util.HashMap<>();
        if (args != null) for (String kv : args.split(";")) {
            int i = kv.indexOf('=');
            a.put(i < 0 ? kv : kv.substring(0, i), i < 0 ? "" : kv.substring(i + 1));
        }
        if (a.containsKey("classes")) {
            inst.addTransformer(new RLTimeTransformer(a.get("classes").split(",")));
            log("time scaling x" + RLClock.SCALE + " for " + a.get("classes"));
        }
        if (a.containsKey("channel")) RLServerChannel.start(Integer.parseInt(a.get("channel")));
        if (a.containsKey("aim")) {   // rendered client: aim override for the bot (see RLMouse)
            inst.addTransformer(new RLMouseTransformer("zombie/input/AimingReticle"));
            Thread ta = new Thread(RLAgent::installAimFunctions, "rl-agent-aim");
            ta.setDaemon(true);
            ta.start();
        }
        if (a.containsKey("autostart")) startAutoClick();
        if (a.containsKey("client")) { // fake-client JVM: optional control socket, no server Lua hooks
            if (a.containsKey("control")) RLClientControl.start(Integer.parseInt(a.get("control")));
            return;
        }
        Thread t = new Thread(RLAgent::installWhenReady, "rl-agent-install");
        t.setDaemon(true);
        t.start();
    }

    /** Rendered client: the loading screen waits for a click ("Click to Start"); press it as soon as the game offers it. */
    private static void startAutoClick() {
        Thread t = new Thread(() -> {
            try {
                Class<?> c = null;
                while (c == null) { Thread.sleep(500); try { c = Class.forName("zombie.gameStates.GameLoadingState"); } catch (Throwable ignored) { } }
                java.lang.reflect.Field shown = findField(c, "showedClickToSkip"); shown.setAccessible(true);
                java.lang.reflect.Field force = findField(c, "forceDone"); force.setAccessible(true);
                Class<?> gw = Class.forName("zombie.GameWindow");
                while (true) {
                    Thread.sleep(500);
                    Object sm = gw.getField("states").get(null);
                    Object cur = sm == null ? null : findField(sm.getClass(), "current").get(sm);
                    if (cur != null && c.isInstance(cur) && shown.getBoolean(null)) {
                        Thread.sleep(1500); force.setBoolean(cur, true); log("clicked through loading screen");
                        Thread.sleep(5000);
                    }
                }
            } catch (Throwable e) { log("autostart stopped: " + e); }
        }, "rl-autostart");
        t.setDaemon(true);
        t.start();
    }

    /** Evaluate "pkg.Class.staticField.method(1,2).field" style paths by reflection. */
    static Object eval(String expr) throws Exception {
        String[] parts = splitDots(expr).toArray(new String[0]);
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
                java.util.List<String> as = splitTop(argStr);
                Object[] args = new Object[as.size()];
                for (int i = 0; i < args.length; i++) {
                    String a = as.get(i).trim();
                    args[i] = a.startsWith("@") ? eval(a.substring(1)) : Integer.valueOf(a);   // "@expr" = nested expression
                }
                Method m = null;
                for (Method c : curCls.getMethods()) {
                    if (c.getName().equals(mname) && fits(c, args)) { m = c; break; }
                }
                if (m == null) for (Method c : curCls.getDeclaredMethods()) {
                    if (c.getName().equals(mname) && fits(c, args)) { m = c; break; }
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


    /** Split on dots that are not inside parentheses. */
    static java.util.List<String> splitDots(String s) {
        java.util.List<String> out = new java.util.ArrayList<>();
        int depth = 0, start = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(') depth++;
            else if (c == ')') depth--;
            else if (c == '.' && depth == 0) { out.add(s.substring(start, i)); start = i + 1; }
        }
        out.add(s.substring(start));
        return out;
    }

    /** Split on commas that are not inside parentheses. */
    static java.util.List<String> splitTop(String s) {
        java.util.List<String> out = new java.util.ArrayList<>();
        if (s.isEmpty()) return out;
        int depth = 0, start = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(') depth++;
            else if (c == ')') depth--;
            else if (c == ',' && depth == 0) { out.add(s.substring(start, i)); start = i + 1; }
        }
        out.add(s.substring(start));
        return out;
    }

    static boolean fits(Method m, Object[] args) {
        Class<?>[] ps = m.getParameterTypes();
        if (ps.length != args.length) return false;
        for (int i = 0; i < ps.length; i++) {
            Class<?> p = ps[i];
            if (args[i] == null) { if (p.isPrimitive()) return false; continue; }
            Class<?> a = args[i].getClass();
            if (p.isPrimitive()) {
                if (p == boolean.class ? a != Boolean.class : !(Number.class.isAssignableFrom(a))) return false;
            } else if (!p.isAssignableFrom(a)) return false;
        }
        return true;
    }

    static java.lang.reflect.Field findField(Class<?> c, String n) throws NoSuchFieldException {
        for (Class<?> k = c; k != null; k = k.getSuperclass()) {
            try { return k.getDeclaredField(n); } catch (NoSuchFieldException ignored) { }
        }
        throw new NoSuchFieldException(n + " on " + c.getName());
    }

    /** Registers the Lua globals rlAim(x, y) and rlAimClear() on the client's Lua environment, again whenever the game replaces that
     *  environment (it rebuilds Lua after connecting to a server, which discards earlier globals). */
    private static void installAimFunctions() {
        try {
            Class<?> jf = Class.forName("se.krka.kahlua.vm.JavaFunction");
            Method frameGet = Class.forName("se.krka.kahlua.vm.LuaCallFrame").getMethod("get", int.class);
            Method rawset = Class.forName("se.krka.kahlua.vm.KahluaTable").getMethod("rawset", Object.class, Object.class);
            InvocationHandler set = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                RLMouse.ox = ((Number) frameGet.invoke(a[0], 0)).intValue();
                RLMouse.oy = ((Number) frameGet.invoke(a[0], 1)).intValue();
                return 0;
            };
            InvocationHandler clear = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                RLMouse.ox = RLMouse.NONE; RLMouse.oy = RLMouse.NONE;
                return 0;
            };
            Object fSet = Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, set);
            Object fClear = Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, clear);
            Object last = null;
            while (true) {
                Thread.sleep(250);
                Object env = null;
                try { env = Class.forName("zombie.Lua.LuaManager").getField("env").get(null); } catch (Throwable ignored) { }
                if (env == null || env == last) continue;
                rawset.invoke(env, "rlAim", fSet);
                rawset.invoke(env, "rlAimClear", fClear);
                last = env;
                log("aim: installed rlAim / rlAimClear");
            }
        } catch (Throwable e) { log("aim install failed: " + e); }
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
            InvocationHandler h3 = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                Object cf = a[0];
                String r;
                try {
                    Object pl = frameGet.invoke(cf, 0);
                    Class<?> gs = Class.forName("zombie.network.GameServer");
                    java.util.List<Object> players = (java.util.List<Object>) gs.getField("Players").get(null);
                    if (!players.contains(pl)) players.add(pl);
                    r = "players=" + players.size();
                } catch (Throwable e) { Throwable c = e; while (c.getCause() != null) c = c.getCause(); r = "ERR " + c; }
                framePush.invoke(cf, r);
                return 1;
            };
            rawset.invoke(env, "rlAddPlayer", Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, h3));
            rawset.invoke(env, "rlGet", Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, h2));
            InvocationHandler hPub = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                Object v = frameGet.invoke(a[0], 0);
                if (v != null) RLServerChannel.publish(v.toString());
                return 0;
            };
            InvocationHandler hPoll = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                String line = RLServerChannel.poll();
                if (line == null) return 0;
                framePush.invoke(a[0], line);
                return 1;
            };
            InvocationHandler hPromote = (proxy, m, a) -> {
                if (!m.getName().equals("call")) return null;
                String r;
                try {
                    String user = String.valueOf(frameGet.invoke(a[0], 0));
                    Object admin = Class.forName("zombie.characters.Roles").getMethod("getDefaultForAdmin").invoke(null);
                    Class<?> gs = Class.forName("zombie.network.GameServer");
                    Object engine = gs.getField("udpEngine").get(null);
                    java.util.List<?> conns = (java.util.List<?>) engine.getClass().getField("connections").get(engine);
                    int n = 0;
                    for (Object c : new java.util.ArrayList<>(conns)) {
                        if (!user.equals(String.valueOf(c.getClass().getMethod("getUserName").invoke(c)))) continue;
                        Class<?> roleClass = admin.getClass();
                        c.getClass().getMethod("setRole", roleClass).invoke(c, admin);
                        Object[] players = (Object[]) c.getClass().getField("players").get(c);
                        for (Object pl : players) if (pl != null) pl.getClass().getMethod("setRole", roleClass).invoke(pl, admin);
                        n++;
                    }
                    r = n > 0 ? "promoted " + n : "no such connection";
                } catch (Throwable e) { Throwable c = e; while (c.getCause() != null) c = c.getCause(); r = "ERR " + c; }
                framePush.invoke(a[0], r);
                return 1;
            };
            rawset.invoke(env, "rlPromote", Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, hPromote));
            if ("true".equals(System.getProperty("rl.dev"))) rawset.invoke(env, "rlDev", Boolean.TRUE);
            rawset.invoke(env, "rlPublish", Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, hPub));
            rawset.invoke(env, "rlPoll", Proxy.newProxyInstance(jf.getClassLoader(), new Class<?>[] { jf }, hPoll));

            log("installed rlLoadArea");
        } catch (Throwable e) {
            log("install failed: " + e);
        }
    }
}
