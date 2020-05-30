cmake_minimum_required(VERSION 3.12)
project(simple_tracer LANGUAGES CXX C)

set(ASSIGNMENT_ROOT "${PROJECT_SOURCE_DIR}")

include(FetchContent)
FetchContent_Declare(
    atlas
    GIT_REPOSITORY https://github.com/marovira/atlas.git)
FetchContent_Populate(atlas)
add_subdirectory(${atlas_SOURCE_DIR} ${atlas_BINARY_DIR})

FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.7.3)

FetchContent_GetProperties(json)
if(NOT json_POPULATED)
    FetchContent_Populate(json)
    add_subdirectory(${json_SOURCE_DIR} ${json_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

set(ASSIGNMENT_INCLUDE
    "${ASSIGNMENT_ROOT}/assignment.hpp"
    )
set(ASSIGNMENT_SOURCE 
    "${ASSIGNMENT_ROOT}/main.cpp"
        main.cpp)

include_directories(${ASSIGNMENT_ROOT}/include)

set(PATH_INCLUDE "${ASSIGNMENT_ROOT}/include/paths.hpp")
configure_file("${ASSIGNMENT_ROOT}/paths.hpp.in" ${PATH_INCLUDE})
list(APPEND ASSIGNMENT_INCLUDE ${PATH_INCLUDE})

source_group("include" FILES ${ASSIGNMENT_INCLUDE})
source_group("source" FILES ${ASSIGNMENT_SOURCE})

add_executable(app ${ASSIGNMENT_SOURCE} ${ASSIGNMENT_SHADER})
target_link_libraries(app PUBLIC atlas::atlas nlohmann_json::nlohmann_json)
