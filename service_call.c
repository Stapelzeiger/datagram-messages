#include "service_call.h"
#include <cmp_mem_access/cmp_mem_access.h>

void service_call_msg_cb(cmp_ctx_t *cmp, void *arg)
{
    cmp_mem_access_t *mem = (cmp_mem_access_t*)cmp->buf;
    struct service_call_handler_s *s = (struct service_call_handler_s*)arg;
    cmp_ctx_t res_cmp;
    cmp_mem_access_t res_mem;
    cmp_mem_access_init(&res_cmp, &res_mem, s->response_buffer, s->response_buffer_sz);

    uint32_t arg_list_size;
    if (!cmp_read_array(cmp, &arg_list_size)) {
        return;
    }
    if (arg_list_size != 3) {
        return;
    }
    uint32_t id_size;
    if (!cmp_read_str_size(cmp, &id_size)) {
        return;
    }
    size_t str_pos = cmp_mem_access_get_pos(mem);
    cmp_mem_access_set_pos(mem, str_pos + id_size);
    // get name without copy
    const char *str = cmp_mem_access_get_ptr_at_pos(mem, str_pos);
    uint32_t seq_nbr;
    if (!cmp_read_uint(cmp, &seq_nbr)) {
        return;
    }
    const struct service_entry_s *serv = s->service_table;
    while (serv->id != NULL) {
        if (strncmp(serv->id, str, id_size) == 0
            && serv->id[id_size] == '\0') {
            cmp_write_array(&res_cmp, 2); // message list: ['res', [...]]
            cmp_write_str(&res_cmp, "res", strlen("res"));
            cmp_write_array(&res_cmp, 3); // service response [NAME, SEQ, ARG]
            cmp_write_str(&res_cmp, str, id_size); // service name
            cmp_write_uint(&res_cmp, seq_nbr);
            if (serv->cb(cmp, &res_cmp, serv->arg)) {
                s->send_cb(s->response_buffer,
                           cmp_mem_access_get_pos(&res_mem),
                           s->send_cb_arg);
            }
            break;
        }
        serv++;
    }
}
