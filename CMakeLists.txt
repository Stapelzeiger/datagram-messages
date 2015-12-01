cmake_minimum_required(VERSION 2.6)

project(datagram-messages)
set(CMAKE_BUILD_TYPE Debug)

include_directories(.)

add_executable(
    tests
    ./cmp/cmp.c
    ./cmp_mem_access/cmp_mem_access.c
    ./msg_dispatcher.c
    ./tests/msg_dispatcher_test.cpp
    )

target_link_libraries(
    tests
    CppUTest
    CppUTestExt
    )
