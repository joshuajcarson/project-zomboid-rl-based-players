import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Line-based TCP channel between server Lua and an external process (Python), localhost only.
 * Lua calls rlPublish(line) to broadcast a line to every connected peer and rlPoll() to take the next received line.
 * Peers are never trusted: lines are only ever handed to Lua as plain strings.
 */
public final class RLServerChannel {
    private static final int MAX_QUEUE = 2000;
    private static final CopyOnWriteArrayList<Peer> peers = new CopyOnWriteArrayList<>();
    private static final ConcurrentLinkedQueue<String> inbound = new ConcurrentLinkedQueue<>();

    private static final class Peer {
        final Socket socket;
        final ConcurrentLinkedQueue<String> out = new ConcurrentLinkedQueue<>();
        Peer(Socket s) { socket = s; }
    }

    public static void start(int port) {
        Thread t = new Thread(() -> {
            try (ServerSocket ss = new ServerSocket(port, 8, InetAddress.getLoopbackAddress())) {
                System.out.println("RLAGENT server channel listening on 127.0.0.1:" + port);
                while (true) {
                    Socket s = ss.accept();
                    s.setTcpNoDelay(true);
                    Peer p = new Peer(s);
                    peers.add(p);
                    new Thread(() -> reader(p), "rl-chan-read").start();
                    new Thread(() -> writer(p), "rl-chan-write").start();
                }
            } catch (IOException e) {
                System.out.println("RLAGENT server channel failed: " + e);
            }
        }, "rl-chan-accept");
        t.setDaemon(true);
        t.start();
    }

    private static void reader(Peer p) {
        try (BufferedReader r = new BufferedReader(new InputStreamReader(p.socket.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = r.readLine()) != null) {
                if (inbound.size() < MAX_QUEUE && line.length() < 4096) inbound.add(line);
            }
        } catch (IOException ignored) { }
        close(p);
    }

    private static void writer(Peer p) {
        try (PrintWriter w = new PrintWriter(p.socket.getOutputStream(), false, StandardCharsets.UTF_8)) {
            while (!p.socket.isClosed()) {
                String line = p.out.poll();
                if (line == null) { Thread.sleep(1); continue; }
                w.print(line);
                w.print('\n');
                if (p.out.isEmpty()) w.flush();
                if (w.checkError()) break;
            }
        } catch (Exception ignored) { }
        close(p);
    }

    private static void close(Peer p) {
        peers.remove(p);
        try { p.socket.close(); } catch (IOException ignored) { }
    }

    /** Called from the game thread via Lua. */
    public static void publish(String line) {
        for (Peer p : peers) {
            if (p.out.size() > MAX_QUEUE) p.out.poll();
            p.out.add(line);
        }
    }

    /** Called from the game thread via Lua; null when nothing is waiting. */
    public static String poll() { return inbound.poll(); }

    public static int peerCount() { return peers.size(); }
}
