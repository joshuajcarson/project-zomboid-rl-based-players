/**
 * Aim point override for a rendered client. The game takes a keyboard-and-mouse player's aim from the real OS cursor
 * (AimingReticle -> Mouse.getXA/getYA); Lua cannot move that cursor (Mouse.setXY is overwritten on the next input poll). RLMouseTransformer
 * re-points those two calls inside AimingReticle at this class, which returns the position set through the Lua functions rlAim(x, y) and
 * rlAimClear(), or the real cursor when none is set. Coordinates are the screen space of ISCoordConversion.ToScreen divided by the zoom.
 */
public final class RLMouse {
    public static final int NONE = Integer.MIN_VALUE;
    public static volatile int ox = NONE, oy = NONE;
    private static java.lang.reflect.Method rx, ry;

    private static int real(boolean xAxis) {
        try {
            if (rx == null) {
                Class<?> m = Class.forName("zombie.input.Mouse");
                rx = m.getMethod("getXA"); ry = m.getMethod("getYA");
            }
            return (Integer) (xAxis ? rx : ry).invoke(null);
        } catch (Throwable t) { return 0; }
    }

    public static int getXA() { int v = ox; return v != NONE ? v : real(true); }
    public static int getYA() { int v = oy; return v != NONE ? v : real(false); }
}
