cmake_minimum_required(VERSION 3.21)

project(cdproc_cpp
  VERSION 0.1.0
  LANGUAGES CXX)

# C++ setup
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Python & pybind11
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

find_package(pybind11 CONFIG REQUIRED)

# FFmpeg
find_package(FFMPEG QUIET)

if(NOT FFMPEG_FOUND)
  if(DEFINED FFMPEG_INCLUDE_DIRS OR DEFINED FFMPEG_INCLUDE_DIR OR DEFINED FFMPEG_LIBRARIES)
    set(FFMPEG_FOUND ON)
  else()
    message(FATAL_ERROR
      "FFmpeg not found.\n\n"
      "Tips:\n"
      "  • vcpkg:  vcpkg install ffmpeg:x64-windows\n"
      "  • Then configure with the vcpkg toolchain:\n"
      "      -DCMAKE_TOOLCHAIN_FILE=$ENV{LOCALAPPDATA}/vcpkg/scripts/buildsystems/vcpkg.cmake\n"
      "  • Or pass explicit hints:\n"
      "      -DFFMPEG_INCLUDE_DIRS=C:/path/include "
      "-DFFMPEG_LIBRARIES=\"C:/path/lib/avcodec.lib;C:/path/lib/avformat.lib;C:/path/lib/avutil.lib;C:/path/lib/swscale.lib;C:/path/lib/swresample.lib\""
    )
  endif()
endif()

# Sources
set(CDPROC_CPP_SOURCES
  cpp/cdproc_py.cpp
  cpp/cdproc_mv.cpp
)

pybind11_add_module(cdproc_cpp ${CDPROC_CPP_SOURCES})

target_include_directories(cdproc_cpp PRIVATE
  ${PROJECT_SOURCE_DIR}/cpp/include
)

# Link FFmpeg
if(TARGET FFMPEG::avcodec)
  target_include_directories(cdproc_cpp PRIVATE ${FFMPEG_INCLUDE_DIRS})
  target_link_libraries(cdproc_cpp PRIVATE
    FFMPEG::avcodec
    FFMPEG::avformat
    FFMPEG::avutil
    FFMPEG::swscale
    FFMPEG::swresample
  )
elseif(DEFINED FFMPEG_LIBRARIES)
  if(DEFINED FFMPEG_INCLUDE_DIRS)
    target_include_directories(cdproc_cpp PRIVATE ${FFMPEG_INCLUDE_DIRS})
  elseif(DEFINED FFMPEG_INCLUDE_DIR)
    target_include_directories(cdproc_cpp PRIVATE ${FFMPEG_INCLUDE_DIR})
  endif()
  target_link_libraries(cdproc_cpp PRIVATE ${FFMPEG_LIBRARIES})
else()
  message(FATAL_ERROR "FFmpeg was reported found, but neither imported targets nor FFMPEG_LIBRARIES are set.")
endif()

# MSVC niceties
if(MSVC)
  target_compile_definitions(cdproc_cpp PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
  target_compile_options(cdproc_cpp PRIVATE /bigobj /EHsc /Zc:__cplusplus /utf-8)
endif()

set_target_properties(cdproc_cpp PROPERTIES OUTPUT_NAME "cdproc_cpp")
