cmake_minimum_required(VERSION 3.27.4)

project(trader VERSION 0.4.0)

# TODO: Specify C++ Standard
# This is not currently set until I can verify what standard TWSAPI can accept.
#set(CMAKE_CXX_STANDARD 20)
#set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(${PROJECT_SOURCE_DIR}/include)

add_subdirectory(${PROJECT_SOURCE_DIR}/include/twsapi)
add_subdirectory(src)
