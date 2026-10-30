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
    @Override
    public byte[] transform(ClassLoader loader, String name, Class<?> redefined, ProtectionDomain pd, byte[] b) {
        if (!"zombie/gameStates/GameStateMachine".equals(name)) return null;
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
}
