add_subdirectory(version)
add_subdirectory(brokerclient)

add_executable(trader trader.cpp)

target_link_libraries(${PROJECT_NAME} PUBLIC brokerclient)


target_include_directories(${PROJECT_NAME} PUBLIC
                                           "${PROJECT_BINARY_DIR}"
                                           "${PROJECT_BINARY_DIR}/src"
                                           )
