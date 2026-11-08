#ifndef RX3_FX_STATE_H
#define RX3_FX_STATE_H
#include <stdint.h>
/* RX3 1.19: IUiObjManager::getMixer -> Mixer::getMasterInnards.
 * MasterInnards::onEv_BeatEffectEnable stores the user On/Off state at +0x44.
 * The engine enable flag can stay set when the selected engine effect is OFF.
 */
static inline uint32_t rx3_fx_enabled(void *root) {
    void *mixer = root ? *(void **)((char *)root + 0x50) : 0;
    void *master = mixer ? *(void **)((char *)mixer + 0xa8) : 0;
    return master && *(volatile unsigned char *)((char *)master + 0x44) == 1;
}
#endif
