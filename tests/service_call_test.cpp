#include "CppUTest/TestHarness.h"
#include "CppUTestExt/MockSupport.h"
#include "CppUTest/CommandLineTestRunner.h"

#include "cmp/cmp.h"
#include "cmp_mem_access/cmp_mem_access.h"
#include "../msg_dispatcher.h"
#include "../service_call.h"

extern "C" void send_cb(const void *dtgrm, size_t length, void *arg)
{
    cmp_mem_access_t mem;
    cmp_ctx_t cmp;
    cmp_mem_access_ro_init(&cmp, &mem, dtgrm, length);

    bool ret;
    uint32_t seq;
    int data;
    uint32_t len;
    static char name[100];

    ret = cmp_read_array(&cmp, &len);
    CHECK_TRUE(ret);
    CHECK_EQUAL(len, 2);

    len = sizeof(name);
    ret = cmp_read_str(&cmp, &name[0], &len);
    CHECK_TRUE(ret);
    CHECK_EQUAL(strncmp("res", name, 3), 0);

    ret = cmp_read_array(&cmp, &len);
    CHECK_TRUE(ret);
    CHECK_EQUAL(len, 3);
    len = sizeof(name);
    ret = cmp_read_str(&cmp, &name[0], &len);
    CHECK_TRUE(ret);
    ret = cmp_read_uint(&cmp, &seq);
    CHECK_TRUE(ret);
    ret = cmp_read_int(&cmp, &data);
    CHECK_TRUE(ret);
    mock().actualCall("send_cb").withParameter("arg", arg).withParameter("name", name)
        .withParameter("seq", seq).withParameter("data", data);
}

// successful call
extern "C" bool echo_cb(cmp_ctx_t *cmp_in, cmp_ctx_t *cmp_out, void *arg)
{
    int32_t i;
    bool ret = cmp_read_s32(cmp_in, &i);
    CHECK_TRUE(ret);
    mock().actualCall("echo_cb").withParameter("arg", arg).withParameter("int", i);
    cmp_write_s32(cmp_out, i);
    return true;
}

// failing call
extern "C" bool fail_cb(cmp_ctx_t *cmp_in, cmp_ctx_t *cmp_out, void *arg)
{
    int32_t i;
    bool ret = cmp_read_s32(cmp_in, &i);
    CHECK_TRUE(ret);
    mock().actualCall("fail_cb").withParameter("arg", arg).withParameter("int", i);
    cmp_write_sint(cmp_out, i);
    return false;
}

int send_cb_arg;
int echo_cb_arg;
int fail_cb_arg;

struct service_entry_s service_calls[] = {
    {.id="echo_cb", .cb=echo_cb, .arg=&echo_cb_arg},
    {.id="fail_cb", .cb=fail_cb, .arg=&fail_cb_arg},
    {NULL, NULL, NULL}
};

struct service_call_handler_s service_call_handler;

TEST_GROUP(ServiceCallHandler)
{
    char arg_buffer[100];
    char response_buffer[100];
    cmp_mem_access_t mem;
    cmp_ctx_t cmp;

    void setup(void)
    {
        service_call_handler.service_table = &service_calls[0];
        service_call_handler.response_buffer = &response_buffer[0];
        service_call_handler.response_buffer_sz = sizeof(response_buffer);
        service_call_handler.send_cb = send_cb;
        service_call_handler.send_cb_arg = &send_cb_arg;
        memset(&response_buffer[0], 0, sizeof(response_buffer));

        cmp_mem_access_init(&cmp, &mem, arg_buffer, sizeof(arg_buffer));
        cmp_write_array(&cmp, 3);
    }

    void teardown()
    {
        mock().clear();
    }
};

TEST(ServiceCallHandler, Nonexistant)
{
    cmp_write_str(&cmp, "foo", strlen("foo"));
    cmp_write_uint(&cmp, 0); // sequence number
    cmp_write_s32(&cmp, 0xdead);

    // reset to start
    cmp_mem_access_init(&cmp, &mem, arg_buffer, sizeof(arg_buffer));
    service_call_msg_cb(&cmp, &service_call_handler);
    mock().checkExpectations();
};

TEST(ServiceCallHandler, ServiceCallNoResponse)
{
    cmp_write_str(&cmp, "fail_cb", strlen("fail_cb"));
    cmp_write_uint(&cmp, 0); // sequence number
    cmp_write_s32(&cmp, 1234);
    mock().expectOneCall("fail_cb").withParameter("arg", &fail_cb_arg).withParameter("int", 1234);

    // reset to start
    cmp_mem_access_init(&cmp, &mem, arg_buffer, sizeof(arg_buffer));
    service_call_msg_cb(&cmp, &service_call_handler);
    mock().checkExpectations();
};

TEST(ServiceCallHandler, ServiceCallWithResponse)
{
    cmp_write_str(&cmp, "echo_cb", strlen("echo_cb"));
    cmp_write_uint(&cmp, 0); // sequence number
    cmp_write_s32(&cmp, 42);
    mock().expectOneCall("echo_cb").withParameter("arg", &echo_cb_arg).withParameter("int", 42);
    mock().expectOneCall("send_cb").withParameter("arg", &send_cb_arg)
        .withParameter("name", "echo_cb").withParameter("seq", 0).withParameter("data", 42);

    // reset to start
    cmp_mem_access_init(&cmp, &mem, arg_buffer, sizeof(arg_buffer));
    service_call_msg_cb(&cmp, &service_call_handler);
    mock().checkExpectations();
};
