/** Scaled clock used by rewritten call sites. rl.timescale=K makes game code see K seconds per real second. */
public final class RLClock {
    public static final double SCALE = Double.parseDouble(System.getProperty("rl.timescale", "1"));
    private static final long BASE_NANOS = System.nanoTime();
    private static final long BASE_MILLIS = System.currentTimeMillis();

    public static long nanoTime() { return BASE_NANOS + (long) ((System.nanoTime() - BASE_NANOS) * SCALE); }
    public static long currentTimeMillis() { return BASE_MILLIS + (long) ((System.currentTimeMillis() - BASE_MILLIS) * SCALE); }

    public static void sleep(long millis) throws InterruptedException {
        if (millis <= 0) { Thread.sleep(millis); return; }
        double real = millis / SCALE;
        long ms = (long) real;
        Thread.sleep(ms, (int) ((real - ms) * 1_000_000));
    }
}
