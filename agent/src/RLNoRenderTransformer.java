import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;

/**
 * Headless-client spike: stops the game states from drawing. GameStateMachine.render() starts with
 * aload_0; getfield current; ifnull END; aload_0; getfield current; invokevirtual GameState.render; END: return.
 * Flipping ifnull (0xC6) to ifnonnull (0xC7) makes the branch to END taken whenever a state exists, so no state draws.
 * ifnull and ifnonnull both pop one reference, so the stack map frame at END stays valid. Everything else in the frame loop
 * (logic, lighting thread, queued Lua events, frame ready) still runs.
 */
public final class RLNoRenderTransformer implements ClassFileTransformer {
    private final boolean worldOnly;
    public RLNoRenderTransformer(boolean worldOnly) { this.worldOnly = worldOnly; }

    @Override
    public byte[] transform(ClassLoader loader, String name, Class<?> redefined, ProtectionDomain pd, byte[] b) {
        if (worldOnly && "zombie/gameStates/IngameState".equals(name)) return patchWorld(b);
        if (worldOnly || !"zombie/gameStates/GameStateMachine".equals(name)) return null;
        // pattern: 2A B4 xx xx C6 00 0A 2A B4 xx xx B6 xx xx B1
        for (int i = 0; i + 15 <= b.length; i++) {
            if ((b[i] & 0xff) == 0x2A && (b[i + 1] & 0xff) == 0xB4 && (b[i + 4] & 0xff) == 0xC6 && b[i + 5] == 0 && b[i + 6] == 10
                    && (b[i + 7] & 0xff) == 0x2A && (b[i + 8] & 0xff) == 0xB4 && (b[i + 11] & 0xff) == 0xB6 && (b[i + 14] & 0xff) == 0xB1) {
                byte[] out = b.clone();
                out[i + 4] = (byte) 0xC7;
                System.out.println("RLAGENT norender: GameStateMachine.render disabled");
                return out;
            }
        }
        System.out.println("RLAGENT norender: pattern not found in GameStateMachine");
        return null;
    }

    /** IngameState.render(): aload_0; invokevirtual renderInternal; aload_1; ifnull END; ... Replace the call (3 bytes) with pop; nop; nop:
     *  the receiver is popped, nothing is drawn, the profiler probe is still closed. Menus and loading screens keep working because only
     *  the in-world state is touched (their transitions run inside their render methods). */
    private static byte[] patchWorld(byte[] b) {
        for (int i = 0; i + 10 <= b.length; i++) {
            if ((b[i] & 0xff) == 0x2A && (b[i + 1] & 0xff) == 0xB6 && (b[i + 4] & 0xff) == 0x2B && (b[i + 5] & 0xff) == 0xC6
                    && b[i + 6] == 0 && b[i + 7] == 30 && (b[i + 8] & 0xff) == 0x2B && (b[i + 9] & 0xff) == 0xB6) {
                byte[] out = b.clone();
                out[i + 1] = 0x57; out[i + 2] = 0; out[i + 3] = 0;
                System.out.println("RLAGENT norender: IngameState.render world drawing disabled");
                return out;
            }
        }
        System.out.println("RLAGENT norender: pattern not found in IngameState");
        return null;
    }
}
