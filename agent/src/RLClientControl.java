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
 *   weapon ID       wield the inventory item with this id (see RLBridge give)
 *   info            reply "info x y z weaponId"
 * Replies are one line: "ok", "info ...", or "err ...". Everything goes through reflection on the game's private classes.
 */
public final class RLClientControl {
    private static Object player, movement, client, destination;
    private static Field fx, fy, fz, fWeapon, fSpeed;
    private static Method vSet, sendCommand, sendTeleport, sendEquip;

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
