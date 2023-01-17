add_subdirectory(version)
add_subdirectory(clients)

add_executable(trader trader.cpp)

target_link_libraries(${PROJECT_NAME} PUBLIC clients)


target_include_directories(${PROJECT_NAME} PUBLIC
                                           "${PROJECT_BINARY_DIR}"
                                           "${PROJECT_BINARY_DIR}/src"
                                           )
