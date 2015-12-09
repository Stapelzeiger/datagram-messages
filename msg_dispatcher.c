#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include "cmp/cmp.h"
#include "cmp_mem_access/cmp_mem_access.h"
#include "msg_dispatcher.h"

void msg_dispatcher(const void *dtgrm,
                    size_t dtgrm_len,
                    const struct msg_dispatcher_entry_s *dispatch_table)
{
    cmp_ctx_t cmp;
    cmp_mem_access_t mem;
    cmp_mem_access_ro_init(&cmp, &mem, dtgrm, dtgrm_len);
    uint32_t list_size;
    if (!cmp_read_array(&cmp, &list_size)) {
        return;
    }
    if (list_size != 2) {
        return;
    }
    uint32_t id_size;
    if (!cmp_read_str_size(&cmp, &id_size)) {
        return;
    }
    size_t str_pos = cmp_mem_access_get_pos(&mem);
    cmp_mem_access_set_pos(&mem, str_pos + id_size);
    const char *str = cmp_mem_access_get_ptr_at_pos(&mem, str_pos);
    while (dispatch_table->id != NULL) {
        if (strncmp(dispatch_table->id, str, id_size) == 0
            && dispatch_table->id[id_size] == '\0') {
            dispatch_table->cb(&cmp, dispatch_table->arg);
            break;
        }
        dispatch_table++;
    }
}
