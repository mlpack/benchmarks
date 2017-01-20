cmake_minimum_required (VERSION 2.8)
project(misc)

# Include modules in the CMake directory.
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/CMake")

# Set the CFLAGS and CXXFLAGS.
add_definitions("-Wno-deprecated-declarations")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules/")
SET(CMAKE_CXX_FLAGS "-std=c++11 -O0 ${CMAKE_CXX_FLAGS}")

# If using clang, we have to link against libc++ depending on the
# OS (at least on some systems). Further, gcc sometimes optimizes calls to
# math.h functions, making -lm unnecessary with gcc, but it may still be
# necessary with clang.
if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  IF (APPLE)
    # detect OS X version. Use '/usr/bin/sw_vers -productVersion' to
    # extract V from '10.V.x'.)
    EXEC_PROGRAM(/usr/bin/sw_vers ARGS
        -productVersion OUTPUT_VARIABLE MACOSX_VERSION_RAW)
    string(REGEX REPLACE
        "10\\.([0-9]+).*" "\\1"
        MACOSX_VERSION
        "${MACOSX_VERSION_RAW}")

     # OSX Lion (10.7) and OS X Mountain Lion (10.8) doesn't automatically
     # select the right stdlib.
    if(${MACOSX_VERSION} LESS 9)
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
     endif(${MACOSX_VERSION} LESS 9)
  endif(APPLE)
endif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")

# Find the libraries we need to compile against.
set(Boost_ADDITIONAL_VERSIONS
  "1.49.0" "1.50.0" "1.51.0" "1.52.0" "1.53.0" "1.54.0" "1.55.0")
find_package(Boost 1.49 COMPONENTS system serialization REQUIRED)
find_package(Armadillo 3.6.0 REQUIRED)
find_package(Mlpack REQUIRED)

# Include directories for the dependencies.
include_directories(${MLPACK_INCLUDE_DIR})
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_BINARY_DIR})
include_directories(${CMAKE_SOURCE_DIR})

# Set source file path.
set(mlp_forward_source
    mlp_forward.cpp
)

# Define the executable and link against the libraries we need to build the
# source.
add_executable(mlp_forward ${mlp_forward_source})
target_link_libraries(mlp_forward ${Boost_LIBRARIES}
                                  ${ARMADILLO_LIBRARIES}
                                  ${MLPACK_LIBRARY})
