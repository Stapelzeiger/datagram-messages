#ifndef MSG_DISPATCHER_H
#define MSG_DISPATCHER_H

#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include "cmp/cmp.h"

#ifdef __cplusplus
extern "C" {
#endif

struct msg_dispatcher_entry_s {
    const char *id;
    void (*cb)(cmp_ctx_t *cmp, void *arg);
    void *arg;
};

void msg_dispatcher(const void *dtgrm,
                    size_t dtgrm_len,
                    const struct msg_dispatcher_entry_s *dispatch_table);

#ifdef __cplusplus
}
#endif

#endif /* MSG_DISPATCHER_H */