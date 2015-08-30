#ifndef SERVICE_CALL_H
#define SERVICE_CALL_H

#ifdef __cplusplus
extern "C" {
#endif

#include <string.h>
#include <stdint.h>
#include "cmp/cmp.h"

struct service_entry_s {
    const char *id;
    bool (*cb)(cmp_ctx_t *cmp_in, cmp_ctx_t *cmp_out, void *arg);
    void *arg;
};

struct service_call_handler_s {
    const struct service_entry_s *service_table;
    void *response_buffer;
    size_t response_buffer_sz;
    void (*send_cb)(const void *dtgrm, size_t len, void *arg);
    void *send_cb_arg;
};

void service_call_msg_cb(cmp_ctx_t *cmp, void *arg);

/*
a message dispatcher entry must be constructed like this:
struct msg_dispatcher_entry_s msg = {
    ... some entries...,
    {.id="req", .cb=service_call_msg_cb, .arg=&service_call_handler},
    {NULL, NULL, NULL}
}
*/

#ifdef __cplusplus
}
#endif

#endif /* SERVICE_CALL_H */
