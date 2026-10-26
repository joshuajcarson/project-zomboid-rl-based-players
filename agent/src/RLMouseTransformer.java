import java.lang.instrument.ClassFileTransformer;
import java.nio.charset.StandardCharsets;
import java.security.ProtectionDomain;
import java.util.Arrays;

/**
 * Redirects zombie.input.Mouse.getXA()/getYA() call sites in selected classes (the aiming code) to RLMouse by re-pointing the
 * constant-pool Methodref at a new class entry, exactly like RLTimeTransformer does for the clock.
 */
public final class RLMouseTransformer implements ClassFileTransformer {
    private final String[] prefixes;
    public RLMouseTransformer(String... prefixes) { this.prefixes = prefixes; }

    @Override
    public byte[] transform(ClassLoader loader, String name, Class<?> redefined, ProtectionDomain pd, byte[] b) {
        if (name == null) return null;
        boolean match = false;
        for (String p : prefixes) if (name.startsWith(p)) { match = true; break; }
        if (!match) return null;
        try { return patch(name, b); } catch (Throwable t) { System.out.println("RLAGENT aim patch failed for " + name + ": " + t); return null; }
    }

    private static int u2(byte[] b, int o) { return ((b[o] & 0xff) << 8) | (b[o + 1] & 0xff); }

    static byte[] patch(String className, byte[] b) {
        int count = u2(b, 8);
        int[] off = new int[count];
        int[] tag = new int[count];
        int o = 10;
        for (int i = 1; i < count; i++) {
            off[i] = o; tag[i] = b[o] & 0xff;
            switch (tag[i]) {
                case 1: o += 3 + u2(b, o + 1); break;
                case 3: case 4: case 9: case 10: case 11: case 12: case 17: case 18: o += 5; break;
                case 5: case 6: o += 9; i++; break;
                case 7: case 8: case 16: case 19: case 20: o += 3; break;
                case 15: o += 4; break;
                default: throw new IllegalStateException("cp tag " + tag[i]);
            }
        }
        int cpEnd = o;
        byte[] out = null;
        int patched = 0;
        int newClassIdx = -1;
        for (int i = 1; i < count; i++) {
            if (tag[i] != 10) continue;
            String cls = className(b, off, tag, u2(b, off[i] + 1));
            int nat = u2(b, off[i] + 3);
            String mname = utf(b, off, u2(b, off[nat] + 1));
            String desc = utf(b, off, u2(b, off[nat] + 3));
            boolean hit = cls.equals("zombie/input/Mouse") && desc.equals("()I") && (mname.equals("getXA") || mname.equals("getYA"));
            if (!hit) continue;
            if (out == null) {
                // append Utf8 "RLMouse" and Class entry at the end of the constant pool
                byte[] name = "RLMouse".getBytes(StandardCharsets.UTF_8);
                int extra = 3 + name.length + 3;
                out = new byte[b.length + extra];
                System.arraycopy(b, 0, out, 0, cpEnd);
                int p = cpEnd;
                out[p++] = 1; out[p++] = 0; out[p++] = (byte) name.length;
                for (byte x : name) out[p++] = x;
                out[p++] = 7; out[p++] = (byte) (count >> 8); out[p++] = (byte) count;   // Class -> Utf8 at index count
                System.arraycopy(b, cpEnd, out, p, b.length - cpEnd);
                newClassIdx = count + 1;
                out[8] = (byte) ((count + 2) >> 8); out[9] = (byte) (count + 2);
            }
            out[off[i] + 1] = (byte) (newClassIdx >> 8); out[off[i] + 2] = (byte) newClassIdx;
            patched++;
        }
        if (patched > 0) System.out.println("RLAGENT aim-patched " + className + " (" + patched + " call sites)");
        return out;
    }

    private static String utf(byte[] b, int[] off, int idx) { int o = off[idx]; return new String(b, o + 3, u2(b, o + 1), StandardCharsets.UTF_8); }
    private static String className(byte[] b, int[] off, int[] tag, int classIdx) { return utf(b, off, u2(b, off[classIdx] + 1)); }
}
