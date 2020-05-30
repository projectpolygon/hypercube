#pragma once

#include <thread>
#include <mutex>

#include <fmt/printf.h>
#include <stb_image.h>
#include <stb_image_write.h>

#include <vector>
#include <cstdlib>

#include <stdio.h>
#include <stdlib.h>
#include <ctime>
#include <cmath>
#include <iostream>

#include <atlas/math/math.hpp>
#include <atlas/math/ray.hpp>
#include <atlas/math/solvers.hpp>
#include <atlas/utils/load_obj_file.hpp>

using namespace atlas;
using Colour = math::Vector;


void saveToBMP(std::string const& filename,
               std::size_t start_width,
               std::size_t end_width,
               std::size_t start_height,
               std::size_t end_height,
               std::vector<Colour> const& image);

Colour random_colour_generate()
{
  unsigned int granularity = 256;
  Colour colour;
  colour.x = (rand() % granularity)
             / (float)granularity;
  colour.y = (rand() % granularity)
             / (float)granularity;
  colour.z = (rand() % granularity)
             / (float)granularity;
  return colour;
}