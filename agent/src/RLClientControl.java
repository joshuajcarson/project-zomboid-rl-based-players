import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Collection;

/**
 * Control channel inside a FakeClientManager JVM (localhost only). One text command per line:
 *   goto X Y        walk toward (X,Y) (needs the scenario movement type "Line")
 *   speed V         set the movement speed value (same units as the scenario "run" speed)
 *   say TEXT        send a chat/admin command as this player, e.g.  say /additem "Client5" Base.BaseballBat
 *   tp X Y Z        move the player instantly and tell the server
 *   autoattack on|off  built-in melee (2 tile reach); off hands melee over to the explicit attack command
 *   attack          hit the nearest owned zombie within 2 tiles (replies 'hit <dist>' or 'miss')
 *   weapon ID       wield the inventory item with this id (see RLBridge give)
 *   info            reply "info x y z weaponId"
 * Replies are one line: "ok", "info ...", or "err ...". Everything goes through reflection on the game's private classes.
 */
public final class RLClientControl {
    private static Object player, movement, client, destination;
    private static Field fx, fy, fz, fWeapon, fSpeed;
    private static Method vSet, sendCommand, sendTeleport, sendEquip, sendHitZombie, setUpdatePeriod;
    private static Object simulator, attackLimiter;
    private static java.util.Map<?, ?> zombieMap;
    private static java.util.Collection<Object> zombieDelete;
    private static Field fDamage, zx, zy, zhealth;
    private static long attackPeriod = 1000;
    private static Object lockedTarget;   // a swing keeps hitting the same zombie while it is alive and within reach (a real player faces one zombie at a time)

    public static void start(int port) {
        Thread t = new Thread(() -> serve(port), "rl-client-control");
        t.setDaemon(true);
        t.start();
    }

    private static Field field(Class<?> c, String n) throws Exception { Field f = c.getDeclaredField(n); f.setAccessible(true); return f; }
    private static Method method(Class<?> c, String n, Class<?>... a) throws Exception { Method m = c.getDeclaredMethod(n, a); m.setAccessible(true); return m; }

    @SuppressWarnings("unchecked")
    private static boolean bind() {
        try {
            Class<?> fm = Class.forName("zombie.network.FakeClientManager");
            Collection<Object> players = (Collection<Object>) field(fm, "players").get(null);
            if (players.isEmpty()) return false;
            player = players.iterator().next();
            Class<?> pc = player.getClass();
            fx = field(pc, "x"); fy = field(pc, "y"); fz = field(pc, "z"); fWeapon = field(pc, "weaponId");
            movement = field(pc, "movement").get(player);
            client = field(pc, "client").get(player);
            Class<?> mc = movement.getClass();
            destination = field(mc, "destination").get(movement);
            fSpeed = field(mc, "speed");
            vSet = method(destination.getClass(), "set", float.class, float.class);
            sendCommand = method(client.getClass(), "sendCommand", String.class);
            sendTeleport = method(client.getClass(), "sendTeleport", float.class, float.class, float.class);
            sendEquip = method(client.getClass(), "sendEquip");
            simulator = field(pc, "simulator").get(player);
            Class<?> sc = simulator.getClass();
            attackLimiter = field(sc, "attackLimiter").get(simulator);
            setUpdatePeriod = method(attackLimiter.getClass(), "setUpdatePeriod", long.class);
            zombieMap = (java.util.Map<?, ?>) field(sc, "zombies").get(simulator);
            zombieDelete = (java.util.Collection<Object>) field(sc, "zombies4Delete").get(simulator);
            attackPeriod = field(sc, "attackPeriod").getInt(null);
            Class<?> zc = Class.forName("zombie.network.FakeClientManager$Zombie");
            zx = field(zc, "x"); zy = field(zc, "y"); zhealth = field(zc, "health");
            fDamage = field(pc, "damage");
            sendHitZombie = method(client.getClass(), "sendHitZombie", zc, float.class);
            return true;
        } catch (Throwable e) {
            return false;
        }
    }

    private static void serve(int port) {
        try (ServerSocket ss = new ServerSocket(port, 4, InetAddress.getLoopbackAddress())) {
            System.out.println("RLAGENT client control listening on 127.0.0.1:" + port);
            while (true) {
                try (Socket s = ss.accept();
                     BufferedReader r = new BufferedReader(new InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8));
                     PrintWriter w = new PrintWriter(s.getOutputStream(), true, StandardCharsets.UTF_8)) {
                    s.setTcpNoDelay(true);
                    String line;
                    while ((line = r.readLine()) != null) w.println(handle(line.trim()));
                } catch (IOException ignored) { }
            }
        } catch (IOException e) {
            System.out.println("RLAGENT client control failed: " + e);
        }
    }

    private static String handle(String line) {
        if (player == null && !bind()) return "err not-ready";
        try {
            String[] p = line.split("\\s+", 2);
            String arg = p.length > 1 ? p[1] : "";
            switch (p[0]) {
                case "goto": {
                    String[] a = arg.split("\\s+");
                    vSet.invoke(destination, Float.parseFloat(a[0]), Float.parseFloat(a[1]));
                    return "ok";
                }
                case "speed":
                    fSpeed.setFloat(movement, Float.parseFloat(arg));
                    return "ok";
                case "say":
                    sendCommand.invoke(client, arg);
                    return "ok";
                case "tp": {
                    String[] a = arg.split("\\s+");
                    float x = Float.parseFloat(a[0]), y = Float.parseFloat(a[1]), z = a.length > 2 ? Float.parseFloat(a[2]) : 0f;
                    fx.setFloat(player, x); fy.setFloat(player, y); fz.setFloat(player, z);
                    vSet.invoke(destination, x, y);
                    sendTeleport.invoke(client, x, y, z);
                    return "ok";
                }
                case "weapon": // weapon <itemId> : wield an item the server has put in this player's inventory
                    fWeapon.setInt(player, Integer.parseInt(arg));
                    sendEquip.invoke(client);
                    return "ok";
                case "autoattack": // autoattack on|off : the game's built-in melee (2 tile reach, fixed period)
                    setUpdatePeriod.invoke(attackLimiter, arg.equals("on") ? attackPeriod : Long.MAX_VALUE / 4);
                    return "ok";
                case "attack": { // attack [dmg]: hit the nearest owned zombie within 2 tiles with the given damage (default: the scenario's), 0 = a swing that does nothing
                    String[] aa = arg.trim().isEmpty() ? new String[0] : arg.trim().split("\s+");
                    float dmgArg = aa.length > 0 ? Float.parseFloat(aa[0]) : Float.NaN;
                    Object best = null; double bd = 2.0;
                    if (aa.length > 1) {   // attack <dmg> <zombie id>: hit exactly that zombie (the id the server reports); stale records of removed zombies sit on the player and must not absorb the hit
                        int wanted = Integer.parseInt(aa[1]);
                        for (java.util.Map.Entry<?, ?> en : new java.util.ArrayList<>(zombieMap.entrySet())) {
                            if (((Number) en.getKey()).intValue() == wanted) { best = en.getValue(); break; }
                        }
                        if (best == null) return "miss";
                        bd = Math.hypot(zx.getFloat(best) - fx.getFloat(player), zy.getFloat(best) - fy.getFloat(player));
                    }
                    float px = fx.getFloat(player), py = fy.getFloat(player);
                    if (best == null && lockedTarget != null && zombieMap.containsValue(lockedTarget)) {
                        double dl = Math.hypot(zx.getFloat(lockedTarget) - px, zy.getFloat(lockedTarget) - py);
                        if (dl < 2.0) { best = lockedTarget; bd = dl; }
                    }
                    if (best == null) for (Object z : new java.util.ArrayList<>(zombieMap.values())) {
                        double d = Math.hypot(zx.getFloat(z) - px, zy.getFloat(z) - py);
                        if (d < bd) { bd = d; best = z; }
                    }
                    lockedTarget = best;
                    if (best == null) return "miss";
                    float dmg = Float.isNaN(dmgArg) ? fDamage.getFloat(null) : dmgArg;
                    if (dmg <= 0f) return "swing " + String.format("%.2f", bd);
                    sendHitZombie.invoke(client, best, dmg);
                    float h = zhealth.getFloat(best) - dmg;
                    zhealth.setFloat(best, h);
                    if (h <= 0) zombieDelete.add(best);
                    return "hit " + String.format("%.2f", bd);
                }
                case "zombies": { // the zombie records this client holds: count, then the 6 nearest as x,y,health,distance
                    float px = fx.getFloat(player), py = fy.getFloat(player);
                    java.util.List<double[]> zs = new java.util.ArrayList<>();
                    for (Object z : new java.util.ArrayList<>(zombieMap.values()))
                        zs.add(new double[] { zx.getFloat(z), zy.getFloat(z), zhealth.getFloat(z), Math.hypot(zx.getFloat(z) - px, zy.getFloat(z) - py) });
                    zs.sort((a, b) -> Double.compare(a[3], b[3]));
                    StringBuilder sb = new StringBuilder("info n=" + zs.size());
                    for (int i = 0; i < Math.min(6, zs.size()); i++)
                        sb.append(String.format(" [%.1f,%.1f h=%.2f d=%.2f]", zs.get(i)[0], zs.get(i)[1], zs.get(i)[2], zs.get(i)[3]));
                    return sb.toString();
                }
                case "info":
                    return "info " + fx.getFloat(player) + " " + fy.getFloat(player) + " " + fz.getFloat(player) + " " + fWeapon.getInt(player);
                default:
                    return "err unknown-command";
            }
        } catch (Throwable e) {
            Throwable c = e;
            while (c.getCause() != null) c = c.getCause();
            return "err " + c;
        }
    }
}
